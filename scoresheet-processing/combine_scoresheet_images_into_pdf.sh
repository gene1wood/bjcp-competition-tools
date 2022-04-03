#!/bin/bash

# Iterate over a list of entry numbers
#
# create a list of all images from prelims where the image filenames are in
# the format of "images/P0123-whatever.png" 0123 is the entry number
# create a list of all images from finals where the image filenames are in
# the format of "images/F0123-whatever.png"
#
# Combine prelims images and finals images, in that order, into a pdf with
# a filename of the prefix and entry number

# Requires imagemagick be installed
# Also requires increasing the memory limit in /etc/ImageMagick-6/policy.xml
# https://github.com/ImageMagick/ImageMagick/issues/396

prefix="My-Homebrew-Competition-Name-2018-Scoresheet-"
cover_page="cover_page.pdf"

mkdir -p pdfs

echo "Producing all pdfs for entries which had prelims or prelims and finals"
find images -maxdepth 1 -name 'P*.png' -printf '%P\n' | cut -c2-5 | sort | uniq | while read entry; do
  prelim=( images/P${entry}-* )
  if compgen -G "images/F${entry}-*" >/dev/null; then
    final=( images/F${entry}-* )
  else
    final=( )
  fi
  echo "Creating pdfs/${prefix}${entry}.pdf"
  if ! convert -compress JPEG -density 600 $cover_page ${prelim[@]} ${final[@]} pdfs/${prefix}${entry}.pdf; then
    exit
  fi
done

echo "Producing all pdfs for entries which had only finals"
find images -maxdepth 1 -name 'F*.png' -printf '%P\n' | cut -c2-5 | sort | uniq | while read entry; do
  if ! compgen -G "images/P${entry}-*" >/dev/null; then
      if compgen -G "images/F${entry}-*" >/dev/null; then
        final=( images/F${entry}-* )
      else
        final=( )
      fi
      echo "Creating entry with only finals pdfs/${prefix}${entry}.pdf"
      if ! convert -compress JPEG -density 600 $cover_page ${prelim[@]} ${final[@]} pdfs/${prefix}${entry}.pdf; then
        exit
      fi
  fi
done
