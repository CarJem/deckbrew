import os
import sys
import evdev
import subprocess
import threading
import psutil
#from xdo import Xdo
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
        
    def getDesiredSize(instance: GamescopeInstance, accountMinMax: bool):
        display_width, display_height = instance.server.getDisplaySize()
        desired_width = display_width
        desired_height = display_height

        if accountMinMax:
            print(instance.window_max_width)
            print(instance.window_max_height)
            if instance.window_max_width != 0:
                if instance.window_max_width != 0 and display_width > instance.window_max_width:
                    desired_width=instance.window_max_width
            if instance.window_max_height != 0:
                if instance.window_max_height != 0 and display_height > instance.window_max_height:
                    desired_height=instance.window_max_height

        print('Desired size:', [desired_width, desired_height])
        return [desired_width, desired_height]
    
    def validateSession(instance: GamescopeInstance):
        display_width, display_height = instance.server.getDisplaySize()
        if instance.window_width == 0 or instance.window_height == 0:
            if instance.debug: 
                print('No Window Width or Height')
            return False
       
        if display_width == 0 or display_height == 0:
            if instance.debug: print('No Display Width or Height')
            return False
        
        return True

    def applyMaxSizeOverride(instance: GamescopeInstance):
        try:
            win = instance.display.getWindow(instance.window_id)
            win.set_wm_normal_hints(flags = (Xlib.Xutil.PMaxSize), max_width=instance.window_width, max_height=instance.window_height)
            win.configure(max_width=instance.window_width, max_height=instance.window_height)
            instance.display.disp.sync()
            win.map()
        except Exception as e:
            print(e)
            pass
        
    def runPatches(ses: GamescopeInstance):

        if not GamescopeTweaks.validateSession(ses):
            return

        displayEnv = ses.display.displayEnv
        serverEnv = ses.server.displayEnv
        serverId = str(ses.server.displayId)
        displayId = str(ses.display.displayId)
        
        SPGM_WINTWEAKS_GAMESCOPE_FILTER_ENABLED = ses.window_options.SPGM_WINTWEAKS_GAMESCOPE_FILTER_ENABLED
        SPGM_WINTWEAKS_GAMESCOPE_FILTER_VALUE = ses.window_options.SPGM_WINTWEAKS_GAMESCOPE_FILTER_VALUE
        SPGM_WINTWEAKS_GAMESCOPE_SCALER_ENABLED = ses.window_options.SPGM_WINTWEAKS_GAMESCOPE_SCALER_ENABLED
        SPGM_WINTWEAKS_GAMESCOPE_SCALER_VALUE = ses.window_options.SPGM_WINTWEAKS_GAMESCOPE_SCALER_VALUE

        SPGM_WINTWEAKS_FIXED_WINDOW_SIZE_ENABLED = ses.window_options.SPGM_WINTWEAKS_FIXED_WINDOW_SIZE_ENABLED
        SPGM_WINTWEAKS_FIXED_WINDOW_WIDTH = ses.window_options.SPGM_WINTWEAKS_FIXED_WINDOW_WIDTH
        SPGM_WINTWEAKS_FIXED_WINDOW_HEIGHT = ses.window_options.SPGM_WINTWEAKS_FIXED_WINDOW_HEIGHT
        
        SPGM_WINTWEAKS_DYNAMICRESIZE_ENABLED = ses.window_options.SPGM_WINTWEAKS_DYNAMICRESIZE_ENABLED
        SPGM_WINTWEAKS_DYNAMICRESIZE_ADJUST_RES = ses.window_options.SPGM_WINTWEAKS_DYNAMICRESIZE_ADJUST_RES
        SPGM_WINTWEAKS_DYNAMICRESIZE_IGNORE_SIZE_LIMITS = ses.window_options.SPGM_WINTWEAKS_DYNAMICRESIZE_IGNORE_SIZE_LIMITS
        SPGM_WINTWEAKS_DYNAMICRESIZE_MAX_TO_SCREEN_SIZE = ses.window_options.SPGM_WINTWEAKS_DYNAMICRESIZE_MAX_TO_SCREEN_SIZE
        SPGM_WINTWEAKS_DYNAMICRESIZE_GS_ADJUST_RES = ses.window_options.SPGM_WINTWEAKS_DYNAMICRESIZE_GS_ADJUST_RES
        SPGM_WINTWEAKS_DYNAMICRESIZE_GS_SUPERRES = ses.window_options.SPGM_WINTWEAKS_DYNAMICRESIZE_GS_SUPERRES

        isMinMaxImportant = SPGM_WINTWEAKS_DYNAMICRESIZE_IGNORE_SIZE_LIMITS == False and SPGM_WINTWEAKS_DYNAMICRESIZE_MAX_TO_SCREEN_SIZE == False

        print('isMinMaxImportant:', isMinMaxImportant)

        display_width, display_height = ses.server.getDisplaySize()
        desired_width, desired_height = GamescopeTweaks.getDesiredSize(ses, isMinMaxImportant)
        gamescope_width, gamescope_height = GamescopeResolution.getSize(serverEnv)

        if ses.debug:
            print('Display size:', [display_width, display_height])
            print('Desired size:', [desired_width, desired_height])
            print('Gamescope size:', [gamescope_width, gamescope_height])
            print('Window size:', [ses.window_width, ses.window_height])
            print('---')

        if SPGM_WINTWEAKS_DYNAMICRESIZE_ENABLED == True:
            if SPGM_WINTWEAKS_DYNAMICRESIZE_ADJUST_RES == True:
                ses.display.setWindowSize(ses.window_id, desired_width, desired_height)
                
            if SPGM_WINTWEAKS_DYNAMICRESIZE_MAX_TO_SCREEN_SIZE == True:
                GamescopeTweaks.applyMaxSizeOverride(ses)

            if SPGM_WINTWEAKS_DYNAMICRESIZE_GS_ADJUST_RES == True:
                GamescopeResolution.changeSize(desired_width, desired_height, displayId, SPGM_WINTWEAKS_DYNAMICRESIZE_GS_SUPERRES, serverEnv)

        if SPGM_WINTWEAKS_FIXED_WINDOW_SIZE_ENABLED == True:
            window_width = SPGM_WINTWEAKS_FIXED_WINDOW_WIDTH if SPGM_WINTWEAKS_FIXED_WINDOW_WIDTH >= 0 else ses.window_min_width
            window_height = SPGM_WINTWEAKS_FIXED_WINDOW_HEIGHT if SPGM_WINTWEAKS_FIXED_WINDOW_HEIGHT >= 0 else ses.window_min_height
            ses.display.setWindowSize(ses.window_id, window_width, window_height)

        if SPGM_WINTWEAKS_GAMESCOPE_FILTER_ENABLED == True:
            GamescopeResolution.changeFilter(serverId, displayEnv, SPGM_WINTWEAKS_GAMESCOPE_FILTER_VALUE)

        if SPGM_WINTWEAKS_GAMESCOPE_SCALER_ENABLED == True:
            GamescopeResolution.changeScaler(serverId, displayEnv, SPGM_WINTWEAKS_GAMESCOPE_SCALER_VALUE)
            
        