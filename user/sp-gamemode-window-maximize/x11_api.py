import os
import evdev
import subprocess
import threading
from xdo import Xdo
import ewmh

import Xlib
import Xlib.display
from Xlib.xobject.drawable import Window
from Xlib.protocol.request import GetGeometry


class X11:
    def __init__(self, displayEnv):
        self.displayEnv = displayEnv
        self.disp = Xlib.display.Display(displayEnv)
        self.root: Window = self.disp.screen().root
        self.last_seen = { 'xid': None } 
        self.xdotool = Xdo(displayEnv)
        self.ewmh = ewmh.EWMH(self.disp, self.root)

        self.NET_WM_NAME = self.disp.intern_atom('_NET_WM_NAME')
        self.NET_WM_WINDOW_TYPE = self.disp.intern_atom('_NET_WM_WINDOW_TYPE')

    def __atom_to_string(self, array):
        new_array = []
        for i in array:
            try:
                new_array.append(self.disp.get_atom_name(i))
            except:
                new_array.append(i)
        return new_array

    def windowHintFix(self, window_id, width: int, height: int):
        try:
            win = self.getWindow(window_id)
            win.set_wm_normal_hints(flags = (Xlib.Xutil.PMaxSize), max_width=width, max_height=height)
            win.configure(max_width=width, max_height=height)
            self.disp.sync()
            win.map()
        except Exception as e:
            print(e)
            pass
        
    def resizeWindow(self, window_id, width: int, height: int):
        try:
            win = self.getWindow(window_id)
            win.configure(x=0, y=0, width=width, height=height)
            self.disp.sync()
        except Exception as e:
            print(e)
            pass


    def getDisplaySize(self):
        try:
            geometry = self.root.get_geometry()
            return [ geometry.width, geometry.height ]
        except:
            return [ 0, 0 ]
        
    def getWindow(self, window_id):
        return self.ewmh._createWindow(window_id)

    def getWindowPID(self, window_id):
        try:
            window_pid = self.xdotool.get_pid_window(window_id)
        except:
            window_pid = None

        return window_pid

    def getWmState(self, window_id):
        try:
            windowObject = self.getWindow(window_id)
            window_state = self.ewmh.getWmState(windowObject, True)
        except Exception:
            window_state = None

        return window_state      

    def getWindowSizeData(self, window_id):
        max_width = 0
        min_width = 0

        max_height = 0
        min_height = 0

        normal_hints = self.getWindowNormalHints(window_id)
        if normal_hints:
            max_width = normal_hints['max_width']
            min_width = normal_hints['min_width']
            max_height = normal_hints['max_height']
            min_height = normal_hints['min_height']

        width = 0
        height = 0

        try:
            window_obj = self.getWindow(window_id)
            geometry = window_obj.get_geometry()
            width = geometry.width
            height = geometry.height
        except:
            pass

        return {
            "width": width,
            "height": height,
            "max_width": max_width,
            "min_width": min_width,
            "max_height": max_height,
            "min_height": min_height
        }

    def getWmType(self, window_id):
        try:
            window_obj = self.getWindow(window_id)
            window_type = self.ewmh.getWmWindowType(window_obj, True)
        except Xlib.error.XError:
            window_type = None

        return window_type

    def getWindowNormalHints(self, window_id):
        try:
            window_obj = self.disp.create_resource_object('window', window_id)
            window_normal_hints = window_obj.get_wm_normal_hints()
        except:
            window_normal_hints = None

        return window_normal_hints

    def getActiveWindow(self):
        window: Window = self.disp.get_input_focus().focus
        window_id = window.id
        return window_id

    def getWindowName(self, window_id):
        try:
            window_obj = self.getWindow(window_id)
            window_name = window_obj.get_full_property(self.NET_WM_NAME, 0).value
        except Xlib.error.XError:
            window_name = None

        return window_name
        