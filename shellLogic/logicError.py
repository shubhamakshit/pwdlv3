class commandNotFound(Exception):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        return f"Command '{self.command}' not found"