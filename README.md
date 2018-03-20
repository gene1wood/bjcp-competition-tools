# Overview

These are a set of tools to enable creating QR code stickers to stick to BJCP
scoresheets and scanning those scoresheets and programatically determining
the entry id. The end goal is to enable digital delivery of completed
scoresheets to competition entrants and to avoid doing data entry from
scoresheets or physically distributing (in person or in snail mail) completed
scoresheets back to entrants.

# Before the competition

## Create `entries.csv`

To create a conforming file from [Brew Competition Online Entry & Management](http://www.brewcompetition.com/) go to the `Admin` page, then in the `Exporting` section, export `All Entries (All Data)`

## Create Scoresheet Labels

### `scoresheet-labels/print_scoresheetlables.py`

Given a `.csv` file called `entries.csv` containing 8 columns

    entry_id,
    brewStyle,
    brewCategory,
    brewSubCategory,
    brewPaid,
    brewReceived,
    brewBoxNum,
    Table

Produce a PDF to print onto Avery 5963 labels containing 2, 3 or 4 copies of
each entry's label

This produces labels which when stuck to scoresheets look like
`example-scanned-scoresheet.png`

# After the competition

## Scan the scoresheets

Run the scoresheets, each with an Avery 5963 sticker on it with a QR code
indicating the entry number, through an industrial copier/scanner. Break the
stack of scoresheets up into batches that fit in the feeder of the scanner.
Configure the scanner to scan in full color photograph mode at 600 DPI to
ensure entrants can read judges writing even if it's in light pencil.

This should produce a collection of pdf files, each with an arbitrary
number of pages of scoresheets in them.

Note : Make sure to give your judges blank pieces of paper and tell them to
not write on the backs of the scoresheets as anything on the backs of
scoresheets will be lost and will not get back to the entrant. Instead
if a judge runs out of room on the front, continue on a new blank piece of
paper and write the entry number at the top of the paper. These will then be
manually entered later when they fail to auto-detect since they have no
QR code sticker on them.

## Read the QR codes

### `scoresheet-processing/process_pdf_scans_of_scoresheets.sh`

Extract each page from each pdf, analyze it to read the QR code and produce
a `.png` image for each scoresheet with a filename containing the entry
number.

### `scoresheet-processing/parse_zxing_output.py`

A small tool used by `scoresheet-processing/process_pdf_scans_of_scoresheets.sh`
to parse the `zxing` output

## Manually enter unreadable QR codes

### `scoresheet-processing/rename_unreadable_images.py`

Iterate over all files in the current working directory that zxing failed to
analyze, display a thumbnail of the page, and prompt the user to
enter the entry number displayed in the thumbnail.

Rename the file to one containing the entered entry number.

## Combine scoresheets

### `scoresheet-processing/combine_scoresheet_images_into_pdf.sh`

Collect together all the prelims and finals scoresheet images into a single
pdf file for each entry