import os
import argparse
import time
from psutil import Process
from src.gamescope.resolution import *
from src.gamescope.tweaks import *
from src.classes.process_options import *
from src.classes.xlib import *
from src.classes.instance import *

last_calibrated_window=-1
last_external_display_state=False

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

def loop(debug=False, ignoreGS=False):
    global last_calibrated_window
    global last_external_display_state

    if isGamescope(ignoreGS):
        server = XlibInstance(":0")
        display = XlibInstance(":1")

        window_id, window_pid, window_appid = server.getActiveWindow()
        is_external_display = server.getExternalDisplayState()

        if window_id == -1: 
            return
        elif last_calibrated_window == window_id and last_external_display_state == is_external_display: 
            return
        else: 
            last_calibrated_window = window_id
            last_external_display_state = is_external_display
            time.sleep(1)
            

        instance = GamescopeInstance(server, display, window_id, window_pid, window_appid, is_external_display, debug)
        GamescopeTweaks.runPatches(instance)

def main(noloop, ignoreGS, debug):
    if noloop:
        loop(debug, ignoreGS)
    else:
        while True:
            loop(debug, ignoreGS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("gamescope_auto_maximize")
    parser.add_argument("-noloop", dest='noloop', action='store_true')
    parser.add_argument("-debug", dest='debug', action='store_true', default=False)
    parser.add_argument("-ignore_gamescope", dest='ignoreGS', action='store_true', default=False)
    args = parser.parse_args()

    ignoreGS = args.ignoreGS
    debug = args.debug
    noloop = args.noloop

    main(noloop, ignoreGS, debug)