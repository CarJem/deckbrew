#!/bin/sh
# Get the coordinates of the active window's
#    top-left corner, and the window's size.
#    This excludes the window decoration.

window_id=0x2000003
window_normal_hints=$(xprop -id $window_id -notype WM_NORMAL_HINTS 2>&1)


set $(echo $window_normal_hints | sed -n "s/^.*program specified minimum size:\s*\([0-9]\+\) by \([0-9]\+\).*$/\1\n\2/p")
min_width=$1
min_height=$2
echo "$min_width $min_height"

set $(echo $window_normal_hints | sed -n "s/^.*program specified maximum size:\s*\([0-9]\+\) by \([0-9]\+\).*$/\1\n\2/p")
max_width=$1
max_height=$2
echo "$max_width $max_height"