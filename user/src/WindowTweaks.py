import os
import sys
import evdev
import subprocess
import threading
import psutil
import time

import Xlib
import Xlib.display
from optparse import OptionParser, Values
from Xlib import display, Xatom, X
from Xlib.protocol import event
from Xlib.xobject import drawable
from Xlib.xobject.drawable import Window
from Xlib.protocol.request import GetGeometry, QueryTree

from .WindowTweaks import *
from .XlibInstance import *
from psutil import Process
from .core.DeckyEnviornment import *
from .ProcessOptions import *

steam_pid = None

last_calibrated_window=-1
last_external_display_state=False

class WindowTweaks:
    def __init__(self, server: XlibInstance, display: XlibInstance, window_id, window_pid, window_appid, global_options: ProcessOptions_Global, is_external_display: bool, debug=False) -> None:
        self.debug = debug
        self.global_options = global_options

        self.server = server
        self.display = display

        self.window_id = window_id
        self.window_pid = window_pid
        self.window_appid = window_appid

        self.is_external_display = is_external_display

        self.window_name, self.wm_state, self.wm_type, window_sizes = self.display.getWindowInfo(self.window_id)
        self.window_width, self.window_height, self.window_max_width, self.window_min_width, self.window_max_height, self.window_min_height = window_sizes

        try:
            if self.global_options.SPGM_WINTWEAKS_DECKY_MODE:
                envVars = DeckyEnviornment.getEnv(window_appid)
                options = ProcessOptions_App(envVars)
                self.window_options = options
            else:
                window_process = Process(pid=self.window_pid)
                envVars = window_process.environ()
                options = ProcessOptions_App(envVars)
                self.window_options = options
        except Exception as e:
            print("Issue:", e)
            self.window_options = ProcessOptions_App({})

        if self.debug:
            print('Window Info:')
            print('Name   |', self.window_name)
            print('Id     |', self.window_id)
            print('Pid    |', self.window_pid)
            print('AppID  |', self.window_appid)
            print('Sizes  |', window_sizes)
            print('Type   |', self.wm_type)
            print('State  |', self.wm_state)
            print('ExtDis |', self.is_external_display)
            print('---\n')

            print('Window Options:')
            print(self.window_options.toString())
            print('---\n')
            
            print('Global Options:')
            print(self.global_options.toString())
            print('---\n')

    def getDesiredSize(instance, accountMinMax: bool):
        display_width, display_height = instance.server.getDisplaySize()
        desired_width = display_width
        desired_height = display_height

        

        if accountMinMax:
            if instance.debug: 
                print("getDesiredSize && accountMinMax: ")
                print("window_max_width: ", instance.window_max_width)
                print("window_max_height: ", instance.window_max_height)

            if instance.window_max_width != 0:
                if instance.window_max_width != 0 and display_width > instance.window_max_width:
                    desired_width=instance.window_max_width
            if instance.window_max_height != 0:
                if instance.window_max_height != 0 and display_height > instance.window_max_height:
                    desired_height=instance.window_max_height

        if instance.debug:
            print('Desired size:', [desired_width, desired_height])

        return [desired_width, desired_height]
    
    def validateSession(instance):
        display_width, display_height = instance.server.getDisplaySize()
        if instance.window_width == 0 or instance.window_height == 0:
            if instance.debug: 
                print('No Window Width or Height')
            return False
       
        if display_width == 0 or display_height == 0:
            if instance.debug: 
                print('No Display Width or Height')
            return False
        
        return True
        
    def runPatches(ses):
        if not ses.validateSession():
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

        if ses.debug:
            print('isMinMaxImportant:', isMinMaxImportant)

        display_width, display_height = ses.server.getDisplaySize()
        desired_width, desired_height = ses.getDesiredSize(isMinMaxImportant)
        gamescope_width, gamescope_height = XlibInstance_GS.getSize(serverEnv)

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
                try:
                    win = ses.display.getWindow(ses.window_id)
                    win.set_wm_normal_hints(flags = (Xlib.Xutil.PMaxSize), max_width=ses.window_width, max_height=ses.window_height)
                    win.configure(max_width=ses.window_width, max_height=ses.window_height)
                    ses.display.disp.sync()
                    win.map()
                except Exception as e:
                    print(e)
                    pass

            if SPGM_WINTWEAKS_DYNAMICRESIZE_GS_ADJUST_RES == True:
                XlibInstance_GS.changeSize(desired_width, desired_height, displayId, SPGM_WINTWEAKS_DYNAMICRESIZE_GS_SUPERRES, serverEnv)

        if SPGM_WINTWEAKS_FIXED_WINDOW_SIZE_ENABLED == True:
            window_width = SPGM_WINTWEAKS_FIXED_WINDOW_WIDTH if SPGM_WINTWEAKS_FIXED_WINDOW_WIDTH >= 0 else ses.window_min_width
            window_height = SPGM_WINTWEAKS_FIXED_WINDOW_HEIGHT if SPGM_WINTWEAKS_FIXED_WINDOW_HEIGHT >= 0 else ses.window_min_height
            ses.display.setWindowSize(ses.window_id, window_width, window_height)

        if SPGM_WINTWEAKS_GAMESCOPE_FILTER_ENABLED == True:
            XlibInstance_GS.changeFilter(serverId, displayEnv, SPGM_WINTWEAKS_GAMESCOPE_FILTER_VALUE)

        if SPGM_WINTWEAKS_GAMESCOPE_SCALER_ENABLED == True:
            XlibInstance_GS.changeScaler(serverId, displayEnv, SPGM_WINTWEAKS_GAMESCOPE_SCALER_VALUE)       
        
    def loop(global_process_options: ProcessOptions_Global, debug: bool):
        global last_calibrated_window
        global last_external_display_state
        global last_window_appid

        server = XlibInstance(global_process_options.SPGM_WINTWEAKS_SERVER_ID)
        display = XlibInstance(global_process_options.SPGM_WINTWEAKS_DISPLAY_ID)

        window_id, window_pid, window_appid = server.getActiveWindow()
        is_external_display = server.getExternalDisplayState()
        has_decky_filechanged = DeckyEnviornment.hasUpdate()

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
            

        instance = WindowTweaks(server, display, window_id, window_pid, window_appid, global_process_options, is_external_display, debug)
        instance.runPatches()