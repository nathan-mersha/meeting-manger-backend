from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import enum

class CreateWhiteListModel(BaseModel):
    to: str
    note : Optional[str] = None
    
class WhitelistStatus(str, enum.Enum):
        accepted = "accepted"
        denied = "denied"
        
class WhiteListModel(BaseModel):
    id: Optional[str] = None
    partyA: str
    partyB: str
    partyAAccepted : Optional[bool] = False
    partyBAccepted : Optional[bool] = False
    note : Optional[str] = None
    responded: Optional[bool] = False
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(whiteList_json):
        return WhiteListModel(
            id=whiteList_json["id"],
            partyA=whiteList_json["partyA"],
            partyB=whiteList_json["partyB"],
            partyAAccepted=whiteList_json["partyAAccepted"],
            partyBAccepted=whiteList_json["partyBAccepted"], 
            note=whiteList_json["note"],
            responded=whiteList_json["responded"],
            firstModified=whiteList_json["firstModified"],
            lastModified=whiteList_json["lastModified"],
        ) 

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.partyA != None: load["partyA"] = self.partyA
        if self.partyB != None: load["partyB"] = self.partyB
        if self.partyAAccepted != None: load["partyAAccepted"] = self.partyAAccepted
        if self.partyBAccepted != None: load["partyBAccepted"] = self.partyBAccepted
        if self.note != None: load["note"] = self.note
        if self.responded != None: load["responded"] = self.responded
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified
        return load

    @staticmethod
    def to_model_list(whiteList_jsons):
        toModelLists = []
        for whiteList_json in whiteList_jsons:
            toModelLists.append(WhiteListModel.to_model(whiteList_json))
        return toModelLists    

    @staticmethod
    def to_json_list(whiteList_models):
        toJSONLists = []
        for whiteList_model in whiteList_models:
            toJSONLists.append(whiteList_model.to_json())
        return toJSONLists   
