from operator import index
from model.user import UserModel
from datetime import datetime
import configparser
import pymongo


class UserModelDAL:
    COLLECTION_NAME = "user"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        data_base_name = str(self.config['mongodb']['database_name'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[data_base_name]
        self.collection = db[self.COLLECTION_NAME]

    async def create_index(self):
        print("Creating user indexes for user model")
        
        indexInfo = self.collection.index_information() 
        indexKeys = indexInfo.keys()

        if "id_1" not in indexKeys:
            print("creating new index for user - id")
            self.collection.create_index([('id', pymongo.ASCENDING)],unique=True)

        if "phoneNumber_text" not in indexKeys:
            self.collection.create_index([('phoneNumber', 'text'),('email', 'text'),('firstName', 'text')])

    async def create(self, user_model: UserModel):
        user_model.firstModified = datetime.now()
        user_model.lastModified = datetime.now()
        return self.collection.insert_one(UserModel.to_json(user_model))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1,select={"_id" : 0}):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query, select).skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            user_model = UserModel.to_model(document)
            data.append(user_model)
        return data

    def update(self, query = None, update_data = None):
        update_data["lastModified"] = datetime.now()
        set_update = {"$set": update_data}
        return self.collection.update_one(query, set_update)

    def delete(self, query = {}):
        return self.collection.delete_many(query)
