class Errors:




    class IllegalType(Exception):

        def __init__(self,data_type,key,object={}):
            self.data_type = data_type
            self.key = key
            self.object = object
            super().__init__(f"Expected {data_type} for key {key} in object {object}")

    class MissingKey(Exception):

        def __init__(self,key,object={}):
            self.key = key
            self.object = object

        def __str__(self):
            return f"Missing key {self.key} in object {self.object}"