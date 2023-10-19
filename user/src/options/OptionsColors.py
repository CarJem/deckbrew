from colorama import Fore, Back, Style


class OptionColors:
    def VARIABLE_NAME(value: str):
        return Fore.RED + value + Style.RESET_ALL
    
    def VARIABLE_NAME_REF(value: str):
        return Fore.WHITE + Style.DIM + value + Style.RESET_ALL

    def VARIABLE_TYPE(value: str):
        return Fore.WHITE + value + Style.RESET_ALL

    def VARIABLE_DEFAULT(value: str):
        return Fore.BLUE + value + Style.RESET_ALL

    def SECTION(value: str):
        return Fore.GREEN + Style.BRIGHT + value + Style.RESET_ALL

    def SUBSECTION(value: str):
        return Fore.GREEN + value + Style.RESET_ALL

    def NOTE(value: str):
        return Fore.YELLOW + value + Style.RESET_ALL
    
    def ENUMS(prefix: str, value: str):
        return Fore.BLUE + Style.BRIGHT + prefix + Style.RESET_ALL + Fore.BLUE + value + Style.RESET_ALL