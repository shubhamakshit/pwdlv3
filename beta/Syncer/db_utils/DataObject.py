from beta.Syncer.db_utils.Errors import Errors
from beta.Syncer.db_utils.Schema import Schema


class DbObject:

    class IllegalDBTuple(Exception):

        req_size = 2

        def __init__(self, data):
            self.data = data
            super().__init__(f"Data must be a tuple, got {type(data)}")

        def __str__(self):
            if len(self.data) != self.req_size:
                return f"Data must be a tuple of length 2, got {len(self.data)}"
            return f"Data must be a tuple, got {type(self.data)}"

    class AttrNotFound(Exception):

        def __init__(self, key):
            self.key = key
            super().__init__(f"Attribute {key} not found")

        def __str__(self):
            return f"Attribute {self.key} not found"

    class IncompleteData(Exception):

        def __init__(self, key):
            self.key = key
            super().__init__(f"Key {key} is required")

        def __str__(self):
            return f"Key {self.key} is required"






    def __init__(self, schema, add_id=True):
        self.schema = Schema(schema) if isinstance(schema, dict) else schema
        if add_id:
            self.schema.add_id()
            self._id = self.schema.schema["_id"]["function"]()

    def __str__(self):
        return str(self.compile())

    def add(self, data):
        if not isinstance(data, tuple):
            raise DbObject.IllegalDBTuple(data)

        key = data[0]
        value = data[1]

        if self.schema.validate(key, value):
            setattr(self, key, value)
            return self

    def does_exist(self, key):
        return hasattr(self, key)

    def update(self,data):
        if not isinstance(data, tuple):
            raise DbObject.IllegalDBTuple(data)

        key = data[0]
        value = data[1]

        if self.schema.validate(key, value):
            if not self.does_exist(key):
                raise DbObject.AttrNotFound(key)
            self.add(data)
            return self

    def compile(self):
        data = {}
        for key, value in self.schema.schema.items():
            if not self.does_exist(key):
                if self.schema.is_required(key):
                    raise DbObject.IncompleteData(key)
            else:
                data[key] = getattr(self, key)
        return data

    def del_key(self, key):
        if self.does_exist(key): delattr(self, key)

    def req_keys_more(self):
        return self.keys_more(req=True)

    def keys_more(self,req=False):
        inc = []
        for key in self.schema.get_keys():
            #print(f"Debug: does_exist({key}) = {self.does_exist(key)}")
            if  self.schema.is_required(key) and (req and not self.does_exist(key)):
                inc.append(key)
        return inc
