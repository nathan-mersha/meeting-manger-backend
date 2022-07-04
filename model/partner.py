from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CreatePartners(BaseModel):
    partners : list

    
class PartnerModel(BaseModel):
    id: Optional[str] = None
    subject: str
    partner: str
    areWhiteList : bool = False
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(partner_json):
        return PartnerModel(
            id=partner_json["id"] if "id" in partner_json else None,
            subject=partner_json["subject"] if "subject" in partner_json else None,
            partner=partner_json["partner"] if "partner" in partner_json else None,
            areWhiteList=partner_json["areWhiteList"] if "areWhiteList" in partner_json else None,
            firstModified=partner_json["firstModified"] if "firstModified" in partner_json else None,
            lastModified=partner_json["lastModified"] if "lastModified" in partner_json else None,
        ) 

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.subject != None: load["subject"] = self.subject
        if self.partner != None: load["partner"] = self.partner
        if self.areWhiteList != None: load["areWhiteList"] = self.areWhiteList
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load

    @staticmethod
    def to_model_list(partner_jsons):
        toModelLists = []
        for partner_json in partner_jsons:
            toModelLists.append(PartnerModel.to_model(partner_json))
        return toModelLists    

    @staticmethod
    def to_json_list(partner_models):
        toJSONLists = []
        for partner_model in partner_models:
            toJSONLists.append(partner_model.to_json())
        return toJSONLists   
