from optparse import Option
from tokenize import group
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class GroupModel(BaseModel):
    id: Optional[str] = 'none'
    name : str = 'none'
    description : Optional[str] = 'none'
    owner: Optional[str] = 'none'
    members: Optional[list] = []
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(group_json):
        return GroupModel(
            id=group_json["id"],
            name=group_json["name"],
            description=group_json["description"],
            owner=group_json["owner"],
            members=group_json["members"],
            firstModified=group_json["firstModified"],
            lastModified=group_json["lastModified"],
        )

    def to_json(self):
        load = {
            "id" : self.id,
            "name" : self.name,
            "description" : self.description,
            "owner" : self.owner,
            "members" : self.members,
            "firstModified" : self.firstModified,
            "lastModified" : self.lastModified
        }

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
    name: str = 'none'
    description : Optional[str] = 'none'
    owner: Optional[str] = 'none'
    members: Optional[list] = []

    def to_json(self):
        load = {
            "name" : self.name,
            "description" : self.description,
            "owner" : self.owner,
            "members" : self.members
        }
        return load