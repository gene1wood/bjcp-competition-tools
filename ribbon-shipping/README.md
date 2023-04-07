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
* Create the `winners.csv` file either
  * by going to the Admin panel of `BCOE&M`, going
    to `Data Exports` and in the `Participant Data (CSV)` section click `Winners`.
    If you're going by entry ids, ensure that your version of `BCOE&M` has the 
    patched `output_entries_export_winner.db.php` and `entries_export.php`
    files so that the entry id is included in the `winners.csv` file
  * or running the SQL query below against the database to produce the CSV
* Create either the `entry_ids_to_ship.txt` file or `table_place_to_ship.txt` file
  * If you create a `entry_ids_to_ship.txt` file it should list the entries you'd 
    like to create shipping labels for. This should be a file with one entry id 
    on each line. Note these are not 0 padded entry ids like `0123` but instead 
    just the number like `123`
  * If you create a `table_place_to_ship.txt` file, each line should contain a
    table number and a place number seperated by a comma. For example Table 21
    3rd place would be `21,3`
* Make a `shipping-labels/` directory where the label images will go
* Run `create_shipping_labels.py entry_ids_to_ship.txt` to do a test run
* Check everything and delete the test labels created
* Run `create_shipping_labels.py --prod entry_ids_to_ship.txt`
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
* Optionally afterward email the winners their tracking numbers. You can do this
  by running `create_tracking_emails.py`

# Gotchas

If your easypost account doesn't have enough money in it, this script will call
their API too quickly for them to charge your credit card and it will fail.
If this happens you can start it up again and it will skip the winners that
it's already created shipping labels for.
To work around this, manually add enough money to your account before starting
so that you don't run out

# SQL query to generate `winners.csv`

```sql
SELECT 'Entry ID', 'First Name', 'Last Name', 'Email Address', 'Address', 'City', 'State/Province', 'Zip/Postal Code', 'Country', 'Phone', 'Table' , 'Place'
UNION ALL
SELECT brewing.id as 'Entry ID', 
brewer.brewerFirstName as 'First Name', 
brewer.brewerLastName as 'Last Name', 
brewer.brewerEmail as 'Email Address', 
brewer.brewerAddress as 'Address', 
brewer.brewerCity as 'City', 
brewer.brewerState as 'State/Province', 
brewer.brewerZip as 'Zip/Postal Code', 
brewer.brewerCountry as 'Country', 
brewer.brewerPhone1 as 'Phone', 
judging_tables.tableNumber as 'Table' ,
judging_scores.scorePlace as 'Place'
FROM brewing, brewer, judging_tables, judging_scores
WHERE brewing.brewBrewerID = brewer.uid
AND judging_scores.scoreTable = judging_tables.id 
AND judging_scores.eid = brewing.id 
AND judging_scores.scorePlace IN (1,2,3)
INTO OUTFILE 'winners.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```