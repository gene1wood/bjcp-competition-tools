"""
Take the zxing output in the formate described example below and echo to
stdout either the entry number scanned from the QR code or the string "none"

file:///dev/stdin (format: QR_CODE, type: TEXT):
Raw result:
0561
Parsed result:
0561
Found 3 result points.
  Point 0: (331.0,150.5)
  Point 1: (332.0,84.5)
  Point 2: (396.0,85.0)

"""

import sys
import re

raw_results = False
for l in sys.stdin.readlines():
    if re.search("No barcode found", l):
        print("none")
        exit()
    if raw_results:
        print(l.strip())
        exit()
    if l.strip() == "Raw result:":
        raw_results = True
print("undefined")

