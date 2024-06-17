import json


class UpdateJSONFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.load()

    def load(self):
        with open(self.file_path, 'r') as file:
            self.data = json.load(file)

    def save(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def update(self, key, value):
        self.data[key] = value
        self.save()
