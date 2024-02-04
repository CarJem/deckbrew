#!/bin/sh
BASEDIR=$(dirname $0)
export PYTHONPATH="$BASEDIR/../pip/"

sleep 4

python3 -S "$BASEDIR/main.py"
