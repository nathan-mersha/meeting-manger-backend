from model.notification import NotificationModel
from datetime import datetime

import configparser
import pymongo


class NotificationModelDAL:
    COLLECTION_NAME = "notification"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        data_base_name = str(self.config['mongodb']['database_name'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[data_base_name]
        self.collection = db[self.COLLECTION_NAME]


    async def create(self, notification_model: NotificationModel):
        notification_model.first_modified = str(datetime.now().isoformat())
        notification_model.last_modified = str(datetime.now().isoformat())
        return self.collection.insert_one(NotificationModel.to_json(notification_model))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING):
        data = []
        response = self.collection.find(query).limit(limit).sort(sort, sort_type)
        for document in response:
            user_model = NotificationModel.to_model(document)
            data.append(user_model)
        print(f"data find {data}")        
        return data


    def update(self, query, update_data):
        update_data["lastModified"] = str(datetime.now().isoformat())
        set_update = {"$set": update_data}
        return self.collection.update_one(query, set_update)


    def delete(self):
        pass
