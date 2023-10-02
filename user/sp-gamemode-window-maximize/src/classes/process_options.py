import os
import argparse
from psutil import Process

class ProcessOptions:
    def getBoolean(self, envVars: dict[str, str], key: str, default: bool = False):
        result = default
        if key in envVars:
            value = envVars[key]
            if value == "1" or value == "true":
                result = True
        
        return result

    def __init__(self, envVars: dict[str, str]):
        varPrefix = "SPGM_WINTWEAKS_"   
        self.isDisabled = self.getBoolean(envVars, varPrefix + "DISABLED", False)
        
        dynamicResPrefix = varPrefix + "DYNAMICRESIZE_"
        self.dynamicResize_MaximumToScreenSize  = self.getBoolean(envVars, dynamicResPrefix + "MAX_TO_SCREEN_SIZE", False)
        self.dynamicResize_IgnoreSizeLimits     = self.getBoolean(envVars, dynamicResPrefix + "IGNORE_SIZE_LIMITS", False)
        self.dynamicResize_AdjustRes            = self.getBoolean(envVars, dynamicResPrefix + "ADJUST_RES", True)
        self.dynamicResize_ForceRes             = self.getBoolean(envVars, dynamicResPrefix + "FORCE_RES", False)
        self.dynamicResize_Enabled              = self.getBoolean(envVars, dynamicResPrefix + "ENABLED", True)

