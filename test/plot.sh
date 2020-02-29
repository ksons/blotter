#!/bin/bash
if [ -z "$1" ]
  then
    echo "No arguments supplied"
    exit 1
fi

[ -z "$BLENDERPATH" ] && echo "Need to set BLENDERPATH" && exit 1;

"$BLENDERPATH/blender"  --python "test/plot.py" `realpath $1` -- $*
