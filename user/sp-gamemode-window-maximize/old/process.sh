#!/bin/sh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while true
do
    IS_GAMESCOPE=false

    if [[ ! -z "${DESKTOP_SESSION}" && ${DESKTOP_SESSION} == "gamescope-wayland" ]]; then
        IS_GAMESCOPE=true
    fi

    if [[ $IS_GAMESCOPE  ]]; then

        ALLOWED_TO_MAXIMIZE=false

        window_id=$(xdotool getwindowfocus)
        window_name=$(xdotool getwindowname $window_id)
        window_type=$(xprop -id $window_id -notype _NET_WM_WINDOW_TYPE | sed 's/[^=]*=//' | cut -c2-)
        window_actions=$(xprop -id $window_id -notype _NET_WM_ALLOWED_ACTIONS)
        window_normal_hints=$(xprop -id $window_id -notype WM_NORMAL_HINTS)

        if [[ "$window_actions" == *"not found"* ]]; then
            ALLOWED_TO_MAXIMIZE=true
        fi

        if [[ $ALLOWED_TO_MAXIMIZE ]]; then
        
            MISMATCH_WIDTH=false
            MISMATCH_HEIGHT=false

            display_width=$(DISPLAY=:0 xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f1)
            display_height=$(DISPLAY=:0 xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f2)

            DESIRED_WIDTH=$display_width
            DESIRED_HEIGHT=$display_height

            set $(xwininfo -id $window_id |sed -n -e "s/^ \+Width: \([0-9]\+\).*/\1/p" -e "s/^ \+Height: \([0-9]\+\).*/\1/p")
            window_width=$1
            window_height=$2

            #if ! [[ "$window_normal_hints" == *"not found"* ]]; then
            #    set $(echo $window_normal_hints | sed -n "s/^.*program specified minimum size:\s*\([0-9]\+\) by \([0-9]\+\).*$/\1\n\2/p")
            #    min_width=$1
            #    min_height=$2
            #
            #    set $(echo $window_normal_hints | sed -n "s/^.*program specified maximum size:\s*\([0-9]\+\) by \([0-9]\+\).*$/\1\n\2/p")
            #    max_width=$1
            #    max_height=$2
            #
            #    if [ $display_width -gt $max_width ]; then
            #        DESIRED_WIDTH=$max_width
            #    fi
            #
            #    if [ $display_height -gt $max_height ]; then
            #        DESIRED_HEIGHT=$max_height
            #    fi
            #fi
            

            if ! [[ "$window_width" == "$DESIRED_WIDTH" ]]; then
                #echo "Width not identical"
                MISMATCH_WIDTH=true
            fi
            if ! [[ "$window_height" == "$DESIRED_HEIGHT" ]]; then
                #echo "Height not identical"
                MISMATCH_HEIGHT=true
            fi

            if [[ $MISMATCH_WIDTH == true || $MISMATCH_HEIGHT == true  ]]; then
                echo "Resizing Window: $window_id..."
                xdotool windowsize $window_id $DESIRED_WIDTH $DESIRED_HEIGHT
                sleep 3
                python "$SCRIPT_DIR/gamescope_mode_change.py" -i 1 -d :0 -x $DESIRED_WIDTH -y $DESIRED_HEIGHT
            fi
        fi
    fi
done
