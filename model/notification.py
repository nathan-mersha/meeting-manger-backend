from pydantic import BaseModel
from typing import Optional

class NotificationModel(BaseModel):
    id:str
    user_id: str
    payload: dict
    sent: bool
    first_modified: Optional[str]
    last_modified: Optional[str]

    @staticmethod
    def to_model(notification_json):
        return NotificationModel(
            id=notification_json["id"] if "id" in notification_json else None,
            user_id=notification_json["userId"] if "userId" in notification_json else None,
            payload=notification_json["payload"] if "payload" in notification_json else None,
            sent=notification_json["sent"] if "sent" in notification_json else None,
            first_modified=notification_json["firstModified"] if "firstModified" in notification_json else None,
            last_modified=notification_json["lastModified"] if "lastModified" in notification_json else None,

        )

    def to_json(self):
        load = {
            "id" : self.id,
            "userId" : self.user_id,
            "payload" : self.payload,
            "sent" : self.sent,
            "firstModified" : self.first_modified,
            "lastModified" : self.last_modified
        }
        return load