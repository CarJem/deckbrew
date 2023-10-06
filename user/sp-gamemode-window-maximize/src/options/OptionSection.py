from .OptionsColors import OptionColors


class OptionSection:
    def __init__(self, name: str = "", isEnding: bool = False):
        self.name = name
        self.isEnding = isEnding

    def __str__(self) -> str:
        result = ""
        #result += "\n"
        result += OptionColors.SECTION(self.name + ":")
        return result