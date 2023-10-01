#!/bin/sh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
while true
do
    /usr/bin/bash -c "$SCRIPT_DIR/process.sh"
done