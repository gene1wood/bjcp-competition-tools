#!/bin/bash -e

# Required software
# optiping
# pngcrush
# pngquant

# This tool assumes you're starting with a directory full of pdf files where
# each pdf contains an arbitrary number of pages and each page contains a
# single full color high resolution (600 dpi) scan of a scoresheet.

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
#   and renames it to a filename containing the interpreted entry prefix
#   and the extracted entry id in the format of
#   "prefix-0123-original_pdf_name-001.png" where
#    prefix=The translated prefix e.g. P=prelims and F=finals
#    0123=The entry number scanned from the QR code
#    original_pdf_name=The original filename of the pdf
#    001=The page number in the original pdf that the image came from

ZXING_JAR=/home/jdoe/bjcp-competition-tools/scoresheet-processing/lib/zxing-zxing-3.4.0/javase/target/javase-3.4.0-jar-with-dependencies.jar
PARSE_ZXING_OUTPUT=/home/jdoe/bjcp-competition-tools/scoresheet-processing/parse_zxing_output.py

# Check for dependencies

if ! pdfimages -help 2>/dev/null; then
  cat <<EOF
pdfimages is missing
pdfimages : https://en.wikipedia.org/wiki/Pdfimages
yum install poppler-utils  # CentOS
apt-get install poppler-utils  # Ubuntu
EOF
  exit 1
fi
if ! convert -version >/dev/null; then
  cat <<EOF
imagemagick is missing
imagemagick : https://www.imagemagick.org/script/index.php
apt-get install imagemagick  # Ubuntu
Install : https://www.imagemagick.org/script/download.php
EOF
  exit 1
fi
if [ ! -e "$ZXING_JAR" ]; then
  cat <<EOF
zxing jar $ZXING_JAR is missing
zxing : https://github.com/zxing/zxing
  Download : https://github.com/zxing/zxing/releases
  Install maven : sudo apt-get install maven
    https://stackoverflow.com/q/15630055/168874
  Build with maven : cd zxing-zxing-*; mvn install -Dmaven.javadoc.skip=true
    https://github.com/zxing/zxing/wiki/Getting-Started-Developing#build
  Create single jar : cd javase && mvn -DskipTests -Dmaven.javadoc.skip=true package assembly:single
  Which you can find in zxing/zxing-zxing-3.4.1/javase/target/javase-3.4.1-jar-with-dependencies.jar
EOF
  exit 1
fi
if [ ! -e "$PARSE_ZXING_OUTPUT" ]; then
  echo "$PARSE_ZXING_OUTPUT is missing"
  exit 1
fi

mkdir -p images/source

pdf_image_format=ppm
if [ "$pdf_image_format" == "png" ]; then
    pdf_images_param="-png"
    extension=".png"
else
    pdf_images_param=""
    extension=".ppm"
fi

for pdf in *.pdf; do
    fullpath_pdf="`readlink -f $pdf`"
    pushd images/source
    echo "extracting images from $pdf"
    pdfimages $pdf_images_param "$fullpath_pdf" $(basename "$fullpath_pdf" .pdf)
    for image in *${extension}; do
        id="`convert $image -scale 10% - | java -jar $ZXING_JAR /dev/stdin | python $PARSE_ZXING_OUTPUT`"
        if [ "$id" == "none" ]; then
            # Try it rotated
            id="`convert $image -scale 10% -rotate -90 - | java -jar $ZXING_JAR /dev/stdin | python $PARSE_ZXING_OUTPUT`"
        fi
        echo -n "${id}"
        echo -n " (extracted from image $image)"
        final_image_name="${id}-`basename $image $extension`.png"
        convert $image -rotate -90 "../$final_image_name" && echo -n " (converted to $final_image_name)" && rm $image && echo " (deleted $image)"
     done
    popd
done
