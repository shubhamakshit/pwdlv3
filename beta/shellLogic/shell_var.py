from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Window, Layout
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.processors import Processor, BeforeInput

from beta.shellLogic.Plugin import Plugin
from beta.shellLogic.handleLogics.HandleWEB import HandleWEB
from beta.shellLogic.handleLogics.HandleBatch import HandleBatch
from beta.shellLogic.logic import batch

# Initialize the plugin and add commands
plugin = HandleWEB()
batch_h = HandleBatch()

prompt = "|pwdl> "


def on_input_processed(buffer):
    if buffer.text.endswith("\n"):
        command = buffer.text.strip()
        if command:
            command = command.split()[0]
            args = command.split()[1:]
            if not args:
                args = []
            Plugin().parseAndRun(command, args)







input_buffer = Buffer(on_text_insert=on_input_processed)
control = BufferControl(buffer=input_buffer,input_processors=[BeforeInput(lambda: prompt)])



kb = KeyBindings()

@kb.add('c-q')
def exit_(event):
    event.app.exit()

app = Application(
    key_bindings=kb,
    layout=Layout(
        Window(
            content=control,
        )),
    full_screen=True
)

if __name__ == "__main__":
    app.run()