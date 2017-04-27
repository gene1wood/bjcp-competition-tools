#!/bin/bash

# Required software
# pdfimages : https://en.wikipedia.org/wiki/Pdfimages
#   yum install poppler-utils
#   apt-get install poppler-utils
# zxing : https://github.com/zxing/zxing
#   Download and build with maven to produce a jar file
# imagemgaick : https://www.imagemagick.org/script/index.php
#   Install : https://www.imagemagick.org/script/download.php

# This tool assumes you're starting with a directory full of pdf files where
# each pdf contains an arbitrary number of pages and each page contains a
# single high resolution (600 dpi) scan of a scoresheet. It assumes that the
# directory name is descriptive of the stage of the competition that the
# scoresheets are from, for example /prelims_1 or /finals

# The tool iterates through the pdf files
#  extracts an image from each page of each pdf in the .ppm image format
#  iterates over each extracted .ppm image
#   scales the super-high resolution down to 1/10th the size
#   rotates it 90 degrees counter clockwise
#   passes the shrunken image to zxing to scan the QR code
#   passes the zxing text output through the parse_zxing_output.py tool
#   and extracts the entry id from the image
#   The tool then rotates the original image 90 degrees counter clockwise
#   converts it from .ppm to .png
#   and renames it to a filename containing both the directory name
#   and the extracted entry id in the format of
#   "dirname-0123-original_pdf_name-001.png" where
#    dirname=The directory name containing the pdfs, e.g. "finals"
#    0123=The entry number scanned from the QR code
#    original_pdf_name=The original filename of the pdf
#    001=The page number in the original pdf that the image came from


ZXING_JAR=/home/jdoe/workspace/zxing/zxing/javase/target/javase-3.3.1-SNAPSHOT-jar-with-dependencies.jar
PARSE_ZXING_OUTPUT=/home/jdoe/workspace/parse_zxing_output.py

for pdf in $1/*.pdf; do
    fullpath_pdf="`readlink -f $pdf`"
    pushd temp
    echo "extracting images from $pdf"
    pdfimages $fullpath_pdf `basename $fullpath_pdf .pdf`
    for image in *.ppm; do
        id="`convert $image -scale 10% -rotate -90 - | java -jar $ZXING_JAR /dev/stdin | python $PARSE_ZXING_OUTPUT`"
        echo "id ${id} extracted from image $image"
        final_image_name="$1-${id}-`basename $image .ppm`.png"
        echo "converting image $image to $final_image_name"
        convert $image -rotate -90 $final_image_name && rm -v $image
    done
    popd
done
