from uvicorn import Config
from model.server_config import ConfigModel
from datetime import datetime

import configparser
import pymongo


class ConfigModelDAL:
    DATABASE_NAME = "arrangeDevDB"
    COLLECTION_NAME = "config"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[self.DATABASE_NAME]
        self.collection = db[self.COLLECTION_NAME]

    async def create(self, config_model: ConfigModel):
        config_model.firstModified = str(datetime.now().isoformat())
        config_model.lastModified = str(datetime.now().isoformat())
        return self.collection.insert_one(ConfigModel.to_json(config_model))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING):
        data = []
        response = self.collection.find(query).limit(limit).sort(sort, sort_type)
        for document in response:
            user_model = ConfigModel.to_model(document)
            data.append(user_model)
        return data


    def update(self, query, update_data):
        update_data["lastModified"] = str(datetime.now().isoformat())
        set_update = {"$set": update_data}
        return self.collection.update_one(query, set_update)


    def delete(self):
        pass
