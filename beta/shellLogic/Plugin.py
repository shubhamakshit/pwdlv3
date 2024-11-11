import shutil
import re
from beta.shellLogic import simpleParser

class Plugin:
    """
    Base class for handling commands.
    Automatically registers commands added via `add_command`.
    """

    global_command_list = {}  # Global registry for all commands

    def __init__(self):
        self.commandList = {}
        self.register_commands()

    def register_commands(self):
        """
        Registers commands from the subclass into the global command list.
        """
        for name, info in self.commandList.items():
            Plugin.global_command_list[name] = {
                "desc": info["desc"],
                "regex": info["regex"],
                "func": info["func"]
            }

    def parseAndRun(self, command, args=[]):
        """
        Parses and executes the given command if found in the global list.
        """
        if command not in Plugin.global_command_list:
            print(f"Command '{command}' not found.")
            return
        simpleParser.parseAndRun(Plugin.global_command_list, command, args)

    def add_command(self, name, desc, regex, func):
        """
        Adds a new command to the local command list.
        """
        self.commandList[name] = {
            "desc": desc,
            "regex": regex,
            "func": func
        }

    def get_help(self, command=""):
        terminal_width = shutil.get_terminal_size().columns
        help_text = "Available commands:\n"
        separator = '-' * terminal_width + '\n'

        if command:
            if command not in Plugin.global_command_list:
                return f"Command '{command}' not found."
            return f"{command}: {Plugin.global_command_list[command]['desc']}"

        help_text += separator
        max_command_length = max(len(cmd) for cmd in Plugin.global_command_list) if Plugin.global_command_list else 0
        padding = max_command_length + 4

        for cmd, info in Plugin.global_command_list.items():
            help_text += f"{cmd.ljust(padding)}: {info['desc']}\n"

        help_text += separator
        return help_text

    def help(self, command=""):
        """
        Displays help text for a command or all commands.
        """
        print(self.get_help(command))

    def match_command(self, command):
        """
        Matches a command using regex patterns from the global command list.
        """
        for key, info in Plugin.global_command_list.items():
            if re.match(info["regex"], command):
                return key
        return None
