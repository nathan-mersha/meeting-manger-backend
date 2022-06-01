from model.server_config import ConfigModel
from datetime import datetime

import configparser
import pymongo


class ConfigModelDAL:
    COLLECTION_NAME = "config"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")
        self.configId = self.config["secrets"]["config_id"]

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        data_base_name = str(self.config['mongodb']['database_name'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[data_base_name]
        self.collection = db[self.COLLECTION_NAME]

    async def create(self, config_model: ConfigModel):
        config_model.firstModified = datetime.now()
        config_model.lastModified = datetime.now()
        return self.collection.insert_one(ConfigModel.to_json(config_model))

    def read(self):
        query = {"id" : self.configId}
        response = self.collection.find(query)
        return ConfigModel.to_model(response[0])

    def update(self, query, update_data):
        update_data["lastModified"] = str(datetime.now())
        set_update = {"$set": update_data}
        

        return self.collection.update_one(query, set_update)

    def delete(self, query = {}):
        return self.collection.delete_many(query)
