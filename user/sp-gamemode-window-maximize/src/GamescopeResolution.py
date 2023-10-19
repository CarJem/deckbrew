import os
import sys
import evdev
import subprocess
import threading
import psutil
from xdo import Xdo
import ewmh

# Change path so we find Xlib
sys.path.append(os.path.join(os.path.dirname(__file__), 'third-party/python-xlib'))

GAMESCOPE_NEW_SCALING_FILTER = "GAMESCOPE_NEW_SCALING_FILTER"
GAMESCOPE_NEW_SCALING_SCALER = "GAMESCOPE_NEW_SCALING_SCALER"
GAMESCOPE_SCALING_FILTER = "GAMESCOPE_SCALING_FILTER"
GAMESCOPE_XWAYLAND_MODE_CONTROL = "GAMESCOPE_XWAYLAND_MODE_CONTROL"
GAMESCOPE_FSR_FEEDBACK = "GAMESCOPE_FSR_FEEDBACK"
GAMESCOPE_FORCE_WINDOWS_FULLSCREEN = "GAMESCOPE_FORCE_WINDOWS_FULLSCREEN"
WM_CHANGE_STATE = "WM_CHANGE_STATE"
GAMESCOPE_DISPLAY_MODE_NUDGE = "GAMESCOPE_DISPLAY_MODE_NUDGE"
GAMESCOPE_DISPLAY_FORCE_INTERNAL = "GAMESCOPE_DISPLAY_FORCE_INTERNAL"

import Xlib
import Xlib.display
from Xlib import display, Xatom, X
from Xlib.protocol import event
from Xlib.xobject import drawable

class GamescopeResolution:



    
    def __queryProp(disp, win, name, prop_type, format_size, empty=None):
        if isinstance(win, int):
            # Create a Window object for the Window ID
            win = disp.create_resource_object('window', win)
        if isinstance(name, str):
            # Create/retrieve the X11 Atom for the property name
            name = disp.get_atom(name)

        result = win.get_full_property(name, prop_type)
        if result and result.format == format_size:
            return result.value
        return empty

    def __sendProp(d: display.Display, win: drawable.Window, propName: str, value: any):
        prop = d.intern_atom(propName, only_if_exists=0)  
        event_ = event.PropertyNotify(
            window = win.id,
            display = d,
            atom = prop,
            time = 0,
            state = X.PropertyNewValue
        )

        win.send_event(event_)
        win.change_property(prop, Xatom.CARDINAL, 32, value)
        d.sync()

    def __delProp(d: display.Display, win: drawable.Window, propName: str):
        prop = d.intern_atom(propName, only_if_exists=0)  
        win.delete_property(prop)

    def __getProp(d: display.Display, win: drawable.Window, propName: str):
        result = GamescopeResolution.__queryProp(d, win, propName, Xatom.CARDINAL, 32)
        print(result)

    def getSize(_display="1", _server=":0"):
        try:
            server = display.Display(_server)
            win: drawable.Window = server.screen().root
            geometry = win.get_geometry()._data
            return geometry['width'], geometry['height']
        except Exception as e:
            return 0, 0


    def changeFilter(_display="1", _server=":0", mode=0):
        disp = display.Display(":" + _display)
        if mode == -1:
            GamescopeResolution.__delProp(disp, disp.screen().root, GAMESCOPE_NEW_SCALING_FILTER)
        else:
            GamescopeResolution.__sendProp(disp, disp.screen().root, GAMESCOPE_NEW_SCALING_FILTER, [mode])

    def changeScaler(_display="1", _server=":0", mode=0):
        disp = display.Display(":" + _display)
        if mode == -1:
            GamescopeResolution.__delProp(disp, disp.screen().root, GAMESCOPE_NEW_SCALING_SCALER)
        else:
            GamescopeResolution.__sendProp(disp, disp.screen().root, GAMESCOPE_NEW_SCALING_SCALER, [mode])

    def changeSize(_width="1280", _height="800", _display="1", _superRes=False, _server=":0"):
        width = int(_width)
        height = int(_height)
        displayID = int(_display)

        MAX_INT = 2**30 + (2**30-1)
        superRes = 1 if _superRes else 0

        if(height == 0 or width == 0):
            height = MAX_INT
            width = MAX_INT
            superRes = 0

        server = display.Display(_server)
        GamescopeResolution.__sendProp(server, server.screen().root, GAMESCOPE_XWAYLAND_MODE_CONTROL, [displayID, width, height, superRes])