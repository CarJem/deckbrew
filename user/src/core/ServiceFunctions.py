import os
import sys
import evdev
import subprocess
import threading
import psutil
import json
import configparser
import os

from .DeckyEnviornment import *

class ServiceFunctions:

    autologin_config = '/etc/sddm.conf.d/zz-steamos-autologin.conf'
    _cached_stamp = 0
    _last_state = False

    def init():
        pass

    def isActive(forceRun: bool):
        if forceRun:
            return True

        #region Check if it's okay to read the config file
        canReadConfig = False
        try:
            if os.path.exists(ServiceFunctions.autologin_config):
                stamp = os.stat(ServiceFunctions.autologin_config).st_mtime
                if stamp != ServiceFunctions._cached_stamp:
                   ServiceFunctions._cached_stamp = stamp
                   canReadConfig = True
        except Exception as e:
            print(e)
        #endregion
        
        #region If so, check if we are in gamescope-wayland
        if canReadConfig:
            print("Checking SDDM Autologin File...")
            config = configparser.ConfigParser()
            try:
                config.read(ServiceFunctions.autologin_config)
                sections = config.sections()
                if 'Autologin' in sections:
                    value = config['Autologin'].get('Session', 'FAIL')
                    if value == 'gamescope-wayland.desktop':
                        print("Gamemode Detected!")
                        ServiceFunctions._last_state = True
                    else:
                        print("Not in Gamemode: ", value)
                        ServiceFunctions._last_state = False
                else:
                    print("No Autologin section!")
                    ServiceFunctions._last_state = False    
            except:
                print("Bad Config File!")
                ServiceFunctions._last_state = False
        #endregion

        return ServiceFunctions._last_state