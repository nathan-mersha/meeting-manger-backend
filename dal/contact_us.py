from model.contact_us import ContactModel
from datetime import datetime
import configparser
import pymongo


class ContactUsModelDAL:
    COLLECTION_NAME = "contactUs"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        data_base_name = str(self.config['mongodb']['database_name'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[data_base_name]
        self.collection = db[self.COLLECTION_NAME]

    async def create(self, contactUsModel: ContactModel):
        contactUsModel.firstModified = datetime.now()
        contactUsModel.lastModified = datetime.now()
        return self.collection.insert_one(ContactModel.to_json(contactUsModel))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query).skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            contactUsModel = ContactModel.to_model(document)
            data.append(contactUsModel)
        return data


    def update(self, query, update_data):
        update_data["lastModified"] = datetime.now()
        set_update = {"$set": update_data}      
        return self.collection.update_one(query, set_update)


    def delete(self,query):
        return self.collection.delete_many(query)
