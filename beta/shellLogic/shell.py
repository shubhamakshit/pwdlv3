from prompt_toolkit import PromptSession
from mainLogic.utils.glv import Global
from mainLogic.startup.checkup import CheckState
import json

from mainLogic.utils.glv_var import EXECUTABLES



from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.document import Document

class CustomCompleter(Completer):
    def __init__(self):
        self.file_completer = PathCompleter()

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        if text.startswith('cd '):
            for completion in self.file_completer.get_completions(document, complete_event):
                yield completion

def main(command_list=[]):
    # Initialize Prompt Toolkit session
    session = PromptSession()

    # Perform checkup and get preferences
    # Hardcoded verbose to False
    state = CheckState().checkup(EXECUTABLES, './', verbose=False)
    prefs = state['prefs']

    # Convert preferences to JSON string for display
    prefs_json = json.dumps(prefs, indent=4)

    # Add a custom completer
    custom_completer = CustomCompleter()

    from beta.shellLogic import logic

    if command_list:
        if len(command_list) == 1:
            command = command_list[0]
            args = []
        else:
            command = command_list[0]
            args = command_list[1:]

        logic.execute(command, args)


    # Command-line interface loop
    while True:
        try:
            user_input = session.prompt('|pwdl> ', completer=custom_completer)

            # just in case the user hits enter without typing anything
            if not user_input: continue

            command = user_input.split()[0]
            args = user_input.split()[1:]
            if not args: args = []

            # check if first arg is /? or -h or --help
            if args and args[0] in ['/?', '-h', '--help']:
                logic.execute_help(command)
            else:
                logic.execute(command, args)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()