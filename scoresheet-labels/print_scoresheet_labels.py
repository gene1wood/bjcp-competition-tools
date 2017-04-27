import labels
import os.path
from reportlab.pdfbase.ttfonts import TTFont
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
    :param data: An 8-tuple containing
        entry_id,
        brewStyle,
        brewCategory,
        brewSubCategory,
        brewPaid,
        brewReceived,
        brewBoxNum,
        Table
    :return: 
    """
    (entry_id,
     brewStyle,
     brewCategory,
     brewSubCategory,
     brewPaid,
     brewReceived,
     brewBoxNum,
     Table) = data

    entry_id = string.zfill(entry_id, 4)
    qrw = QrCodeWidget(
        entry_id,
        barLevel='H',
        barWidth=46*mm,
        barHeight=46*mm)

    label.add(qrw)

    offset = 40
    label.add(shapes.String(140,
                            height-offset,
                            "Entry: %s" % entry_id,
                            fontSize=20))
    offset += 46
    label.add(shapes.String(140,
                            height-offset,
                            "Category: %s" % brewCategory,
                            fontSize=16))
    offset += 16
    label.add(shapes.String(140,
                            height-offset,
                            "Subcategory: %s" % brewSubCategory,
                            fontSize=16))
    offset += 16
    label.add(shapes.String(140,
                            height-offset,
                            brewStyle,
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


def add_labels(sheet, rows, number=3, entry_numbers=None):
    """
    
    :param sheet: The labels.Sheet object in which to add the labels
    :param rows: List of lists. Each list represents an entry. Each list has
        8 elements :
            entry_id,
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
    :param entry_numbers: List of strings of the entry numbers to print 
    :return: 
    """

    if entry_numbers is None:
        entries = rows
    else:
        entries = [x for x in rows if x[7][:2] in entry_numbers]

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
    print([x[0] for x in entries])


def main():
    sheet = get_sheet()
    with open(os.path.join(base_path, "entries.csv")) as f:
        reader = csv.reader(f)
        add_labels(sheet, reader)
        # finals = ['004', '033', '212']
        # add_labels(sheet, reader, 4, finals)
    sheet.save('scoresheet_entry_labels.pdf')
    print("{0:d} label(s) output on {1:d} page(s).".format(sheet.label_count,
                                                           sheet.page_count))

if __name__ == "__main__":
    main()
