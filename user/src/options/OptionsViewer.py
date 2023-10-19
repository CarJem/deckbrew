import os
import argparse
import ansiwrap
from psutil import Process
from colorama import *
from colorama import Cursor
from .OptionsData import OptionData
from .OptionSection import OptionSection
from .OptionText import OptionText
from .OptionsReadMode import OptionsReadMode

class OptionViewer:

    def __out_getIndent(self, i: str, isSection: bool = False):
        indent_string = ' '
        if not isSection: indent_string += "• "
    
        indent_space = ' ' * (ansiwrap.ansilen(indent_string))
        result = indent_string + i.replace('\n', '\n' + indent_space)
        return result

    def __out_printSection(self, i: OptionSection):
        if i.isEnding == False:
            print(self.__out_getIndent(str(i), True))

    def __out_printText(self, i: OptionText):
        print(self.__out_getIndent(str(i), i.type == 1 or i.type == 0))

    def __out_printData(self, i: OptionData):
        print(self.__out_getIndent(str(i)))

    def setEnv(self, envVars: dict[str, str]):
        self.envVars = envVars
      

    def show(self):
        for i in self.vars_list:
            if type(i) == OptionData: self.__out_printData(i)
            elif type(i) == OptionSection: self.__out_printSection(i)
            elif type(i) == OptionText: self.__out_printText(i)

    def subitem(self, name: str, type: int = 0):
        if self.readMode == OptionsReadMode.VIEWER: self.vars_list.append(OptionText(name=name, type=type))

    def sectionInfo(self, name: str):
        self.subitem(name, 0)

    def subSection(self, name: str):
        self.subitem(name, 1)

    def section(self, name: str):
        if self.readMode == OptionsReadMode.VIEWER: self.vars_list.append(OptionSection(name=name))

    def parent(self):
        if self.readMode == OptionsReadMode.VIEWER: self.vars_list.append(OptionSection(isEnding=True))

    def add(self, name: str, itemType: type, description: str, default: any, notes: str = None):
        value = None

        if itemType == "bool": value = OptionData.getBoolean(self.envVars, name, default)
        elif itemType == "int": value = OptionData.getInt(self.envVars, name, default)
        elif itemType == "str": value = OptionData.getStr(self.envVars, name, default)
        else: value = OptionData.getStr(self.envVars, name, default)

        if self.readMode == OptionsReadMode.VIEWER: 
            self.vars_list.append(OptionData(name, description, str(itemType), default, value, notes))
        return value


    def __init__(self, readMode: OptionsReadMode):
        self.readMode = readMode
        self.vars_list = []
