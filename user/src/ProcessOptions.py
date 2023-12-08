import os
import argparse
import json
from psutil import Process
from .options.OptionsColors import OptionColors
from .options.OptionsViewer import *
from .core.DeckyEnviornment import *

class ProcessOptions:

    jsonFile = None
    
    def showOptions(self):
        self.vw.show()

    def toString(self) -> str:
        var_list = vars(self)
        var_list.pop('vw')
        var_list.pop('key')
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

    def preload():
        if ProcessOptions.jsonFile:
            return ProcessOptions.jsonFile
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, '_variables.json')
            file = open(filepath)
            ProcessOptions.jsonFile = dict(json.load(file))
        except Exception as e:
            ProcessOptions.jsonFile = dict()

        return ProcessOptions.jsonFile

    def load(self):
        jsonFile = ProcessOptions_App.preload()
        try:
            if self.key in jsonFile:
                for entry in jsonFile[self.key]:
                    if 'type' in entry:
                        
                        if entry['type'] == "section": 
                            self.vw.section(entry['title'])

                        elif entry['type'] == "sectioninfo": 
                            self.vw.sectionInfo(entry['title'])

                        elif entry['type'] == "value": 
                            notes = None
                            desc = None
                            if 'desc' in entry:
                                desc = entry['desc']
                            if 'cmd_enumHints' in entry:
                                notes = OptionColors.ENUMS("Enums: ", entry['cmd_enumHints'])
                            value = self.vw.add(entry['id'], entry['xtype'], desc, entry['default'], notes)  
                            setattr(self, entry['id'], value)

                        elif entry['type'] == "subsection": 
                            self.vw.subSection(entry['title'])
        except Exception as e:
            raise e
    
    def __init__(self, readMode: OptionsReadMode = OptionsReadMode.NORMAL):
        self.vw = OptionViewer(readMode)
        self.key = "none"

class ProcessOptions_Global(ProcessOptions):
    def __init__(self, readMode: OptionsReadMode = OptionsReadMode.NORMAL):
        super().__init__(readMode)
        os_env = Process(os.getpid()).environ()
        self.key = "global"
        self.vw.setEnv(os_env)
        self.load()
        self.vw.parent()

class ProcessOptions_App(ProcessOptions):
    def __init__(self, envVars: dict[str, str] = {}, readMode: OptionsReadMode = OptionsReadMode.NORMAL):
        super().__init__(readMode)
        self.key = "user"
        self.vw.setEnv(envVars)
        self.load()
        self.vw.parent()
        


