import os
import argparse
from psutil import Process
from .options.OptionsColors import OptionColors
from .options.OptionsViewer import *


class ProcessOptions:
    def showOptions(self):
        self.vw.show()

    def toString(self) -> str:
        var_list = vars(self)
        var_list.pop('vw')
        output = ""

        maxLength = 0

        for i in var_list:
            length = len(i)
            if maxLength < length:
                maxLength = length

        for index, i in enumerate(var_list):
            output += i.ljust(maxLength) + " | "
            output += str(var_list[i])
            if len(var_list) - 1 > index: output += "\n"
        
        return output
    
    def __init__(self, readMode: OptionsReadMode = OptionsReadMode.NORMAL):
        self.vw = OptionViewer(readMode)

class ProcessOptions_Global(ProcessOptions):
    def __init__(self, readMode: OptionsReadMode = OptionsReadMode.NORMAL):
        super().__init__(readMode)
        os_env = Process(os.getpid()).environ()
        self.vw.setEnv(os_env)

        self.vw.section("Global Options")
        self.vw.sectionInfo("These options need to be applied before starting the service")
        
        self.useWhitelist =                     self.vw.add("SPGM_WINTWEAKS_ENABLE_WHITELIST", "bool", "Enable the tweak only for applications that specify the '{0}' enviornment variable".format(OptionColors.VARIABLE_NAME_REF("SPGM_WINTWEAKS_IS_WHITELISTED")), False)
        self.serverId =                         self.vw.add("SPGM_WINTWEAKS_SERVER_ID", "int", "The X Server containing the Embeded Gamescope Session", 0)
        self.displayId =                        self.vw.add("SPGM_WINTWEAKS_DISPLAY_ID", "int", "The XWayland Server of the Embeded Gamescope", 1)

        self.vw.parent()

class ProcessOptions_App(ProcessOptions):
    def __init__(self, envVars: dict[str, str] = {}, readMode: OptionsReadMode = OptionsReadMode.NORMAL):
        super().__init__(readMode)
        self.vw.setEnv(envVars)

        self.vw.section("Per Application Options")
        self.vw.sectionInfo("These options are applied to the applications themselves, usually through Steam launch arguments")

        self.isDisabled =                        self.vw.add("SPGM_WINTWEAKS_DISABLED", "bool", "Disable the tweak for any application containing this environment variable value", False)  
        self.isWhitelisted =                     self.vw.add("SPGM_WINTWEAKS_IS_WHITELISTED", "bool", "Enables the tweak when the '{0}' enviornment variable is used. See '{0}' for more info".format(OptionColors.VARIABLE_NAME_REF("SPGM_WINTWEAKS_ENABLE_WHITELIST")), False)

        self.vw.subSection("Dynamic Resize Options")
        self.dynamicResize_Enabled =             self.vw.add("SPGM_WINTWEAKS_DYNAMICRESIZE_ENABLED", "bool", "Enable dynamic resize settings", True)
        self.dynamicResize_ResizeWindow =        self.vw.add("SPGM_WINTWEAKS_DYNAMICRESIZE_ADJUST_RES", "bool", "Enable automatic window resizing to fit available space", True)
        self.dynamicResize_MaximumToScreenSize = self.vw.add("SPGM_WINTWEAKS_DYNAMICRESIZE_MAX_TO_SCREEN_SIZE", "bool", "Forcefully Sets the Window's Maximum Size to the Screen Size (fix for LEGO Star Wars: TSS, etc.)", False)
        self.dynamicResize_IgnoreSizeLimits =    self.vw.add("SPGM_WINTWEAKS_DYNAMICRESIZE_IGNORE_SIZE_LIMITS", "bool", "Ignore Maximum and Minimums when resizing windows", False)
        self.dynamicResize_GS_AdjustRes =        self.vw.add("SPGM_WINTWEAKS_DYNAMICRESIZE_GS_ADJUST_RES", "bool", "Adjust gamescope resolution alongside of the actual window size", True)        
        self.dynamicResize_GS_SuperRes =         self.vw.add("SPGM_WINTWEAKS_DYNAMICRESIZE_GS_SUPERRES", "bool", "Use gamescope super resolution", False)

        self.vw.subSection("Gamescope Options")
        self.dynamicResize_GS_Filter =           self.vw.add("SPGM_WINTWEAKS_GAMESCOPE_FILTER", "int", "Use a specific gamescope upscaling filter", -1, OptionColors.ENUMS("Enums: ", "OFF(-1), LINEAR(0), NEAREST(1), FSR(2), NIS(3)"))
        self.dynamicResize_GS_Scaler =           self.vw.add("SPGM_WINTWEAKS_GAMESCOPE_SCALER", "int", "Use a specific gamescope upscaling scaler", -1, OptionColors.ENUMS("Enums: ", "OFF(-1), AUTO(0), INTEGER(1), FIT(2), FILL(3), STRETCH(4)"))

        self.vw.parent()
        


