#!/bin/bash

# Iterate over a list of entry numbers
#
# create a list of all images from prelims where the image filenames are in
# the format of "images/prelim-N-0123-whatever.png" where "N" is the round
# of prelims that the scoresheet is from and 0123 is the entry number
# create a list of all images from finals where the image filenames are in
# the format of "images/final-0123-whatever.png"
#
# Combine prelims images and finals images, in that order, into a pdf with
# a filename of the entry number, e.g. 0123.pdf

# Requires imagemagick be installed

for entry in `cat entrylistuniq.txt`; do
  prelim=
  final=

  prelim=( images/prelim-*-$entry-* )
  if compgen -G "images/final-$entry-*" >/dev/null; then
    final=( images/final-$entry-* )
  else
    final=( )
  fi
  echo convert ${prelim[@]} ${final[@]} pdfs/$entry.pdf
  convert ${prelim[@]} ${final[@]} pdfs/$entry.pdf
done