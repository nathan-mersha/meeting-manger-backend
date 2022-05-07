from model.group import GroupModel
from datetime import datetime
import configparser
import pymongo


class GroupModelDAL:
    DATABASE_NAME = "arrangeDevDB"
    COLLECTION_NAME = "group"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[self.DATABASE_NAME]
        self.collection = db[self.COLLECTION_NAME]

    async def create_index(self):
        print("Creating group indexes for id")
        self.collection.create_index([('id', pymongo.ASCENDING)])

    async def create(self, group_model: GroupModel):
        group_model.firstModified = str(datetime.now().isoformat())
        group_model.lastModified = str(datetime.now().isoformat())
        return self.collection.insert_one(GroupModel.to_json(group_model))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query).populate("owner", "user").skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            group_model = GroupModel.to_model(document)
            data.append(group_model)
        return data


    def update(self, query, update_data):
        update_data["lastModified"] = str(datetime.now().isoformat())
        set_update = {"$set": update_data}      
        return self.collection.update_one(query, set_update)


    def delete(self,query):
        return self.collection.delete_many(query)
