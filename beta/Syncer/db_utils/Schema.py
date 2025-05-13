from beta.Syncer.db_utils.Errors import Errors
import uuid

class Schema:
    class InvalidSchema(Exception):
        def __init__(self, schema, key, value, type, required=False):
            self.schema = schema
            self.key = key
            self.value = value
            self.type = type
            self.required = required
            super().__init__(f"Invalid schema {schema}")

        def __str__(self):
            if self.required:
                return f"Invalid schema {self.schema} for key {self.key} with value {self.value} of type {type(self.type)} is required"
            return f"Invalid schema {self.schema} for key {self.key} with value {self.value} of type {type(self.value)} with expected type {self.type}"

    class InvalidIdFunction (Exception):
        def __init__(self, schema):
            self.schema = schema
            super().__init__(f"Invalid id function for schema {schema}")

        def __str__(self):
            return f"Invalid id function for schema {self.schema}"

    test_schema = {
        "key": {
            "type": str,
            "required": True
        }
    }

    def __init__(self, schema):
        self.schema = schema

    def has_id(self):
        return "_id" in self.schema

    def generate_id(self):
        return str(uuid.uuid4())

    def add_id(self):

        if not self.has_id():
            self.schema["_id"] = {
                "type": str,
                "required": True,
                "function": self.generate_id
            }
        if not "function" in self.schema["_id"]:
            self.schema["_id"]["function"] = self.generate_id

        if not callable(self.schema["_id"]["function"]):
            raise Schema.InvalidIdFunction(self.schema)





    def validate_schema(self, data):
        for key, value in self.schema.items():
            if key not in data:
                if not "required" in value or value["required"]:
                    raise Schema.InvalidSchema(self.schema, key, None, value["type"], True)
            else:
                if not isinstance(data[key], value["type"]):
                    raise Schema.InvalidSchema(self.schema, key, data[key], value["type"])
        return True

    def validate(self, key, value):
        if key not in self.schema:
            raise Errors.MissingKey(key, self.schema)
        if not isinstance(value, self.schema[key]["type"]):
            raise Errors.IllegalType(self.schema[key]["type"], key, value)
        return True


    def get_type(self, key):
        if key not in self.schema:
            raise Errors.MissingKey(key, self.schema)
        return self.schema[key]["type"]

    def is_required(self, key):
        if key not in self.schema:
            raise Errors.MissingKey(key, self.schema)
        return (not "required" in self.schema[key]) or (self.schema[key]["required"])

    def get_keys(self):
        return [key for key in self.schema]

    @staticmethod
    def gen_schema(data):
        schema = {}
        if data:
            for key, value in data.items():
                schema[key] = {
                    "type": type(value)
                }
        return schema