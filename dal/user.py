from model.user import UserModel
from datetime import datetime
import configparser
import pymongo


class UserModelDAL:
    DATABASE_NAME = "arrangeDevDB"
    COLLECTION_NAME = "user"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[self.DATABASE_NAME]
        self.collection = db[self.COLLECTION_NAME]

    async def create_index(self):
        print("Creating user indexes for : id,email,phonenumber")
        self.collection.create_index([('id', pymongo.ASCENDING)],unique=True)
        self.collection.create_index([('email', pymongo.ASCENDING)],unique=True)
        self.collection.create_index([('phoneNumber', pymongo.ASCENDING)])
        

    async def create(self, user_model: UserModel):
        user_model.firstModified = str(datetime.now().isoformat())
        user_model.lastModified = str(datetime.now().isoformat())
        return self.collection.insert_one(UserModel.to_json(user_model))

    
    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query).skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            user_model = UserModel.to_model(document)
            data.append(user_model)
        return data


    def update(self, query = None, update_data = None):
        update_data["lastModified"] = str(datetime.now().isoformat())
        set_update = {"$set": update_data}
        return self.collection.update_one(query, set_update)


    def delete(self, query = {}):
        return self.collection.delete_many(query)
