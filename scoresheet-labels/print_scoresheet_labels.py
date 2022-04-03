import labels  # pip install pylabels
import sys
import os.path
from reportlab.pdfbase.ttfonts import TTFont  # pip install reportlab
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.graphics import shapes
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib.units import mm
import csv
import string

import random
random.seed(48465)

base_path = os.path.dirname(__file__)


def write_name(label, width, height, data):
    """

    :param label:
    :param width:
    :param height:
    :param data: A dictionary containing fields like
        id, Entry Number
        brewStyle, Style
        brewCategory, Category
        brewSubCategory, Sub Category
        brewPaid, Paid
        brewReceived, Received
        brewBoxNum, Box Num
        brewTable Table
    :return:
    """

    table_number = data['Table'].split(':')[0].lstrip('0')

    qrw = QrCodeWidget(
        data['prefixed_id'],
        barLevel='H',
        barWidth=46*mm,
        barHeight=46*mm)

    label.add(qrw)

    offset = 40
    label.add(shapes.String(140,
                            height-offset,
                            "Entry: %s" % data['Entry Number'],
                            fontSize=20))
    offset += 18
    label.add(shapes.String(140,
                            height-offset,
                            "Table: %s" % table_number,
                            fontSize=16))
    offset += 16
    label.add(shapes.String(140,
                            height-offset,
                            "Category: %s%s" % (data['Category'], data['Sub Category']),
                            fontSize=16))
    offset += 14
    label.add(shapes.String(140,
                            height-offset,
                            data['Style'],
                            fontSize=10))

    offset += 12
    label.add(shapes.String(140,
                            height-offset,
                            "        Final",
                            fontSize=8))

    label.add(shapes.Rect(180,
                          height-(offset + 22),
                          60,
                          30,
                          fillColor=None,
                          strokeWidth=1))

    offset += 10
    label.add(shapes.String(140,
                            height-offset,
                            "Composite",
                            fontSize=8))

    offset += 10
    label.add(shapes.String(140,
                            height-offset,
                            "        Score",
                            fontSize=8))


def get_sheet():
    # Avery 5963 Labels
    # http://www.avery.com/avery/en_us/Products/Labels/Shipping-Labels/White-Shipping--Labels_05963.htm
    # http://www.worldlabel.com/Pages/wl-ol125.htm
    specs = labels.Specification(216, 279, 2, 5, 102, 51,
                                 corner_radius=2,
                                 left_padding=3,
                                 bottom_padding=2,
                                 row_gap=0)

    # Add some fonts.
    registerFont(TTFont('Judson Bold',
                        os.path.join(base_path, 'Judson-Bold.ttf')))
    registerFont(TTFont('KatamotzIkasi',
                        os.path.join(base_path, 'KatamotzIkasi.ttf')))

    # Create the sheet.
    return labels.Sheet(specs, write_name, border=False)

def add_prefix(row, prefix):
    row['Entry Number'] = string.zfill(row['Entry Number'], 4)
    row['prefixed_id'] = prefix + string.zfill(row['Entry Number'], 4)
    return row


def add_labels(sheet, reader, number=3, prefix='F', filter_function=None):
    """

    :param sheet: The labels.Sheet object in which to add the labels
    :param reader: A csv DictReader object that returns an array of dicts
        each containing fields like :
            id, Entry Number
            brewStyle, Style
            brewCategory, Category
            brewSubCategory, Sub Category
            brewPaid, Paid
            brewReceived, Received
            brewBoxNum, Box Num
            brewTable Table
    :param number: Number of labels to print for each given entry.
      1 judge would be 2 labels (1 judges + 1 cover sheet), 5 entries/sheet
      2 judges would be 3 labels (2 judges + 1 cover sheet), 3 entries/sheet
      3 judges would be 4 labels (3 judges + 1 cover sheet), 2 entries/sheet
    :param prefix: Entry id prefix
    :param filter_function: A function used to filter the entries
    :return:
    """

    if filter_function is None:
        filter_function = lambda x: True
    all_entries = list(reader)
    entries = list(filter(filter_function, all_entries))
    entries = [add_prefix(x, prefix) for x in entries]
    entries.sort(key=lambda x: int(x['Table'][:2]))

    if number == 2:
        # +---+---+
        # | A | A |
        # | B | B |
        # | C | C |
        # | D | D |
        # | E | E |
        # +---+---+
        sheet.add_labels(entries, count=2)
    elif number == 3:
        for i in range(1, len(entries)+1):
            if i % 3 == 0:  # Entry C
                # +---+---+
                # | A | B |
                # | A | B |
                # | A | B |
                # | C | C |
                # | C | - |
                # +---+---+
                sheet.partial_page(sheet.page_count + 1, ((5,2),))
                sheet.add_label(entries[i-3])
                sheet.add_label(entries[i-2])
                sheet.add_label(entries[i-3])
                sheet.add_label(entries[i-2])
                sheet.add_label(entries[i-3])
                sheet.add_label(entries[i-2])
                sheet.add_label(entries[i-1])
                sheet.add_label(entries[i-1])
                sheet.add_label(entries[i-1])
        print("number of entries %s" % len(entries))
        print("entries mod 3 = %s" % (len(entries) % 3))
        if len(entries) % 3 == 1:  # 1 entry left over
            # +---+---+
            # | A | A |
            # | A | - |
            # | - | - |
            # | - | - |
            # | - | - |
            # +---+---+
            sheet.add_label(entries[-1], count=3)
        elif len(entries) % 3 == 2:  # 2 entries left over
            # +---+---+
            # | A | B |
            # | A | B |
            # | A | B |
            # | - | - |
            # | - | - |
            # +---+---+
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
    elif number == 4:
        for i in range(1, len(entries) + 1):
            if i % 4 == 0:  # Entry D
                # +---+---+
                # | A | B |
                # | A | B |
                # | A | B |
                # | A | B |
                # | - | - |
                # +---+---+
                # +---+---+
                # | C | D |
                # | C | D |
                # | C | D |
                # | C | D |
                # | - | - |
                # +---+---+

                sheet.partial_page(sheet.page_count + 1, ((5, 1), (5, 2)))
                sheet.partial_page(sheet.page_count + 2, ((5, 1), (5, 2)))
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 3])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 3])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 3])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 3])

                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])


        print("number of entries %s" % len(entries))
        print("entries mod 5 = %s" % (len(entries) % 5))
        if len(entries) % 4 == 1:  # 1 entry left over
            # +---+---+
            # | A | A |
            # | A | A |
            # | - | - |
            # | - | - |
            # | - | - |
            # +---+---+
            sheet.add_label(entries[-1], count=4)
        elif len(entries) % 4 == 2:  # 2 entries left over
            # +---+---+
            # | A | B |
            # | A | B |
            # | A | B |
            # | A | B |
            # | - | - |
            # +---+---+
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
        elif len(entries) % 4 == 3:  # 3 entries left over
            # +---+---+
            # | A | B |
            # | A | B |
            # | A | B |
            # | A | B |
            # | - | - |
            # +---+---+
            # +---+---+
            # | C | - |
            # | C | - |
            # | C | - |
            # | C | - |
            # | - | - |
            # +---+---+
            sheet.partial_page(sheet.page_count + 1, ((5,1), (5,2)))
            sheet.partial_page(sheet.page_count + 2, ((1,2), (2,2), (3,2), (4,2)))
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-1])


    print([x['Entry Number'] for x in entries])


def main():
    if len(sys.argv) < 2:
        print('missing argument')
        return True
    sheet = get_sheet()
    with open(os.path.join(base_path, sys.argv[1])) as f:
        reader = csv.DictReader(f)

        # Offsites
        # 2 labels for each entry (2 judges, no scoresheets)
        # Tables 22 or 29
        # beers that are received and paid for
        # prelims prefix
        add_labels(
             sheet,
             reader,
             number=2,
             prefix='P',
             filter_function=lambda x: '{}{}'.format(x['Category'], x['Sub Category']) in ['20A', '20B', '27A8'] and int(x['Received']) == 1 and int(x['Paid']) in [1, 0])

        # Prelims
        # 2 labels for each entry (2 judges, no scoresheets)
        # All tables except 22 or 29 which were already printed
        # beers that are received and paid for
        # prelims prefix
        # add_labels(
        #      sheet,
        #      reader,
        #      number=2,
        #      prefix='P',
        #      filter_function=lambda x: x['Table'][:2] not in ['22', '29'] and int(x['Received']) == 1 and int(x['Paid']) == 1)


        # Add labels for all entries received and paid for
        # add_labels(sheet, reader, filter_function=lambda x: int(x['Received']) == 1 and int(x['Paid']) == 1)

        # Add 4 labels for each entry in the `finals` list
        # finals = ['004', '033', '212', '214']
        # add_labels(sheet, reader, number=4, filter_function=lambda x: x['Entry Number'].zfill(3) in finals)

        # Add 3 labels for each entry based on the custom Mini-BOS field
        # add_labels(
        #     sheet,
        #     reader,
        #     number=3,
        #     prefix='F',
        #     filter_function=lambda x: x['Mini-BOS'] == '1')

    sheet.save('scoresheet_entry_labels.pdf')
    print("{0:d} label(s) output on {1:d} page(s).".format(sheet.label_count,
                                                           sheet.page_count))


if __name__ == "__main__":
    main()
