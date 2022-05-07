from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ContactModel(BaseModel):
    id: Optional[str] = None
    title : str
    body : str 
    sender : Optional[str] = None
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(contact_us_json):
        return ContactModel(
            id=contact_us_json["id"],
            title=contact_us_json["title"],
            body=contact_us_json["body"],
            sender=contact_us_json["sender"],
            firstModified=contact_us_json["firstModified"],
            lastModified=contact_us_json["lastModified"],
        )

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.title != None: load["title"] = self.title
        if self.body != None: load["body"] = self.body
        if self.sender != None: load["sender"] = self.sender
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load

    @staticmethod
    def to_model_list(contact_us_jsons):
        toModelLists = []
        for contact_us_json in contact_us_jsons:
            toModelLists.append(ContactModel.to_model(contact_us_json))
        return toModelLists    

    @staticmethod
    def to_json_list(contactUs_models):
        toJSONLists = []
        for contact_us_model in contactUs_models:
            toJSONLists.append(contact_us_model.to_json())
        return toJSONLists   
