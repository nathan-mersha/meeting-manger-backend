from datetime import datetime
import enum
from pydantic import BaseModel
from typing import Optional


class MeetingModeModel(str, enum.Enum):
    virtual = "virutal"
    inPersion = "inPerson"

class MeetingStatus(str,enum.Enum):
    upComming = "upComming"
    active = "active"
    canceled = "canceled"
    ended = "ended"

class MeetingAttendeStatus(str, enum.Enum):
    pending = "pending"
    accept = "accept"
    reject = "reject"    

class MeetingAttendees(BaseModel):
    id: Optional[str] = 'none'
    userId : Optional[str] = 'none'
    email: Optional[str] = 'none'
    status : Optional[MeetingAttendeStatus] = MeetingAttendeStatus.pending
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(meeting_attendees_json):
        return MeetingAttendees(
            id=meeting_attendees_json["id"],
            userId=meeting_attendees_json["userId"],
            email=meeting_attendees_json["email"],
            status=meeting_attendees_json["status"],
            firstModified=meeting_attendees_json["firstModified"],
            lastModified=meeting_attendees_json["lastModified"],
        )

    @staticmethod
    def to_model_list(meetings_json):
        toModelLists = []
        for meeting_json in meetings_json:
            toModelLists.append(MeetingAttendees.to_model(meeting_json))
        return toModelLists

    @staticmethod
    def to_json_list(meetings_model):
        
        toJSONLists = []
        for meeting_model in meetings_model:
            toJSONLists.append(meeting_model.to_json())

        
        return toJSONLists        

    def to_json(self):
        load={
            "id" : self.id,
            "userId" : self.userId,
            "email" : self.email,
            "status" : self.status,
            "firstModified" : self.firstModified,
            "lastModified" : self.lastModified
        }    
        return load

class MeetingModel(BaseModel):
    id: Optional[str] = 'none'
    title:Optional[str] = 'none'
    description:Optional[str] = 'none'
    host: str
    attendees : Optional[list] = []
    date: Optional[str] = 'none'
    time : Optional[str] = 'none'
    duration : Optional[str] = 'none'
    mode : MeetingModeModel
    meetingLink : Optional[str] = 'none'
    status: MeetingStatus
    note : Optional[str] = 'none'
    reminderNote : Optional[str] = 'none'
    reminderTitle : Optional[str] = 'none'
    remindBefore : Optional[str] = 'none'
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(meeting_json):
     
        return MeetingModel(
            id=meeting_json["id"],
            title=meeting_json["title"],
            description=meeting_json["description"],
            host=meeting_json["host"],
            attendees=MeetingAttendees.to_model_list(meeting_json["attendees"]),
            date=meeting_json["date"],
            time=meeting_json["time"],
            duration=meeting_json["duration"],
            mode=meeting_json["mode"],
            meetingLink=meeting_json["meetingLink"],
            status=meeting_json["status"],
            note=meeting_json["note"],
            reminderNote=meeting_json["reminderNote"],
            reminderTitle=meeting_json["reminderTitle"],
            remindBefore=meeting_json["remindBefore"],
            firstModified=meeting_json["firstModified"],
            lastModified=meeting_json["lastModified"]
        )

    @staticmethod
    def to_json_list(meetings_model):
        toJSONLists = []
        for meeting_model in meetings_model:
            toJSONLists.append(meeting_model.to_json())
        return toJSONLists 

    def to_json(self):
        load = {
            "id": self.id,
            "title" : self.title,
            "description" : self.description,
            "host" : self.host,
            "attendees" : MeetingAttendees.to_json_list(self.attendees),
            "date" : self.date,
            "time" : self.time,
            "duration" : self.duration,
            "mode" : self.mode,
            "meetingLink" : self.meetingLink,
            "status" : self.status,
            "note" : self.note,
            "reminderNote" : self.reminderNote,
            "reminderTitle" : self.reminderTitle,
            "remindBefore" : self.remindBefore,
            "firstModified": self.firstModified,
            "lastModified": self.lastModified
        }

        return load


class UpdateMeetingModel(BaseModel):
    title:Optional[str] = None
    description:Optional[str] = None
    date: Optional[str] = None
    time : Optional[str] = None
    duration : Optional[str] = None
    mode : Optional[MeetingModeModel] = None 
    meetingLink : Optional[str] = None
    status: Optional[MeetingStatus] = None
    note : Optional[str] = None
    reminderNote : Optional[str] = None
    reminderTitle : Optional[str] = None
    remindBefore : Optional[str] = None

    def to_json(self):
        load = {}
        if self.title != None: load["title"] = self.title
        if self.description != None: load["description"] = self.description
        if self.date != None: load["date"] = self.date
        if self.time != None: load["time"] = self.time
        if self.duration != None: load["duration"] = self.duration
        if self.mode != None: load["mode"] = self.mode
        if self.meetingLink != None: load["meetingLink"] = self.meetingLink
        if self.status != None: load["status"] = self.status
        if self.note != None: load["note"] = self.note
        if self.reminderNote != None: load["reminderNote"] = self.reminderNote
        if self.reminderTitle != None: load["reminderTitle"] = self.reminderTitle
        if self.remindBefore != None: load["remindBefore"] = self.remindBefore