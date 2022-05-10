from model.blocklist import BlockListModel
from datetime import datetime
import configparser
import pymongo


class BlockListModelDAL:
    COLLECTION_NAME = "blockList"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")

        # database connection string
        data_base_connection_str = str(self.config['mongodb']['database_url'])
        data_base_name = str(self.config['mongodb']['database_name'])
        client = pymongo.MongoClient(data_base_connection_str, serverSelectionTimeoutMS=5000)
        db = client[data_base_name]
        self.collection = db[self.COLLECTION_NAME]

    async def create(self, blockListUsModel: BlockListModel):
        blockListUsModel.firstModified = str(datetime.now().isoformat())
        blockListUsModel.lastModified = str(datetime.now().isoformat())
        return self.collection.insert_one(BlockListModel.to_json(blockListUsModel))

    async def create_index(self):
        print("Creating index for block list")
        self.collection.create_index([('subject', pymongo.ASCENDING)])
        self.collection.create_index([('blocked', pymongo.ASCENDING)])

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query).skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            blockListUsModel = BlockListModel.to_model(document)
            data.append(blockListUsModel)
        return data

    def update(self, query, update_data):
        update_data["lastModified"] = str(datetime.now().isoformat())
        set_update = {"$set": update_data}      
        return self.collection.update_one(query, set_update)

    def delete(self,query):
        return self.collection.delete_many(query)
