import os.path
import sys
import csv
import string
import json
import easypost  # pip install easypost
import requests  # pip install requests
import shutil
import yaml      # pip install pyyaml


def check():
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.load(f)
        assert 'easypost_production_api_key' in config
        assert len(config['easypost_production_api_key']) > 0
        assert 'easypost_test_api_key' in config
        assert len(config['easypost_test_api_key']) > 0
        assert 'from_address' in config
        for field in ['name', 'company', 'street1', 'city', 'state', 'zip', 'phone']:
            assert field in config['from_address']
    except:
        print("Make sure that you've created a config.yaml with the correct contents")
        raise
    try:
        with open("winners.csv") as f:
            reader = csv.DictReader(f)
            for winner in reader:
                assert 'Entry ID' in winner
    except:
        print("Make sure winners.csv exists and is in the correct format")
        raise


def get_winners():
    with open("winners.csv") as f:
        reader = csv.DictReader(f)
        all_winners = list(reader)

    with open("entry_ids_to_ship.txt") as f:
        entry_ids = [line.rstrip('\n') for line in f if line[0] != '#']

    winners = {}
    for winner in all_winners:
        if winner['Entry ID'] in entry_ids:
            if winner['Email'] not in winners:
                winners[winner['Email']] = winner.copy()
                winners[winner['Email']]['entries'] = []
            entry_ids.remove(winner['Entry ID'])
            winners[winner['Email']]['entries'].append(winner['Entry ID'])
        else:
            print("Skipping entry %s as the ribbon was already picked up" % winner['Entry ID'])

    if len(entry_ids) > 0:
        raise Exception('The entry ids %s in entry_ids_to_ship.txt were missing from winners.csv' % entry_ids)

    print("%s Shipments to be sent" % len(winners))
    return winners


def get_labels(from_address, winners, prod):
    result = {}
    for email in winners:
        winner = winners[email]
        name = "%s %s" % (winner['First Name'], winner['Last Name'])
        filename = 'shipping-labels/%s.png' % name
        if os.path.isfile(filename):
            print("File %s already exists, skipping" % filename)
            continue

        fields = {
            'name': name,
            'country': winner['Country'],
            'email': winner['Email']
        }
        if winner['Address']:
            fields['street1'] = winner['Address']
        if winner['City']:
            fields['city'] = winner['City']
        if winner['State/Province']:
            fields['state'] = winner['State/Province']
        if winner['Zip/Postal Code']:
            fields['zip'] = winner['Zip/Postal Code']
        if winner['Zip/Postal Code']:
            fields['zip'] = winner['Zip/Postal Code']
        if winner['Phone']:
            fields['phone'] = winner['Phone']

        to_address = easypost.Address.create(**fields)
        # name=name,
        # street1=winner['Address'],
        # city=winner['City'],
        # state=winner['State/Province'],
        # zip=winner['Zip/Postal Code'],
        # country=winner['Country'],
        # phone=winner['Phone'],
        # email=winner['Email']



        tyvek_envelope_weight = 0.6
        paper_envelope_weight = 1.0
        ribbon_weight = 1.5
        weight = paper_envelope_weight + (ribbon_weight * len(winner['entries']))

        parcel = easypost.Parcel.create(
            length=13,
            width=2,
            height=10,
            weight=weight
        )

        shipment = easypost.Shipment.create(
            to_address=to_address,
            from_address=from_address,
            parcel=parcel
        )

        # for rate in shipment.rates:
        #     print("%s (%s oz) : %s %s %s %s" % (email, weight, rate.carrier, rate.service, rate.rate, rate.id))

        try:
            shipment.buy(
                rate=shipment.lowest_rate(
                    carriers=['USPS'],
                    services=['First']))
        except:
            print("Unable to purchase postage for %s at %s of weight %s" % (name, to_address, weight))
            continue

        print("Shipment purchased for %s" % name)

        response = requests.get(shipment.postage_label.label_url, stream=True)
        response.raw.decode_content = True
        filename = 'shipping-labels/%s%s.png' % (
            name, '' if prod else '-test')
        print("Saving label %s" % filename)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        print('Tracking : %s %s for entries %s' % (email, shipment.tracking_code, winner['entries']))

        result[email] = {
            'name': name,
            'tracking_code': shipment.tracking_code
        }
    return result


def main():
    check()
    with open("config.yaml", 'r') as f:
        config = yaml.load(f)
    prod = len(sys.argv) > 1 and sys.argv[1] == 'prod'
    if prod:
        easypost.api_key = config['easypost_production_api_key']
    else:
        easypost.api_key = config['easypost_test_api_key']

    winners = get_winners()

    from_address = easypost.Address.create(**config['from_address'])

    labels = get_labels(from_address, winners, prod)

    with open('labels.json', 'w') as f:
        json.dump(labels, f)


if __name__ == "__main__":
    main()
