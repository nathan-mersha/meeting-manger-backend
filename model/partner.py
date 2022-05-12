from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PartnerModel(BaseModel):
    id: Optional[str] = None
    subject: str
    partner: str
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(partner_json):
        return PartnerModel(
            id=partner_json["id"],
            subject=partner_json["subject"],
            partner=partner_json["partner"],
            firstModified=partner_json["firstModified"],
            lastModified=partner_json["lastModified"],
        ) 

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.subject != None: load["subject"] = self.subject
        if self.partner != None: load["partner"] = self.partner
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
