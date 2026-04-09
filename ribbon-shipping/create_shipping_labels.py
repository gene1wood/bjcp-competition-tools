import argparse
import os.path
import csv
import json
import easypost  # pip install easypost
import easypost.errors  # pip install easypost
import requests  # pip install requests
import shutil
import yaml      # pip install pyyaml

PLASTIC_ENVELOPE_WEIGHT = 0.6  # 0.6 - 0.8  includes 4" X 6" mailing label
TYVEK_ENVELOPE_WEIGHT = 0.6
PAPER_ENVELOPE_WEIGHT = 1.0
RIBBON_WEIGHT = 1.7  # 1.5 - 1.7
BOS_RIBBON_WEIGHT = 2.7

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
            if [winner['Table'], winner['Place']] in [x.split(',')[0:2] for x in lines]:
                if winner['Email Address'] not in winners:
                    winners[winner['Email Address']] = winner.copy()
                    winners[winner['Email Address']]['entries'] = []
                if [winner['Table'], winner['Place'], 'bos'] in [x.split(',') for x in lines]:
                    winners[winner['Email Address']]['entries'].append("%s,%s,bos" % (winner['Table'], winner['Place']))
                winners[winner['Email Address']]['entries'].append("%s,%s" % (winner['Table'], winner['Place']))
            else:
                print("Skipping winner for Table %s Place %s as the ribbon was already picked up" % (
                    winner['Table'], winner['Place']))
    else:
        print(f"The {entries_file.name} file has a mix of comma delimited tables/place lines and entry number lines")
        exit(1)

    print("%s Shipments to be sent" % len(winners))
    return winners


def get_labels(client, config, winners, prod, just_show_rates):
    result = {}
    total_cost = 0.0
    for email in winners:
        winner = winners[email]
        name = "%s %s" % (winner['First Name'], winner['Last Name'])
        filename = 'shipping-labels/%s.png' % name
        if os.path.isfile(filename):
            print("File %s already exists, skipping" % filename)
            continue

        to_address = {
            'name': name,
            'country': winner['Country'],
            'email': winner['Email Address']
        }
        if winner['Address']:
            to_address['street1'] = winner['Address']
        if winner['City']:
            to_address['city'] = winner['City']
        if winner['State/Province']:
            to_address['state'] = winner['State/Province']
        if winner['Zip/Postal Code']:
            to_address['zip'] = winner['Zip/Postal Code']
        if winner['Zip/Postal Code']:
            to_address['zip'] = winner['Zip/Postal Code']
        if winner['Phone']:
            to_address['phone'] = winner['Phone']

        # name=name,
        # street1=winner['Address'],
        # city=winner['City'],
        # state=winner['State/Province'],
        # zip=winner['Zip/Postal Code'],
        # country=winner['Country'],
        # phone=winner['Phone'],
        # email=winner['Email Address']

        entries = [x for x in winner['entries'] if len(x.split(',')) == 2]
        bos_entries = [x for x in winner['entries'] if len(x.split(',')) == 3 and x.split(',')[2] == 'bos']
        weight = PLASTIC_ENVELOPE_WEIGHT + (RIBBON_WEIGHT * len(entries)) + (BOS_RIBBON_WEIGHT * len(bos_entries))

        parcel = {
            "length": 13,
            "width": 2,
            "height": 10,
            "weight": weight
        }

        shipment_args = {
            "to_address": to_address,
            "from_address": config['from_address'],
            "parcel": parcel
        }

        if to_address['country'] != 'US':
            customs_items = []
            for entry in entries:
                customs_items.append(client.customs_item.create(
                    description="Award ribbon",
                    quantity=1,
                    weight=RIBBON_WEIGHT,
                    value=10,
                    hs_tariff_number="6307.90.9989",  # http://www.faqs.org/rulings/rulings2001NYH84051.html
                    origin_country="US"
                ))
            for entry in bos_entries:
                customs_items.append(client.customs_item.create(
                    description="Award ribbon",
                    quantity=1,
                    weight=BOS_RIBBON_WEIGHT,
                    value=10,
                    hs_tariff_number="6307.90.9989",  # http://www.faqs.org/rulings/rulings2001NYH84051.html
                    origin_country="US"
                ))
            customs_info = client.customs_info.create(
                customs_items=customs_items,
                contents_type="merchandise",
                restriction_type="none",
                customs_certify=True,
                customs_signer=config['customs_signer'],
                eel_pfc="NOEEI 30.37(a)"  # https://docs.easypost.com/guides/customs-guide
            )
            shipment_args["customs_info"] = customs_info

        shipment = client.shipment.create(**shipment_args)

        # for rate in shipment.rates:
        #     print("%s (%s oz) : %s %s %s %s" % (email, weight, rate.carrier, rate.service, rate.rate, rate.id))

        try:
            rate = shipment.lowest_rate(
                carriers=['USPS', 'UPS'],
                services=['GroundAdvantage', 'FirstClassPackageInternationalService', 'UPSDAP UPSSaver'])
        except easypost.errors.general.filtering_error.FilteringError as e:
            print(e)
            print(shipment)
            raise e
        if just_show_rates:
            result[email] = {'name': name, 'price': rate.rate}
            total_cost += float(rate.rate)
            print('Rate : %s %s for entries using %s %s will cost %s to ship to %s' % (
                email, entries + bos_entries, rate.carrier, rate.service, rate.rate, '%s %s, %s' % (shipment.to_address['street1'], shipment.to_address['city'], shipment.to_address['state'])))
            # for r in shipment['rates']:
            #     print('%s %s %s' % (r['rate'], r['carrier'], r['service']))
        else:
            try:
                shipment_args = {
                    "id": shipment.id,
                    "rate": rate
                }
                bought_shipment = client.shipment.buy(**shipment_args)
            except Exception as e:
                print("Unable to purchase postage for %s at %s of weight %s : %s : %s : %s" % (name, to_address, weight, e, e.json_body, e.http_body))
                print("Shipment : %s" % shipment)
                print("Shipment arguments : %s" % shipment_args)
                raise
                continue

            print("Shipment purchased for %s" % name)

            response = requests.get(bought_shipment.postage_label.label_url, stream=True)
            response.raw.decode_content = True
            filename = 'shipping-labels/%s%s.png' % (
                name, '' if prod else '-test')
            print("Saving label %s" % filename)
            with open(filename, 'wb') as f:
                shutil.copyfileobj(response.raw, f)

            print('Tracking : %s %s %s for entries %s' % (
                name, email, bought_shipment.tracking_code, entries + bos_entries))

            result[email] = {
                'name': name,
                'tracking_code': bought_shipment.tracking_code
            }
    if just_show_rates:
        print(f"Total cost is {total_cost:.2f}")
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
        client = easypost.EasyPostClient(api_key=config['easypost_production_api_key'])
    else:
        client = easypost.EasyPostClient(api_key=config['easypost_test_api_key'])

    winners = get_winners(args.filename[0])

    labels = get_labels(client, config, winners, args.prod, args.just_show_rates)
    try:
        with open('labels.json', 'r') as f:
            output = json.load(f)
    except FileNotFoundError:
        print('Creating labels.json as none exists')
        output = {}
    if not args.prod:
        output['test'] = labels
    else:
        output.update(labels)
    with open('labels.json', 'w') as f:
        json.dump(output, f, indent=4)


if __name__ == "__main__":
    main()
