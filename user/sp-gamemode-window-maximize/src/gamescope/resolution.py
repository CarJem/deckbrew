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

atomName = "GAMESCOPE_XWAYLAND_MODE_CONTROL"

import Xlib
import Xlib.display
from Xlib import display, Xatom, X
from Xlib.protocol import event
from Xlib.xobject import drawable

class GamescopeResolution:
    def main(_width="1280", _height="800", _serverID="0", _force=False, _display=":1", debug=False):
        width = int(_width)
        height = int(_height)
        serverID = int(_serverID)

        MAX_INT = 2**30 + (2**30-1)
        superRes = 1 if _force else 0

        if(height == 0 or width == 0):
            height = MAX_INT
            width = MAX_INT
            superRes = 0

        d = display.Display(_display)

        atom = d.intern_atom(atomName, only_if_exists=1)
        if atom == X.NONE:
            sys.stderr.write('xwayland:  no atom named "%s" on server "%s"\n'%(atomName, d.get_display_name()))
            sys.exit(1)

        if debug:
            print(d.screen().root.id)

        sendModeChanged = GamescopeResolution.apply(GamescopeResolution.x11, d, GamescopeResolution._sendModeChanged, atom)
        changeMode = GamescopeResolution.apply(GamescopeResolution.x11, d, GamescopeResolution._changeMode, atom)

        changeMode(d.screen().root, width, height, serverID, superRes, debug)
        sendModeChanged(d.screen().root)

    def _sendModeChanged(disp : display.Display, atom : int, win : drawable.Window):
        event_ = event.PropertyNotify(
            window = win.id,
            display = disp,
            atom = atom,
            time = 0,
            state = X.PropertyNewValue
        )

        win.send_event(event_)
        disp.sync()

    def _changeMode(disp : display.Display, atom : int, win : drawable.Window, width : int, height : int, serverID = 1, superRes = 1, debug = False):
        if debug:
            print(f"changeMode({win.id})")
            win.change_property(atom, Xatom.CARDINAL, 32, [serverID, width, height, superRes])

    def x11(disp : display.Display, func, *args):
        ret = func(disp, *args)
        disp.flush()
        return ret

    def apply(f, *args1):
        def _apply(*args2):
            f(*args1, *args2)
        return _apply