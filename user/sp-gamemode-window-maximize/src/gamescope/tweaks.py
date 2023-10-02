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

from ..classes.instance import *
from ..gamescope.resolution import *
from ..classes.xlib import *

class GamescopeTweaks:

    def runPatches(instance: GamescopeInstance):
        if instance.window_options.isDisabled:
            return
        
        if instance.window_options.dynamicResize_Enabled:
            GamescopeTweaks.dynamicResize(instance)

    def dynamicResize(instance: GamescopeInstance):
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

        account_maximum_size = (instance.window_options.dynamicResize_IgnoreSizeLimits == False and instance.window_options.dynamicResize_MaximumToScreenSize == False)
        
        if account_maximum_size:
            if instance.window_max_width != 0 or instance.window_max_height != 0:
                if instance.window_max_width != 0 and display_width > instance.window_max_width:
                    desired_width=instance.window_max_width
                if instance.window_max_height != 0 and display_height > instance.window_max_height:
                    desired_height=instance.window_max_height

        if instance.debug:
            print('Display size:', [display_width, display_height])
            print('Desired size:', [desired_width, desired_height])
            print('Window size:', [instance.window_width, instance.window_height])
            print('---')

        size_mismatch = (not instance.window_height == desired_height or not instance.window_width == desired_width)

        if not size_mismatch:
            if instance.debug: print('No need to resize')
            #return
            
        instance.display.setWindowSize(instance.window_id, desired_width, desired_height)
        
        if instance.window_options.dynamicResize_MaximumToScreenSize:
            try:
                win = instance.display.getWindow(instance.window_id)
                win.set_wm_normal_hints(flags = (Xlib.Xutil.PMaxSize), max_width=instance.window_width, max_height=instance.window_height)
                win.configure(max_width=instance.window_width, max_height=instance.window_height)
                instance.display.disp.sync()
                win.map()
            except Exception as e:
                print(e)
                pass

        if instance.window_options.dynamicResize_AdjustRes:
            GamescopeResolution.main(desired_width, desired_height, "1", instance.window_options.dynamicResize_ForceRes, ":0", instance.debug)
        