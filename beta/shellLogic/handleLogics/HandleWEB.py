from beta.shellLogic.Plugin import Plugin


class HandleWEB(Plugin):

    def __init__(self):
        super().__init__()
        self.add_command("web", "Open the web interface", "web", self.web)
        self.register_commands()


    def web(self, args):
        # Open the web interface
        print("Opening the web interface...")
