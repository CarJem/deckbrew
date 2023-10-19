import ansiwrap
from .OptionsColors import OptionColors


class OptionData:
    name: str
    type: str
    description: str
    default: any
    value: any
    notes: str



    def getStr(envVars: dict[str, str], key: str, default: str = ""):
        result = default
        value = envVars.get(key)
        if value:
            result  = value
        return result
    
    def getInt(envVars: dict[str, str], key: str, default: int = 0):
        result = default
        value = envVars.get(key)
        if value:
            try:
                result = int(value)
            except:
                pass

        return result
    
    def getBoolean(envVars: dict[str, str], key: str, default: bool = False):
        result = default
        value = envVars.get(key)
        if str(value):
            if value == "1" or value == "true" or value == True:
                result = True
            elif value == "0" or value == "false" or value == False:
                result = False

        return result

    def __init__(self, name: str, description: str, type: str, default, value=None, notes: str=None):
        self.name = name
        self.description = description
        self.default = default
        self.type = type
        self.value = value
        self.notes = notes

    def __str__(self) -> str:
        nameSection = OptionColors.VARIABLE_NAME(self.name)
        valueSection = OptionColors.VARIABLE_TYPE("({0})".format(self.type))
        defaultSection = OptionColors.VARIABLE_DEFAULT("(default: {0})".format(self.default))
        if self.notes == None:
            additionalNotes = "{0}".format(defaultSection)
        else:   
            additionalNotes = "{0} {1}".format(defaultSection, self.notes)

        max_width = 80

        descriptionSection = '\n'.join(ansiwrap.wrap(self.description, width=max_width))
        detailsSection = '\n'.join(ansiwrap.wrap(additionalNotes, width=max_width))



        return "{0}{1}:\n{2}\n{3}".format(nameSection, valueSection, descriptionSection, detailsSection)
