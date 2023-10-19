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

class XlibInstance:
    def __init__(self, displayNum: int):
        self.displayId = displayNum
        self.displayEnv = ":{0}".format(self.displayId)
        self.disp = Xlib.display.Display(self.displayEnv)
        self.root: Window = self.disp.screen().root
        self.last_seen = { 'xid': None }
        self.ewmh = ewmh.EWMH(self.disp, self.root)

        self.NET_WM_NAME = self.disp.intern_atom('_NET_WM_NAME')
        self.NET_WM_WINDOW_TYPE = self.disp.intern_atom('_NET_WM_WINDOW_TYPE')
        self.NET_WM_WINDOW_TYPE = self.disp.intern_atom('_NET_WM_WINDOW_TYPE')

    def query_propertyFirstItem(self, win, name, prop_type, format_size, empty=None):
        return self.query_property(win, name, prop_type, format_size, empty)[0]

    def query_property(self, win, name, prop_type, format_size, empty=None):
        if isinstance(win, int):
            # Create a Window object for the Window ID
            win = self.disp.create_resource_object('window', win)
        if isinstance(name, str):
            # Create/retrieve the X11 Atom for the property name
            name = self.disp.get_atom(name)

        result = win.get_full_property(name, prop_type)
        if result and result.format == format_size:
            return result.value
        return empty

    def setWindowSize(self, window_id, width: int, height: int):
        try:
            win = self.getWindow(window_id)
            win.configure(x=0, y=0, width=width, height=height)
            self.disp.sync()
        except Exception as e:
            print(e)
            pass
    
    def getActiveWindow(self, debug=False):

        window_id = -1
        process_id = -1
        app_id = -1

        try:
            win = self.getWindow(self.root.id)
            focusable_windows = self.query_property(win.id, "GAMESCOPE_FOCUSABLE_WINDOWS", Xlib.Xatom.CARDINAL, 32)
            focused_window = self.query_propertyFirstItem(win.id, "GAMESCOPE_FOCUSED_WINDOW", Xlib.Xatom.CARDINAL, 32)
            focused_app_gfx = self.query_propertyFirstItem(win.id, "GAMESCOPE_FOCUSED_APP_GFX", Xlib.Xatom.CARDINAL, 32)
            focused_app = self.query_propertyFirstItem(win.id, "GAMESCOPE_FOCUSED_APP", Xlib.Xatom.CARDINAL, 32)

            isNext = False
            for window in focusable_windows:
                if isNext:
                    process_id = window
                    break
                elif window == focused_app_gfx:
                    isNext = True

            window_id = focused_window
            app_id = focused_app_gfx
        except:
            process_id = -1
            window_id = -1
            app_id = -1
            
        if debug:
            print("Window Id: ", window_id)
            print("Process Id: ", process_id)
            print("App Id: ", app_id)

        return window_id, process_id, app_id

    def getExternalDisplayState(self):
        state = False
        try:
            win = self.getWindow(self.root.id)
            externalDisplayValue = self.query_propertyFirstItem(win.id, "GAMESCOPE_DISPLAY_IS_EXTERNAL", Xlib.Xatom.CARDINAL, 32)
            if externalDisplayValue == 1: state = True
        except:
            pass

        return state

    def getDisplaySize(self):
        try:
            geometry = self.root.get_geometry()
            return [ geometry.width, geometry.height ]
        except:
            return [ 0, 0 ]
    
    def getWindow(self, window_id):
        return self.ewmh._createWindow(window_id)

    def getWindowInfo(self, window_id):
        windowObject = self.getWindow(window_id)

        try: window_name = windowObject.get_full_property(self.NET_WM_NAME, 0).value
        except: window_name = None

        try: window_state = self.ewmh.getWmState(windowObject, True)
        except: window_state = None

        try: window_size = self.getWindowSize(window_id)
        except: window_size = None

        try: window_type = self.ewmh.getWmWindowType(windowObject, True)
        except: window_type = None

        return window_name, window_type, window_state, window_size  

    def getWindowSize(self, window_id):
        max_width = 0
        min_width = 0

        max_height = 0
        min_height = 0

        window_obj = self.getWindow(window_id)

        try:    
            window_normal_hints = window_obj.get_wm_normal_hints()
        except:
            window_normal_hints = None
    
        if window_normal_hints:
            max_width = window_normal_hints['max_width']
            min_width = window_normal_hints['min_width']
            max_height = window_normal_hints['max_height']
            min_height = window_normal_hints['min_height']

        width = 0
        height = 0

        try:
            geometry = window_obj.get_geometry()
            width = geometry.width
            height = geometry.height
        except:
            pass

        return width, height, max_width, min_width, max_height, min_height

        try:
            win = xhost.getWindow(window_id)
            win.set_wm_normal_hints(flags = (Xlib.Xutil.PMaxSize), max_width=width, max_height=height)
            win.configure(max_width=width, max_height=height)
            xhost.disp.sync()
            win.map()
        except Exception as e:
            print(e)
            pass