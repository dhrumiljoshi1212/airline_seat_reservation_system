#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <command> <seat> <count>"
    exit 1
fi

COMMAND=$(echo "$1" | tr '[:lower:]' '[:upper:]')
SEAT=$(echo "$2" | tr '[:lower:]' '[:upper:]')
COUNT=$3

python3 main.py $COMMAND $SEAT $COUNT
