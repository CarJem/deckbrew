import os
import evdev
import subprocess
import threading
import x11_api
import argparse
import time
import sys
import gamescope_mode_change
from psutil import Process


class ProcessOptions:

    def __init__(self, envVars):
        self.disableTweak = False
        self.ignoreMinMax = False
        self.forceResize = False
        self.fixMaximumSize = False

        if "SPGM_WINMAX_IGNOREMAXMIN" in envVars:
            self.ignoreMinMax = True

        if "SPGM_WINMAX_FIXMAXIMUM" in envVars:
            self.fixMaximumSize = True

        if "SPGM_WINMAX_GLOBALIGNORE" in envVars:
            self.disableTweak = True

        if "SPGM_WINMAX_FORCE_GAMESCOPE_RESIZE" in envVars:
            self.forceResize = True


def isGamescope(ignoreGS=False):
    if ignoreGS:
        return True
    else:
        try:
            DESKTOP_SESSION = os.environ.get('DESKTOP_SESSION')
            if DESKTOP_SESSION == "gamescope-wayland":
                return True
            else:
                return False
        except:
            return False

def getProcessOptions(window_pid):
    try:
        window_process = Process(pid=window_pid)
        envVars = window_process.environ()
        options = ProcessOptions(envVars)
        return options
    except:
        return ProcessOptions({})


def loop(debug=False, ignoreGS=False):

    host_display=":0"
    server_display=":1"
    server_display_int=1

    if isGamescope(ignoreGS):
        deck_display_host = x11_api.X11(host_display)
        current_display = x11_api.X11(server_display)


        window_id = current_display.getActiveWindow()
        window_name = current_display.getWindowName(window_id)
        window_pid = current_display.getWindowPID(window_id)
        window_options = getProcessOptions(window_pid)
        window_data = current_display.getWindowSizeData(window_id)

        allowed_to_maximize = not window_options.disableTweak

        window_width = window_data['width']
        window_height = window_data['height']
        window_max_width = window_data['max_width']
        window_max_height = window_data['max_height']
        window_min_width = window_data['min_width']
        window_min_height = window_data['min_height']

        if debug:
            print('Window ID:', window_id)
            print('Window Name:', str(window_name))
            print('Window PID:', window_pid)
            print('Options:', vars(window_options))


        if window_width == 0 or window_height == 0:
            if debug:
                print('No Window Width or Height')
            return

        if allowed_to_maximize:
            display_width, display_height = deck_display_host.getDisplaySize()

            if display_width == 0 or display_height == 0:
                if debug:
                    print('No Display Width or Height')
                return

            desired_width = display_width
            desired_height = display_height
            

     
            if not window_options.ignoreMinMax and not window_options.fixMaximumSize:
                if window_max_width != 0 or window_max_height != 0:
                    if window_max_width != 0 and display_width > window_max_width:
                        desired_width=window_max_width
                    if window_max_height != 0 and display_height > window_max_height:
                        desired_height=window_max_height

            if debug:
                print('DisplaySize:', [display_width, display_height])
                print('DesiredSize:', [desired_width, desired_height])
                print('CurrentWindowSize:', [window_width, window_height])

            if not window_height == desired_height or not window_width == desired_width:
                current_display.resizeWindow(window_id, desired_width, desired_height)
                if window_options.fixMaximumSize:
                    current_display.fixMaximumSize(window_id, desired_width, desired_height)
                gamescope_mode_change.main(desired_width, desired_height, server_display_int, window_options.forceResize, host_display, debug)
            else:
                if debug:
                    print('No need to resize')

def main():
    parser = argparse.ArgumentParser("gamescope_auto_maximize")
    parser.add_argument("-noloop", dest='noloop', action='store_true')
    parser.add_argument("-debug", dest='debug', action='store_true', default=False)
    parser.add_argument("-ignore_gamescope", dest='ignoreGS', action='store_true', default=False)
    args = parser.parse_args()

    if args.noloop:
        loop(args.debug, args.ignoreGS)
    else:
        while True:
            loop(args.debug, args.ignoreGS)

if __name__ == "__main__":
    main()