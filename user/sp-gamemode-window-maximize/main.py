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

def loop(debug=False, forceRun=False):
    global last_calibrated_window
    global last_external_display_state
    global last_window_appid

    if GamescopeTweaks.isGameModeRunning(forceRun):
        server = XlibInstance(0)
        display = XlibInstance(1)

        window_id, window_pid, window_appid = server.getActiveWindow()
        is_external_display = server.getExternalDisplayState()

        if window_id == -1: 
            return
        elif last_calibrated_window == window_id and last_external_display_state == is_external_display and last_window_appid == window_appid: 
            return
        else:
            last_calibrated_window = window_id
            last_external_display_state = is_external_display
            last_window_appid = window_appid
            

        instance = GamescopeInstance(server, display, window_id, window_pid, window_appid, is_external_display, debug)
        GamescopeTweaks.runPatches(instance)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("gamescope_auto_maximize")
    parser.add_argument("-noloop", dest='noloop', action='store_true')
    parser.add_argument("-debug", dest='debug', action='store_true', default=False)
    parser.add_argument("-force", dest='force', action='store_true', default=False)
    parser.add_argument("-options", dest='showEnvVariables', action='store_true', default=False)
    args = parser.parse_args()

    force = args.force
    debug = args.debug
    noloop = args.noloop
    showEnvVariables = args.showEnvVariables

    if showEnvVariables:
        ProcessOptions({}).showOptions()
    else:
        if noloop:
            loop(debug, force)
        else:
            while True:
                loop(debug, force)