#!/bin/bash
BASEDIR=$(dirname $0)
export PYTHONPATH="$BASEDIR/../pip/"

python3 -S "$BASEDIR/main.py"