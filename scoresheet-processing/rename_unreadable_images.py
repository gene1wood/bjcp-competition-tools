"""
Iterate over all files in the current working directory that zxing failed to
read the QR code, display a thumbnail of the page, and prompt the user to
enter the entry number displayed in the thumbnail.

Rename the file to one containing the entered entry number.
"""
import os
from os import listdir
from os.path import isfile, join
from PIL import Image # pip install Pillow
import string

unreadable_files = [
    f for f in listdir("./") if isfile(join("./", f)) and "-none-" in f]
for file in sorted(unreadable_files):
    img = Image.open(file)
    img.thumbnail((2000, 2000))
    img.show()
    id = raw_input("What's the ID for %s > " % file)
    new_name = string.replace(file, "-none-", "-%s-" % id)
    if file != new_name:
        print("Renaming %s to %s" % (file, new_name))
        os.rename(file, new_name)

