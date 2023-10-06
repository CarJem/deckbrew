import os
import sys
import evdev
import subprocess
import threading
import psutil
from xdo import Xdo
import ewmh

import Xlib
import Xlib.display
from optparse import OptionParser, Values
from Xlib import display, Xatom, X
from Xlib.protocol import event
from Xlib.xobject import drawable
from Xlib.xobject.drawable import Window
from Xlib.protocol.request import GetGeometry, QueryTree

from .GamescopeInstance import *
from .GamescopeResolution import *
from .XlibInstance import *

steam_pid = None

class GamescopeTweaks:
    def isGameModeRunning(forceRun: bool = False):
        global steam_pid

        if forceRun:
            return True

        if not steam_pid or not psutil.pid_exists(steam_pid):
            process_name = "steam"
            for proc in psutil.process_iter():
                if process_name in proc.name():
                    steam_pid = proc.pid
                    break

        if psutil.pid_exists(steam_pid):
            steam_proc = Process(steam_pid)
            DESKTOP_SESSION = steam_proc.environ().get('DESKTOP_SESSION')
            return DESKTOP_SESSION == "gamescope-wayland"
        else:
            return False
        
    def runPatches(instance: GamescopeInstance):
        if instance.window_options.isDisabled:
            return
        
        if instance.global_options.useWhitelist and not instance.window_options.isWhitelisted:
            return
        
        if instance.window_options.dynamicResize_Enabled:
            GamescopeTweaks.dynamicResize(instance)

    def dynamicResize(instance: GamescopeInstance):

        options = instance.window_options

        if instance.window_width == 0 or instance.window_height == 0:
            if instance.debug: 
                print('No Window Width or Height')
            return

        display_width, display_height = instance.server.getDisplaySize()

        if display_width == 0 or display_height == 0:
            if instance.debug:
                print('No Display Width or Height')
            return

        desired_width = display_width
        desired_height = display_height

        gamescope_width, gamescope_height = GamescopeResolution.getSize(instance.display.displayEnv)

        account_maximum_size = (options.dynamicResize_IgnoreSizeLimits == False and options.dynamicResize_MaximumToScreenSize == False)
        
        if account_maximum_size:
            if instance.window_max_width != 0 or instance.window_max_height != 0:
                if instance.window_max_width != 0 and display_width > instance.window_max_width:
                    desired_width=instance.window_max_width
                if instance.window_max_height != 0 and display_height > instance.window_max_height:
                    desired_height=instance.window_max_height

        if instance.debug:
            print('Display size:', [display_width, display_height])
            print('Desired size:', [desired_width, desired_height])
            print('Gamescope size:', [gamescope_width, gamescope_height])
            print('Window size:', [instance.window_width, instance.window_height])
            print('---')

        size_mismatch = (not instance.window_height == desired_height or not instance.window_width == desired_width)

        if not size_mismatch:
            if instance.debug: print('No need to resize')
            #return
            
        if options.dynamicResize_ResizeWindow:
            instance.display.setWindowSize(instance.window_id, desired_width, desired_height)
        
        if options.dynamicResize_MaximumToScreenSize:
            try:
                win = instance.display.getWindow(instance.window_id)
                win.set_wm_normal_hints(flags = (Xlib.Xutil.PMaxSize), max_width=instance.window_width, max_height=instance.window_height)
                win.configure(max_width=instance.window_width, max_height=instance.window_height)
                instance.display.disp.sync()
                win.map()
            except Exception as e:
                print(e)
                pass

        if options.dynamicResize_GS_Filter >= 0:
            GamescopeResolution.changeFilter(str(instance.server.displayId), str(instance.display.displayId), options.dynamicResize_GS_Filter)

        if options.dynamicResize_GS_Scaler >= 0:
            GamescopeResolution.changeScaler(str(instance.server.displayId), str(instance.display.displayId), options.dynamicResize_GS_Scaler)

        if options.dynamicResize_GS_AdjustRes:
            GamescopeResolution.changeSize(desired_width, desired_height, str(instance.display.displayId), options.dynamicResize_GS_SuperRes, instance.server.displayEnv)
        else:
            GamescopeResolution.changeSize(0, 0, str(instance.display.displayId), False, instance.server.displayEnv)

            
        