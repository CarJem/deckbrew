import os
import argparse
import time
from psutil import Process
from src.GamescopeResolution import *
from src.GamescopeTweaks import *
from src.ProcessOptions import *
from src.XlibInstance import *
from src.GamescopeInstance import *

last_calibrated_window=-1
last_external_display_state=False
global_process_options=None

def loop(debug: bool, forceRun: bool):
    global last_calibrated_window
    global last_external_display_state
    global last_window_appid
    global global_process_options


    if not global_process_options:
        global_process_options = ProcessOptions_Global()

    if GamescopeTweaks.isGameModeRunning(forceRun):
        server = XlibInstance(global_process_options.SPGM_WINTWEAKS_SERVER_ID)
        display = XlibInstance(global_process_options.SPGM_WINTWEAKS_DISPLAY_ID)

        window_id, window_pid, window_appid = server.getActiveWindow()
        is_external_display = server.getExternalDisplayState()
        has_decky_filechanged = DeckyEnviornment.hasFileUpdated()

        if has_decky_filechanged and window_id != -1:
            pass
        elif window_id == -1: 
            return
        elif last_calibrated_window == window_id and last_external_display_state == is_external_display and last_window_appid == window_appid: 
            return
        
        time.sleep(1)

        last_calibrated_window = window_id
        last_external_display_state = is_external_display
        last_window_appid = window_appid
            

        instance = GamescopeInstance(server, display, window_id, window_pid, window_appid, global_process_options, is_external_display, debug)
        GamescopeTweaks.runPatches(instance)

def showHelp():
    print()
    ProcessOptions_Global(readMode=OptionsReadMode.VIEWER).showOptions()
    print()
    ProcessOptions_App(readMode=OptionsReadMode.VIEWER).showOptions()
    print()

def main(debug: bool, forceRun: bool, noLoop: bool):
    canLoop = True
    DeckyEnviornment.hasFileUpdated()
    while canLoop:
        loop(debug, forceRun)
        if noLoop: canLoop = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser("gamescope_auto_maximize")
    parser.add_argument("-noloop", dest='noloop', action='store_true')
    parser.add_argument("-debug", dest='debug', action='store_true', default=False)
    parser.add_argument("-force", dest='force', action='store_true', default=False)
    parser.add_argument("-devMode", dest='devMode', action='store_true', default=False)
    parser.add_argument("-options", dest='showEnvVariables', action='store_true', default=False)
    args = parser.parse_args()

    force = args.force
    debug = args.debug
    noloop = args.noloop
    helpMode = args.showEnvVariables
    devMode = args.devMode

    if devMode:
        force = True
        debug = True
        noloop = True

    if helpMode: showHelp()
    else: main(debug, force, noloop)