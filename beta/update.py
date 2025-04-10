import json

from mainLogic.utils.glv_var import debugger


class UpdateJSONFile:
    def __init__(self, file_path, debug=False):
        self.file_path = file_path
        self.data = None
        self.load()

        if debug:
            debugger.info(f"Debug Mode: Loaded data from {file_path}")
            debugger.warning(f"Debug Mode: Data: {self.data}")

    def load(self):
        with open(self.file_path, 'r') as file:
            self.data = json.load(file)

    def save(self):
        with open(self.file_path, 'w+') as file:
            file.write(json.dumps(self.data, indent=4))

        # manually check if the file is saved correctly
        with open(self.file_path, 'r') as file:
            saved_data = json.load(file)
            if saved_data != self.data:
                debugger.error("Error: Data not saved correctly.")
            else:
                debugger.info("Data saved correctly.")

    def update(self, key, value, debug=False):

        if debug:
            print(f"Debug Mode: Updating {key} to {value}")

        self.data[key] = value
        self.save()
