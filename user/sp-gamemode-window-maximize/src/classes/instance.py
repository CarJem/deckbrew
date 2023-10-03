import os
import argparse
from psutil import Process
from .xlib import *
from .process_options import *

class GamescopeInstance:
    def __init__(self, server: XlibInstance, display: XlibInstance, window_id, window_pid, window_appid, is_external_display: bool, debug=False) -> None:
        self.debug = debug

        self.server = server
        self.display = display

        self.window_id = window_id
        self.window_pid = window_pid
        self.window_appid = window_appid

        self.is_external_display = is_external_display

        self.window_name, self.wm_state, self.wm_type, window_sizes = self.display.getWindowInfo(self.window_id)
        self.window_width, self.window_height, self.window_max_width, self.window_min_width, self.window_max_height, self.window_min_height = window_sizes

        try:
            window_process = Process(pid=self.window_pid)
            envVars = window_process.environ()
            options = ProcessOptions(envVars)
            self.window_options = options
        except:
            self.window_options = ProcessOptions({})

        if self.debug:
            print('window_name:', self.window_name)
            print('window_id:', self.window_id)
            print('window_pid:', self.window_pid)
            print('window_appid:', self.window_appid)
            print('window_data:', window_sizes)
            print('wm_type:', self.wm_type)
            print('wm_state:', self.wm_state)
            print('window_options:', vars(self.window_options))
            print('is_external_display:', self.is_external_display)
            print('---')