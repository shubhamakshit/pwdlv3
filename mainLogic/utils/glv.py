from colorama import Fore, Style, init
import mainLogic.utils.glv_var
import shutil

from mainLogic.utils import glv_var

# Initialize colorama
init()

class Global:

    # PREFERENCES_FILE is currently not used in mainLogic Project
    # only used in beta project
    import os
    disable_hr = False

    def __init__(self, vout=True, outDir="./"):
        self.outDir = outDir
        self.vout = vout

    @staticmethod
    def set_color(color, style=None):
        """Prints text in the specified color and style."""
        print(getattr(Fore, color), end="")
        if style:
            print(getattr(Style, style), end="")

    @staticmethod
    def reset():
        """Resets text color and style to defaults."""
        print(Style.RESET_ALL, end="")

    @staticmethod
    def print_colored(text, color, style=None):
        """Prints text in the specified color and style, resetting afterward."""
        Global.set_color(color, style)
        print(text)
        Global.reset()

    @staticmethod
    def dprint(text):
        """Prints debug text in yellow."""
        Global.print_colored(text, "YELLOW")

    @staticmethod
    def errprint(text):
        """Prints error text in red."""
        Global.print_colored(text, "RED")

    @staticmethod
    def setDebug():
        """Sets the text color to yellow (for debugging)."""
        Global.set_color("YELLOW")

    @staticmethod
    def setSuccess():
        """Sets the text color to green (for success messages)."""
        Global.set_color("GREEN")

    @staticmethod
    def sprint(text):
        """Prints success text in green."""
        Global.print_colored(text, "GREEN")

    @staticmethod
    def hr():

        # Disable horizontal rule if set
        if Global.disable_hr:
            return

        """Fills the entire terminal with = (one row only)."""
        columns, _ = shutil.get_terminal_size()
        print("-" * columns)