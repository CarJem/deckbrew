import os
import argparse
from psutil import Process
from .option_viewer import *
from colorama import Fore, Back, Style

vw = OptionViewer()

class ProcessOptions:

    def showOptions(self):
        vw.show()

    def __init__(self, envVars: dict[str, str]):
        try:
            if envVars != {}:
                os_env = Process(os.getpid()).environ() 
            else: os_env = {} 
        except:
            os_env = {}

        #region Cachced Descriptions/Names

        var_IsWhitelisted = "SPGM_WINTWEAKS_IS_WHITELISTED"
        var_EnableWhitelist = "SPGM_WINTWEAKS_ENABLE_WHITELIST"
        
        des_IsWhiteListed = "Enables the tweak when the '{0}' enviornment variable is used. See '{0}' for more info".format(OptionColors.VARIABLE_NAME(var_EnableWhitelist))
        des_EnableWhitelist = "Enable the tweak only for applications that specify the '{0}' enviornment variable".format(OptionColors.VARIABLE_NAME(var_IsWhitelisted))

        #endregion

        #region Definitions

        #region [] Global
        
        vw.section(os_env, "Global Options")
        vw.subitem(os_env, "These options need to be applied before starting the service")
        
        self.useWhitelist = vw.add(os_env, var_EnableWhitelist, "bool", des_EnableWhitelist, False)
        vw.parent(os_env)

        #endregion
        
        #region [] Per Application
              
        vw.section(envVars, "Per Application Options")
        vw.subitem(envVars, "These options are applied to the applications themselves, usually through Steam launch arguments")
        self.isDisabled = vw.add(envVars, "SPGM_WINTWEAKS_DISABLED", "bool", "Disable the tweak for any application containing this environment variable value", False)  
        self.isWhitelisted = vw.add(envVars, var_IsWhitelisted, "bool", des_IsWhiteListed, False)

        #region [][] Dynamic Resize

        vw.subitem(envVars, "Dynamic Resize Options", 1)
        self.dynamicResize_MaximumToScreenSize = vw.add(envVars, "SPGM_WINTWEAKS_DYNAMICRESIZE_MAX_TO_SCREEN_SIZE", "bool", "Forcefully Sets the Window's Maximum Size to the Screen Size (fix for LEGO Star Wars: TSS, etc.)", False)
        self.dynamicResize_IgnoreSizeLimits = vw.add(envVars, "SPGM_WINTWEAKS_DYNAMICRESIZE_IGNORE_SIZE_LIMITS", "bool", "Ignore Maximum and Minimums when resizing windows", False)
        self.dynamicResize_AdjustRes = vw.add(envVars, "SPGM_WINTWEAKS_DYNAMICRESIZE_ADJUST_RES", "bool", "Adjust gamescope resolution alongside of the actual window size", True)
        self.dynamicResize_ForceRes = vw.add(envVars, "SPGM_WINTWEAKS_DYNAMICRESIZE_FORCE_RES", "bool", "Forcefully adjust the gamescope resolution even if it exceeds the gamescope output size", False)
        self.dynamicResize_Enabled = vw.add(envVars, "SPGM_WINTWEAKS_DYNAMICRESIZE_ENABLED", "bool", "Enable automatic window resizing to fit available space", True)
        vw.parent(envVars)

        #endregion

        vw.parent(envVars)

        #endregion

        #endregion
        


