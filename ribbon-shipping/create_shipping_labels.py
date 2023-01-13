import argparse
import os.path
import sys
import csv
import json
import easypost  # pip install easypost
import requests  # pip install requests
import shutil
import yaml      # pip install pyyaml


def check():
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
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
        with open("winners.csv", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for winner in reader:
                if config['filename'] == 'entry_ids_to_ship.txt':
                    assert 'Entry ID' in winner
                elif config['filename'] == 'table_place_to_ship.txt':
                    assert 'Table' in winner
                    assert 'Place' in winner
    except:
        print("Make sure winners.csv exists and is in the correct format")
        raise


def get_winners(entries_file):
    with open("winners.csv", encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_winners = list(reader)

    winners = {}
    lines = [line.rstrip('\n') for line in entries_file if line[0] != '#']
    if not any([',' in x for x in lines]):
        entry_ids = lines
        for winner in all_winners:
            if winner['Entry ID'] in entry_ids:
                if winner['Email Address'] not in winners:
                    winners[winner['Email Address']] = winner.copy()
                    winners[winner['Email Address']]['entries'] = []
                entry_ids.remove(winner['Entry ID'])
                winners[winner['Email Address']]['entries'].append(winner['Entry ID'])
            else:
                print("Skipping entry %s as the ribbon was already picked up" % winner['Entry ID'])

        if len(entry_ids) > 0:
            raise Exception('The entry ids %s in entry_ids_to_ship.txt were missing from winners.csv' % entry_ids)
    elif all([',' in x for x in lines]):
        for winner in all_winners:
            if [winner['Table'], winner['Place']] in [x.split(',') for x in lines]:
                if winner['Email Address'] not in winners:
                    winners[winner['Email Address']] = winner.copy()
                    winners[winner['Email Address']]['entries'] = []
                winners[winner['Email Address']]['entries'].append("%s,%s" % (winner['Table'], winner['Place']))
            else:
                print("Skipping winner for Table %s Place %s as the ribbon was already picked up" % (winner['Table'], winner['Place']))
    else:
        print(f"The {entries_file.name} file has a mix of comma delimited tables/place lines and entry number lines")
        exit(1)

    print("%s Shipments to be sent" % len(winners))
    return winners


def get_labels(from_address, winners, prod, just_show_rates):
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
            'email': winner['Email Address']
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
        # email=winner['Email Address']



        plastic_envelope_weight = 0.5
        tyvek_envelope_weight = 0.6
        paper_envelope_weight = 1.0
        ribbon_weight = 1.7
        weight = plastic_envelope_weight + (ribbon_weight * len(winner['entries']))

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

        rate = shipment.lowest_rate(
            carriers=['USPS'],
            services=['First'])

        if just_show_rates:
            result[email] = {'name': name, 'price': rate.rate}
            print('Rate : %s %s for entries %s' % (email, winner['entries'], rate.rate))
        else:
            try:
                shipment.buy(rate=rate)
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
        config = yaml.load(f, Loader=yaml.SafeLoader)
    parser = argparse.ArgumentParser(description='Generate shipping labels to ship ribbons')
    parser.add_argument('filename', type=argparse.FileType('r'), nargs=1,
                        help='Filename containing list of entries to generate shipping labels for')
    parser.add_argument('--prod', action='store_true',
                        help='produce real shipping labels and spend real money')
    parser.add_argument('--just-show-rates', action='store_true',
                        help="Don't buy postage just show the rates")
    args = parser.parse_args()
    if args.prod:
        easypost.api_key = config['easypost_production_api_key']
    else:
        easypost.api_key = config['easypost_test_api_key']

    winners = get_winners(args.filename[0])
    from_address = easypost.Address.create(**config['from_address'])

    labels = get_labels(from_address, winners, args.prod, args.just_show_rates)

    with open('labels.json', 'w') as f:
        json.dump(labels, f)


if __name__ == "__main__":
    main()
