import os
import argparse
from psutil import Process
from colorama import Fore, Back, Style



class OptionData:
    name: str
    type: str
    description: str
    default: any
    value: any

    def getBoolean(envVars: dict[str, str], key: str, default: bool = False):
        result = default
        if key in envVars:
            value = envVars[key]
            if value == "1" or value == "true":
                result = True
        
        return result

    def __init__(self, name: str, description: str, type: str, default, value=None):
        self.name = name
        self.description = description
        self.default = default
        self.type = type
        self.value = value

class ProcessOptions:

    vars_list = []

    def showOptions(self):
        print('Options:')
        for i in self.vars_list:
            print("- {4}{2}{5}({0}):{6}  {3} {5}(default: {1}){6}".format(i.type, i.default, i.name, i.description, Fore.BLUE + Style.BRIGHT, Fore.RED, Style.RESET_ALL))

    def create(self, envVars: dict[str, str], name: str, itemType: type, description: str, default: any):
        value = None

        if itemType == "bool":
            value = OptionData.getBoolean(envVars, name, default)

        if not envVars:
            optionData = OptionData(name, description, str(itemType), default, value)
            self.vars_list.append(optionData)
        return value


    def __init__(self, envVars: dict[str, str]):
        varPrefix = "SPGM_WINTWEAKS_"   
        self.isDisabled = self.create(envVars, varPrefix + "DISABLED", "bool", "Disable the tweak for any application containing this environment variable value", False)
        
        dynamicResPrefix = varPrefix + "DYNAMICRESIZE_"
        self.dynamicResize_MaximumToScreenSize = self.create(envVars, dynamicResPrefix + "MAX_TO_SCREEN_SIZE", "bool", " Forcefully Sets the Window's Maximum Size to the Screen Size (fix for LEGO Star Wars: TSS, etc.)", False)
        self.dynamicResize_IgnoreSizeLimits = self.create(envVars, dynamicResPrefix + "IGNORE_SIZE_LIMITS", "bool", "Ignore Maximum and Minimums when resizing windows", False)
        self.dynamicResize_AdjustRes = self.create(envVars, dynamicResPrefix + "ADJUST_RES", "bool", "Adjust gamescope resolution alongside of the actual window size", True)
        self.dynamicResize_ForceRes = self.create(envVars, dynamicResPrefix + "FORCE_RES", "bool", "Forcefully adjust the gamescope resolution even if it exceeds the gamescope output size", False)
        self.dynamicResize_Enabled = self.create(envVars, dynamicResPrefix + "ENABLED", "bool", "Enable automatic window resizing to fit available space", True)

