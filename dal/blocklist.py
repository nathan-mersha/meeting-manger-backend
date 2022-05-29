from model.blocklist import BlockListModel
from datetime import datetime
import configparser
import pymongo
from dal.user import UserModelDAL

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
        self.user_model_dal = UserModelDAL()

    async def create(self, blockListUsModel: BlockListModel):
        blockListUsModel.firstModified = datetime.now()
        blockListUsModel.lastModified = datetime.now()
        return self.collection.insert_one(BlockListModel.to_json(blockListUsModel))

    async def create_index(self):
        print("Creating index for block list")
        indexInfo = self.collection.index_information() 
        indexKeys = indexInfo.keys()
        if "subject_1" not in indexKeys:
            self.collection.create_index([('subject', pymongo.ASCENDING)])
        if "blocked_1" not in indexKeys:    
            self.collection.create_index([('blocked', pymongo.ASCENDING)])

    def read(self, query = {}, limit = 24, sort = 'firstModified', sort_type = pymongo.DESCENDING, page=1, populate="false"):
        data= []
        offset = (page * limit) - limit
        response = self.collection.find(query).skip(offset).limit(limit).sort(sort, sort_type)
        for document in response:
            blockListUsModel = BlockListModel.to_model(document)
            if populate == "true":
                # query subject
                subject_query = {"id" : blockListUsModel.subject}
                subjectsData  = self.user_model_dal.read(query=subject_query, limit=1)
                if len(subjectsData) == 0:
                    blockListUsModel.subject = None
                else:
                    blockListUsModel.subject = subjectsData[0]

                #query blocked
                blocked_query = {"id" : blockListUsModel.blocked}
                blockedData = self.user_model_dal.read(query=blocked_query, limit=1)
                if len(blockedData) == 0:
                    blockListUsModel.blocked = None
                else:
                    blockListUsModel.blocked = blockedData[0]


            data.append(blockListUsModel)
        return data

    def update(self, query, update_data):
        update_data["lastModified"] = datetime.now()
        set_update = {"$set": update_data}      
        return self.collection.update_one(query, set_update)

    def delete(self,query):
        return self.collection.delete_many(query)
