from pymongo import MongoClient
from pymongo.server_api import ServerApi

from beta.Syncer.db_utils.DataObject import DbObject
from beta.Syncer.db_utils.Schema import Schema


class DB:


    def __init__(self,uri):
        import dns.resolver
        dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers=['8.8.8.8']
        self.uri = uri
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client["OPCluster"]
        self.collection = self.db["OPCluster"]

    def set_db(self,db):
        self.db = self.client[db]
        return self

    def set_collection(self,collection):
        self.collection = self.db[collection]
        return self

    def insert(self,db_obj:DbObject):
        return self.collection.insert_one(db_obj.compile())

    def find(self,query):
        return self.collection.find(query)

    def list_all(self):
        import json
        for i in self.collection.find():
            print(json.dumps(i, indent=4))

    def get_object(self,query):
        data = self.collection.find_one(query)

        if data:
            obj = DbObject(Schema.gen_schema(data))
            for key, value in data.items():
                obj.add((key, value))
        else:
            obj = DbObject(Schema.gen_schema(data), False)
        return obj

    def get_objects(self,query,limit:int = 0):
        data = self.collection.find(query).limit(limit)
        objs = []
        for i in data:
            obj = DbObject(Schema.gen_schema(i))
            for key, value in i.items():
                obj.add((key, value))
            objs.append(obj)
        return objs



    def delete(self,query):
        return self.collection.delete_one(query)

    def delete_many(self,query):
        return self.collection.delete_many(query)

    def update(self,query,update):
        return self.collection.update_one(query,update)

    def update_many(self,query,update):
        return self.collection.update_many(query,update)

    def ping(self):
        return self.client.server_info()


