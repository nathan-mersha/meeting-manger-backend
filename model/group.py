from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class GroupModel(BaseModel):
    id: Optional[str] = None
    name : str = None
    description : Optional[str] = None
    owner: Optional[str] = None
    members: Optional[list] = []
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(group_json):
        return GroupModel(
            id=group_json["id"] if "id" in group_json else None,
            name=group_json["name"] if "name" in group_json else None,
            description=group_json["description"] if "description" in group_json else None,
            owner=group_json["owner"] if "owner" in group_json else None,
            members=group_json["members"] if "members" in group_json else None,
            firstModified=group_json["firstModified"] if "firstModified" in group_json else None,
            lastModified=group_json["lastModified"] if "lastModified" in group_json else None,
        )

    def to_json(self):

        load = {}

        if self.id != None: load["id"] = self.id
        if self.name != None: load["name"] = self.name
        if self.description != None: load["description"] = self.description
        if self.owner != None: load["owner"] = self.owner
        if self.members != None: load["members"] = self.members
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load

    @staticmethod
    def to_model_list(group_json):
        toModelLists = []
        for meeting_json in group_json:
            toModelLists.append(GroupModel.to_model(meeting_json))
        return toModelLists    

    @staticmethod
    def to_json_list(groups_model):
        toJSONLists = []
        for group_model in groups_model:
            toJSONLists.append(group_model.to_json())
        return toJSONLists   

class UpdateGroupModel(BaseModel):
    name: str = None
    description : Optional[str] = None
    owner: Optional[str] = None
    members: Optional[list] = []

    def to_json(self):
        load = {
            "name" : self.name,
            "description" : self.description,
            "owner" : self.owner,
            "members" : self.members
        }

        if self.name != None: load["name"] = self.name
        if self.description != None: load["description"] = self.description
        if self.owner != None: load["owner"] = self.owner
        if self.members != None: load["members"] = self.members
        
        return load