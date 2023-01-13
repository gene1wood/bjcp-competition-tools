# How to use `create_shipping_lables.py`

* Sign up for an EasyPost account and setup a billing method
* Create a `config.yaml` file and
  * set the `easypost_production_api_key` variable in the config file with your
    EasyPost API key and the `easypost_test_api_key` with your test key. For
    example :

        easypost_production_api_key: abcdefghijklmnopqrstuv
        easypost_test_api_key: vutsrqponmlkjihgfedcba
  * set the `from_address` for example :

        from_address:
          name: John Doe
          company: Homebrew Club Name
          street1: 123 First Ave.
          city: Springfield
          state: NY
          zip: 12345
          phone: 212-555-5555
* Create the `winners.csv` file by going to the Admin panel of `BCOE&M`, going
  to `Data Exports` and in the `Participant Data (CSV)` section click `Winners`.
  If you're going by entry ids, ensure that your version of `BCOE&M` has the 
  patched `output_entries_export_winner.db.php` and `entries_export.php`
  files so that the entry id is included in the `winners.csv` file
* Create the `entry_ids_to_ship.txt` file that lists the entries you'd like to
  create shipping labels for. This should be a file with one entry id on each
  line. Note these are not 0 padded entry ids like `0123` but instead just the
  number like `123`
* Make a `shipping-labels/` directory where the label images will go
* Run `create_shipping_labels.py` to do a test run
* Check everything and delete the test labels created
* Run `create_shipping_labels.py prod`
* Record the resulting tracking numbers that are output. You'll want to save
  these to send to the entrants after you've shipped the ribbons so they can
  track their shipment.
* Combine the resulting images togeting into a single PDF to make it easier to
  print with the Imagemagick command
```
convert shipping-labels/*.png print-shippping-labels.pdf
```
* Print out the shipping labels and attach them to the envelopes. Add the
  ribbons and seal them. Drop them at the post office
* Optionally afterward email the winners their tracking numbers

# Gotchas

If your easypost account doesn't have enough money in it, this script will call
their API too quickly for them to charge your credit card and it will fail.
If this happens you can start it up again and it will skip the winners that
it's already created shipping labels for.
To work around this, manually add enough money to your account before starting
so that you don't run out
