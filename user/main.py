import os
import argparse
import time
import atexit
from psutil import Process
from src.ProcessOptions import *
from src.XlibInstance import *
from src.WindowTweaks import *
from src.core.DeckyEnviornment import *
from src.InputResolver import *
from src.core.ServiceFunctions import *

global_process_options=None

def loop(debug: bool, forceRun: bool, noLoop: bool):
    global global_process_options

    if not global_process_options:
        global_process_options = ProcessOptions_Global()

    DeckyEnviornment.init()
    ServiceFunctions.init()
    InputResolver.init()

    canLoop = True
    while canLoop:

        if ServiceFunctions.isActive(forceRun):
            WindowTweaks.loop(global_process_options, debug)
            InputResolver.loop(True)
        else:
            InputResolver.loop(False)

        if noLoop: canLoop = False

def onexit():
    InputResolver.close_devices()

def main():
    atexit.register(onexit)
    
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

    if helpMode: showhelp()
    else: loop(debug, force, noloop)

def showhelp():
    print()
    ProcessOptions_Global(readMode=OptionsReadMode.VIEWER).showOptions()
    print()
    ProcessOptions_App(readMode=OptionsReadMode.VIEWER).showOptions()
    print()

if __name__ == "__main__":
    main()