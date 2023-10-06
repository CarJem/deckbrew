import os
import argparse
from psutil import Process
from .XlibInstance import *
from .ProcessOptions import *

class GamescopeInstance:
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
            window_process = Process(pid=self.window_pid)
            envVars = window_process.environ()
            options = ProcessOptions_App(envVars)
            self.window_options = options
        except:
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