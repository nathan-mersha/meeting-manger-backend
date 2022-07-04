from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ContactModel(BaseModel):
    id: Optional[str] = None
    title : str
    body : str 
    sender : Optional[str] = None
    resolved : Optional[bool] = False
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(contact_us_json):
        return ContactModel(
            id=contact_us_json["id"] if "id" in contact_us_json else None,
            title=contact_us_json["title"] if "title" in contact_us_json else None,
            body=contact_us_json["body"] if "body" in contact_us_json else None,
            sender=contact_us_json["sender"] if "sender" in contact_us_json else None,
            resolved =contact_us_json["resolved"] if "resolved" in contact_us_json else None,
            firstModified=contact_us_json["firstModified"] if "firstModified" in contact_us_json else None,
            lastModified=contact_us_json["lastModified"] if "lastModified" in contact_us_json else None,
        )

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.title != None: load["title"] = self.title
        if self.body != None: load["body"] = self.body
        if self.sender != None: load["sender"] = self.sender
        if self.resolved != None: load["resolved"] = self.resolved
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
