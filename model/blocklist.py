from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BlockListModel(BaseModel):
    id: Optional[str] = None
    subject: str
    blocked: str
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(blockList_us_json):
        return BlockListModel(
            id=blockList_us_json["id"] if "id" in blockList_us_json else None,
            subject=blockList_us_json["subject"] if "subject" in blockList_us_json else None,
            blocked=blockList_us_json["blocked"] if "blocked" in blockList_us_json else None,
            firstModified=blockList_us_json["firstModified"] if "firstModified" in blockList_us_json else None,
            lastModified=blockList_us_json["lastModified"] if "lastModified" in blockList_us_json else None,
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
