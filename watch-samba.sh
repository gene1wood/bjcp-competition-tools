#!/bin/bash

# This watches as scanned scoresheets are transferred over and alerts when
# they've all arrived and it's time to load more scoresheets to be scanned

path_to_check=/path/to/check

lines=0
while true; do
    oldlines="$lines"
    lines="`ls -1 ${path_to_check}/*.pdf | wc -l`"
    if [ "$oldlines" != "$lines" ]; then
        notify-send "XXXXXXXXXXXXXXXXXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXX Time for more scanning XXXXXXXXXXXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        echo "`date` Time for more scanning"
    fi
    sleep 3
done