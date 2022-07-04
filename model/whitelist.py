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
        print("to modell..... ....")
        return WhiteListModel(
            id=whiteList_json["id"] if "id" in whiteList_json else None,
            partyA=whiteList_json["partyA"] if "partyA" in whiteList_json else None,
            partyB=whiteList_json["partyB"] if "partyB" in whiteList_json else None,
            partyAAccepted=whiteList_json["partyAAccepted"] if "id" in whiteList_json else None,
            partyBAccepted=whiteList_json["partyBAccepted"] if "partyBAccepted" in whiteList_json else None,
            note=whiteList_json["note"] if "note" in whiteList_json else None,
            responded=whiteList_json["responded"] if "responded" in whiteList_json else None,
            firstModified=whiteList_json["firstModified"] if "firstModified" in whiteList_json else None,
            lastModified=whiteList_json["lastModified"] if "lastModified" in whiteList_json else None,
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
