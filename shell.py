from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from utils.glv import Global
from startup.checkup import CheckState
import json
from utils.os2 import SysFunc

glv = Global()
EXECUTABLES = glv.EXECUTABLES
os2 = SysFunc()

# Initialize Prompt Toolkit session
session = PromptSession()

def main():
    # Perform checkup and get preferences
    # Hardcoded verbose to False
    state = CheckState().checkup(EXECUTABLES, False)
    prefs = state['prefs']

    # Convert preferences to JSON string for display
    prefs_json = json.dumps(prefs, indent=4)



    # Define available commands for auto-completion
    #commands = ['show_prefs', 'exit']
    #completer = WordCompleter(commands, ignore_case=True)

    from shellLogic import logic

    # Command-line interface loop
    while True:
        try:
            user_input = session.prompt('|pwdl> ',)

            for command in logic.commands:

                if user_input.startswith(command):
                    # Check if user input matches a command (with arguments)
                    if user_input == command:
                        logic.commands[command]['func']()
                        break
                    else:
                        # Check if user input matches a command (with arguments)
                        args = user_input.split(' ')[1:]
                        logic.commands[command]['func'](*args)
                        break

        except KeyboardInterrupt:
            continue
        except EOFError:
            break



if __name__ == "__main__":
    main()