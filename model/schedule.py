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
            id=schedule_json["id"] if "id" in schedule_json else None,
            userId=schedule_json["userId"] if "userId" in schedule_json else None,
            fromDate=schedule_json["fromDate"] if "fromDate" in schedule_json else None,
            toDate=schedule_json["toDate"] if "toDate" in schedule_json else None,
            title=schedule_json["title"] if "title" in schedule_json else None,
            note=schedule_json["note"] if "note" in schedule_json else None,
            mode=schedule_json["mode"] if "mode" in schedule_json else None,
            firstModified=schedule_json["firstModified"] if "firstModified" in schedule_json else None,
            lastModified=schedule_json["lastModified"] if "lastModified" in schedule_json else None,
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
