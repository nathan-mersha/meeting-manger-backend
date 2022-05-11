from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import enum

class ScheduleMode(str, enum.Enum):
    inPerson = "inPerson"
    virutal = "virtual"

class UpdateScheduleModel(BaseModel):
    date: datetime
    duration: str
    title: str
    note: str
    mode: Optional[ScheduleMode] = ScheduleMode.virutal
    repeat: Optional[str] = None
    travelTime: datetime

    def to_json(self):
        load = {}
    
        if self.date != None: load["date"] = self.date
        if self.duration != None: load["duration"] = self.duration
        if self.title != None: load["title"] = self.title
        if self.note != None: load["note"] = self.note
        if self.mode != None: load["mode"] = self.mode
        if self.repeat != None: load["repeat"] = self.repeat
        if self.travelTime != None: load["travelTime"] = self.travelTime

        return load

class ScheduleModel(BaseModel):
    id: Optional[str] = None
    userId: str
    date: datetime
    duration: str
    title: str
    note: str
    mode: Optional[ScheduleMode] = ScheduleMode.virutal
    repeat: Optional[str] = None
    travelTime: datetime
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(schedule_json):
        return ScheduleModel(
            id=schedule_json["id"],
            userId=schedule_json["userId"],
            date=schedule_json["date"],
            duration=schedule_json["duration"],
            title=schedule_json["title"],
            note=schedule_json["note"],
            mode=schedule_json["mode"],
            repeat=schedule_json["repeat"],
            travelTime=schedule_json["travelTime"],
            firstModified=schedule_json["firstModified"],
            lastModified=schedule_json["lastModified"],
        )

    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        
        if self.userId != None: load["userId"] = self.userId
        if self.date != None: load["date"] = self.date
        if self.duration != None: load["duration"] = self.duration
        if self.title != None: load["title"] = self.title
        if self.note != None: load["note"] = self.note
        if self.mode != None: load["mode"] = self.mode
        if self.repeat != None: load["repeat"] = self.repeat
        if self.travelTime != None: load["travelTime"] = self.travelTime

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
