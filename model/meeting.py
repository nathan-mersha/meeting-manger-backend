from datetime import datetime
import enum
from pydantic import BaseModel
from typing import List, Optional


class MeetingModeModel(str, enum.Enum):
    virtual = "virtual"
    inPersion = "inPerson"


class MeetingStatus(str, enum.Enum):
    upComming = "upComming"
    active = "active"
    canceled = "canceled"
    ended = "ended"


class MeetingAttendeStatus(str, enum.Enum):
    pending = "pending"
    accept = "accept"
    reject = "reject"


class MeetingAttendees(BaseModel):
    id: Optional[str] = None
    userId: Optional[str] = None
    email: Optional[str] = None
    status: Optional[MeetingAttendeStatus] = MeetingAttendeStatus.pending
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(meeting_attendees_json):
        print(meeting_attendees_json)
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
        # print(meetings_model)
        toJSONLists = []
        for meeting_model in meetings_model:
            print("to json begin .... ")
            print(meeting_model)
            print("to json end ....")
            toJSONLists.append(meeting_model.to_json())

        return toJSONLists

    def to_json(self):
        load = {
            "id": self.id,
            "userId": self.userId,
            "email": self.email,
            "status": self.status,
            "firstModified": self.firstModified,
            "lastModified": self.lastModified
        }

        if self.id != None:
            load["id"] = self.id
        if self.userId != None:
            load["userId"] = self.userId
        if self.email != None:
            load["email"] = self.email
        if self.status != None:
            load["status"] = self.status
        if self.firstModified != None:
            load["firstModified"] = self.firstModified
        if self.lastModified != None:
            load["lastModified"] = self.lastModified

        return load


class MeetingModel(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    host: str
    hostName: Optional[str] = None
    attendees: Optional[list] = []
    fromDate: Optional[datetime] = None
    toDate: Optional[datetime] = None
    mode: MeetingModeModel
    meetingLink: Optional[str] = None
    status: MeetingStatus
    note: Optional[str] = None
    reminderNote: Optional[str] = None
    reminderTitle: Optional[str] = None
    remindBefore: Optional[str] = None
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(meeting_json):
        return MeetingModel(
            id=meeting_json["id"] if "id" in meeting_json else None,
            title=meeting_json["title"] if "title" in meeting_json else None,
            description=meeting_json["description"] if "description" in meeting_json else None,
            host=meeting_json["host"] if "host" in meeting_json else None,
            hostName=meeting_json["hostName"] if "hostName" in meeting_json else None,
            attendees=MeetingAttendees.to_model_list(
                meeting_json["attendees"]),
            fromDate=meeting_json["fromDate"] if "fromDate" in meeting_json else None,
            toDate=meeting_json["toDate"] if "toDate" in meeting_json else None,
            mode=meeting_json["mode"] if "mode" in meeting_json else None,
            meetingLink=meeting_json["meetingLink"] if "meetingLink" in meeting_json else None,
            status=meeting_json["status"] if "status" in meeting_json else None,
            note=meeting_json["note"] if "note" in meeting_json else None,
            reminderNote=meeting_json["reminderNote"] if "reminderNote" in meeting_json else None,
            reminderTitle=meeting_json["reminderTitle"] if "reminderTitle" in meeting_json else None,
            remindBefore=meeting_json["remindBefore"] if "remindBefore" in meeting_json else None,
            firstModified=meeting_json["firstModified"] if "firstModified" in meeting_json else None,
            lastModified=meeting_json["lastModified"] if "lastModified" in meeting_json else None,
        )

    @staticmethod
    def to_json_list(meetings_model):
        toJSONLists = []
        for meeting_model in meetings_model:
            toJSONLists.append(meeting_model.to_json())
        return toJSONLists

    def to_json(self):

        load = {}

        if self.id != None:
            load["id"] = self.id
        if self.title != None:
            load["title"] = self.title
        if self.description != None:
            load["description"] = self.description
        if self.host != None:
            load["host"] = self.host
        if self.hostName != None:
            load["hostName"] = self.hostName
        if self.attendees != None:
            load["attendees"] = MeetingAttendees.to_json_list(self.attendees)
        if self.fromDate != None:
            load["fromDate"] = self.fromDate
        if self.toDate != None:
            load["toDate"] = self.toDate
        if self.mode != None:
            load["mode"] = self.mode
        if self.meetingLink != None:
            load["meetingLink"] = self.meetingLink
        if self.status != None:
            load["status"] = self.status
        if self.note != None:
            load["note"] = self.note
        if self.reminderNote != None:
            load["reminderNote"] = self.reminderNote
        if self.reminderTitle != None:
            load["reminderTitle"] = self.reminderTitle
        if self.remindBefore != None:
            load["remindBefore"] = self.remindBefore
        if self.firstModified != None:
            load["firstModified"] = self.firstModified
        if self.lastModified != None:
            load["lastModified"] = self.lastModified

        return load


class UpdateAttendee(BaseModel):
    attendees: List[str]


class UpdateAttendeeActions(str, enum.Enum):
    add = "add"
    remove = "remove"


class UpdateMeetingModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fromDate: Optional[datetime] = None
    toDate: Optional[datetime] = None
    mode: Optional[MeetingModeModel] = None
    meetingLink: Optional[str] = None
    status: Optional[MeetingStatus] = None
    note: Optional[str] = None
    reminderNote: Optional[str] = None
    reminderTitle: Optional[str] = None
    remindBefore: Optional[str] = None

    def to_json(self):
        load = {}
        if self.title != None:
            load["title"] = self.title
        if self.description != None:
            load["description"] = self.description
        if self.fromDate != None:
            load["fromDate"] = self.fromDate
        if self.toDate != None:
            load["toDate"] = self.toDate
        if self.mode != None:
            load["mode"] = self.mode
        if self.meetingLink != None:
            load["meetingLink"] = self.meetingLink
        if self.status != None:
            load["status"] = self.status
        if self.note != None:
            load["note"] = self.note
        if self.reminderNote != None:
            load["reminderNote"] = self.reminderNote
        if self.reminderTitle != None:
            load["reminderTitle"] = self.reminderTitle
        if self.remindBefore != None:
            load["remindBefore"] = self.remindBefore

        return load
