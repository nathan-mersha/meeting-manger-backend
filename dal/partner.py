from model.partner import PartnerModel
from datetime import datetime
import configparser
import pymongo


class PartnerModelDAL:
    COLLECTION_NAME = "partner"

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
        print("Creating index for partner")

        indexInfo = self.collection.index_information() 
        indexKeys = indexInfo.keys()

        if "subject_1" not in indexKeys:
            print("creating new index for partner - subject")
            self.collection.create_index([('subject', pymongo.ASCENDING)])

        if "partner_1" not in indexKeys:  
            print("creating new index for partner - partner")  
            self.collection.create_index([('partner', pymongo.ASCENDING)])

        if "id_1" not in indexKeys:    
            print("creating new index for partner - id")
            self.collection.create_index([('id', pymongo.ASCENDING)])

    async def create(self, partnerModel: PartnerModel):
        partnerModel.firstModified = datetime.now()
        partnerModel.lastModified = datetime.now()
        return self.collection.insert_one(PartnerModel.to_json(partnerModel))

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query).skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            partnerModel = PartnerModel.to_model(document)
            data.append(partnerModel)
        return data


    def update(self, query, update_data):
        update_data["lastModified"] = datetime.now()
        set_update = {"$set": update_data}      
        return self.collection.update_one(query, set_update)


    def delete(self,query):
        return self.collection.delete_many(query)
