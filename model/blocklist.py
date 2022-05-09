from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BlockListModel(BaseModel):
    id: Optional[str] = None
    subject: str
    blocked: str
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(blockList_us_json):
        return BlockListModel(
            id=blockList_us_json["id"],
            subject=blockList_us_json["subject"],
            blocked=blockList_us_json["blocked"],
            firstModified=blockList_us_json["firstModified"],
            lastModified=blockList_us_json["lastModified"],
        )

    def to_json(self):
        load = {}

        if self.id != None: load["id"] = self.id
        if self.subject != None: load["subject"] = self.subject
        if self.blocked != None: load["blocked"] = self.blocked
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load

    @staticmethod
    def to_model_list(blockList_us_jsons):
        toModelLists = []
        for blockList_us_json in blockList_us_jsons:
            toModelLists.append(BlockListModel.to_model(blockList_us_json))
        return toModelLists    

    @staticmethod
    def to_json_list(blockListUs_models):
        toJSONLists = []
        for blockList_us_model in blockListUs_models:
            toJSONLists.append(blockList_us_model.to_json())
        return toJSONLists   
