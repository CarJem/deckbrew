import ansiwrap
from .OptionsColors import OptionColors


class OptionText:
    def __init__(self, name: str = "", type: int = 0):
        self.name = name
        self.type = type

    def __str__(self) -> str:
        text = ""

        if self.type == 1:
            text = OptionColors.SUBSECTION(self.name + ":")
        elif self.type == 2:
            text = self.name
        else:
            text = OptionColors.NOTE(self.name)
            
        output = '\n'.join(ansiwrap.wrap(text, width=80))
        
        #if self.type == 1:
        #    output = '\n' + output
        #elif self.type == 0:
        #    output += '\n'
        return output