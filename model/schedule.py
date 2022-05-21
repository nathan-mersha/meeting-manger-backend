from optparse import Option
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from model.meeting import MeetingModeModel


class RequestAvailableTimeModel(BaseModel):
    attendees: List[str]
    fromDate : datetime
    toDate : datetime
    duration : str

class UpdateScheduleModel(BaseModel):
    fromDate: Optional[datetime]
    toDate: Optional[datetime]
    title: Optional[str]
    note: Optional[str]
    mode: Optional[MeetingModeModel] = MeetingModeModel.virtual

    def to_json(self):
        load = {}
    
        if self.fromDate != None: load["fromDate"] = self.fromDate
        if self.toDate != None: load["toDate"] = self.toDate
        if self.title != None: load["title"] = self.title
        if self.note != None: load["note"] = self.note
        if self.mode != None: load["mode"] = self.mode

        return load

class ScheduleModel(BaseModel):
    id: Optional[str] = None
    userId: str
    fromDate: datetime
    toDate:datetime
    title: Optional[str] = None
    note: Optional[str] = None
    mode: Optional[MeetingModeModel] = MeetingModeModel.virtual
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(schedule_json):
        return ScheduleModel(
            id=schedule_json["id"],
            userId=schedule_json["userId"],
            fromDate=schedule_json["fromDate"],
            toDate=schedule_json["toDate"],
            title=schedule_json["title"],
            note=schedule_json["note"],
            mode=schedule_json["mode"],
            firstModified=schedule_json["firstModified"],
            lastModified=schedule_json["lastModified"],
        )

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.userId != None: load["userId"] = self.userId
        if self.fromDate != None: load["fromDate"] = self.fromDate
        if self.toDate != None: load["toDate"] = self.toDate
        if self.title != None: load["title"] = self.title
        if self.note != None: load["note"] = self.note
        if self.mode != None: load["mode"] = self.mode
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load

    @staticmethod
    def to_model_list(schedule_jsons):
        toModelLists = []
        for schedule_json in schedule_jsons:
            toModelLists.append(ScheduleModel.to_model(schedule_json))
        return toModelLists    

    @staticmethod
    def to_json_list(contactUs_models):
        toJSONLists = []
        for schedule_model in contactUs_models:
            toJSONLists.append(schedule_model.to_json())
        return toJSONLists   
