import os
import argparse
import ansiwrap
from psutil import Process
from colorama import *
from colorama import Fore, Back, Style, Cursor

class OptionColors: 
    def VARIABLE_NAME(value: str):
        return Fore.BLUE + Style.BRIGHT + value + Style.RESET_ALL
    
    def VARIABLE_TYPE(value: str):
        return Fore.RED + Style.BRIGHT + value + Style.RESET_ALL
    
    def VARIABLE_DEFAULT(value: str):
        return Fore.RED + value + Style.RESET_ALL
    
    def SECTION_A(value: str):
        return Fore.GREEN + Style.BRIGHT + value + Style.RESET_ALL
    
    def SECTION_B(value: str):
        return Fore.GREEN + Style.DIM + Style.BRIGHT + value + Style.RESET_ALL
    
    def NOTE(value: str):
        return Fore.YELLOW + value + Style.RESET_ALL

class OptionData:
    name: str
    type: str
    description: str
    default: any
    value: any

    def getBoolean(envVars: dict[str, str], key: str, default: bool = False):
        result = default
        value = envVars.get(key)
        if value:
            if value == "1" or value == "true":
                result = True
        
        return result

    def __init__(self, name: str, description: str, type: str, default, value=None):
        self.name = name
        self.description = description
        self.default = default
        self.type = type
        self.value = value

    def __str__(self) -> str:
        nameSection = OptionColors.VARIABLE_NAME(self.name)
        valueSection = OptionColors.VARIABLE_TYPE("({0})".format(self.type))
        descriptionSection = self.description
        defaultSection = OptionColors.VARIABLE_DEFAULT("(default: {0})".format(self.default))
        
        prefixSection = "{0}{1}: ".format(nameSection, valueSection)
        descriptionSection = '\n'.join(ansiwrap.wrap(descriptionSection, width=100))
        
        return "{0}\n{1} {2}".format(prefixSection, descriptionSection, defaultSection)
    
class OptionText:
    def __init__(self, name: str = "", type: int = 0):
        self.name = name
        self.type = type

    def __str__(self) -> str:
        if self.type == 1:
            return OptionColors.SECTION_B(self.name + ":")
        else:
            return '\n'.join(ansiwrap.wrap(OptionColors.NOTE(self.name), width=120))
        
class OptionSection:
    def __init__(self, name: str = "", isEnding: bool = False):
        self.name = name
        self.isEnding = isEnding

    def __str__(self) -> str:
        return OptionColors.SECTION_A(self.name + ":")

class OptionViewer:
    vars_list = []
    
    def show(self):
        self.section_indent = 0

        
        def getIndentedText(i: str, isSection: bool = False):
            indent_string = ' ' * self.section_indent
            if not isSection: indent_string += "• "
        
            indent_space = ' ' * (ansiwrap.ansilen(indent_string))
            result = indent_string + i.replace('\n', '\n' + indent_space)
            return result

        def sectionPrint(i: OptionSection):
            if i.isEnding == False:
                print()
                print(getIndentedText(str(i), True))
                self.section_indent += 1
            else:
                self.section_indent -= 1

        def subSectionPrint(i: OptionSection):
            if i.type == 1:
                print()
            print(getIndentedText(str(i), True))
            if i.type == 0:
                print()

        def dataPrint(i: OptionData):
            print(getIndentedText(str(i)))
            print('')
        
        for i in self.vars_list:
            if type(i) == OptionData: dataPrint(i)
            elif type(i) == OptionSection: sectionPrint(i)
            elif type(i) == OptionText: subSectionPrint(i)
        print()

    def subitem(self, envVars: dict[str, str], name: str, type: int = 0):
        if envVars == {}: self.vars_list.append(OptionText(name=name, type=type))
                
    def section(self, envVars: dict[str, str], name: str):
        if envVars == {}: self.vars_list.append(OptionSection(name=name))

    def parent(self, envVars: dict[str, str]):
        if envVars == {}: self.vars_list.append(OptionSection(isEnding=True))

    def add(self, envVars: dict[str, str], name: str, itemType: type, description: str, default: any):
        value = None
        if itemType == "bool": value = OptionData.getBoolean(envVars, name, default)
        if envVars == {}: self.vars_list.append(OptionData(name, description, str(itemType), default, value))
        return value

    def __init__(self):
        pass
