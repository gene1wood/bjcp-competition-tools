import labels  # pip install pylabels
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
        id,
        brewStyle,
        brewCategory,
        brewSubCategory,
        brewPaid,
        brewReceived,
        brewBoxNum,
        Table
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
                            "Entry: %s" % data['id'],
                            fontSize=20))
    offset += 46
    label.add(shapes.String(140,
                            height-offset,
                            "Table: %s" % table_number,
                            fontSize=16))
    offset += 16
    label.add(shapes.String(140,
                            height-offset,
                            "Category: %s%s" % (data['brewCategory'], data['brewSubCategory']),
                            fontSize=16))
    offset += 16
    label.add(shapes.String(140,
                            height-offset,
                            data['brewStyle'],
                            fontSize=10))


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
    row['id'] = string.zfill(row['id'], 4)
    row['prefixed_id'] = prefix + string.zfill(row['id'], 4)
    return row


def add_labels(sheet, reader, number=3, prefix='P', filter_function=None):
    """
    
    :param sheet: The labels.Sheet object in which to add the labels
    :param reader: A csv DictReader object that returns an array of dicts 
        each containing fields like :
            id,
            brewStyle,
            brewCategory,
            brewSubCategory,
            brewPaid,
            brewReceived,
            brewBoxNum,
            Table
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
            if i % 5 == 0:  # Entry E
                # +---+---+
                # | A | B |
                # | A | B |
                # | A | B |
                # | A | B |
                # | C | C |
                # +---+---+
                # +---+---+
                # | D | E |
                # | D | E |
                # | D | E |
                # | D | E |
                # | C | C |
                # +---+---+
                sheet.add_label(entries[i - 5])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 5])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 5])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 5])
                sheet.add_label(entries[i - 4])
                sheet.add_label(entries[i - 3])
                sheet.add_label(entries[i - 3])

                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 2])
                sheet.add_label(entries[i - 1])
                sheet.add_label(entries[i - 3])
                sheet.add_label(entries[i - 3])

        print("number of entries %s" % len(entries))
        print("entries mod 5 = %s" % (len(entries) % 5))
        if len(entries) % 5 == 1:  # 1 entry left over
            # +---+---+
            # | A | A |
            # | A | A |
            # | - | - |
            # | - | - |
            # | - | - |
            # +---+---+
            sheet.add_label(entries[-1], count=4)
        elif len(entries) % 5 == 2:  # 2 entries left over
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
        elif len(entries) % 5 == 3:  # 3 entries left over
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
        elif len(entries) % 5 == 4:  # 4 entries left over
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
            sheet.partial_page(sheet.page_count + 1, ((5,1), (5,2)))
            sheet.add_label(entries[-4])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-4])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-4])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-4])
            sheet.add_label(entries[-3])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])
            sheet.add_label(entries[-2])
            sheet.add_label(entries[-1])

    print([x['id'] for x in entries])


def main():
    sheet = get_sheet()
    with open(os.path.join(base_path, "entries.csv")) as f:
        reader = csv.DictReader(f)
        
        # Add labels for all entries received and paid for
        add_labels(sheet, reader, filter_function=lambda x: int(x['brewReceived']) == 1 and int(x['brewPaid']) == 1)

        # Add labels for all entries at table 02 or 09 and paid for
        # add_labels(sheet, reader, filter_function=lambda x: int(x['brewPaid']) == 1 and ('02:' in x['Table'] or '09:' in x['Table']))

        # Add 4 labels for each entry in the `finals` list
        # finals = ['004', '033', '212', '214']
        # add_labels(sheet, reader, number=4, filter_function=lambda x: x['id'].zfill(3) in finals)
    sheet.save('scoresheet_entry_labels.pdf')
    print("{0:d} label(s) output on {1:d} page(s).".format(sheet.label_count,
                                                           sheet.page_count))

if __name__ == "__main__":
    main()
