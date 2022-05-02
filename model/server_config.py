from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ConfigModel(BaseModel):
    id: Optional[str] = 'none'
    tokenExpirationInDay: Optional[int] = 60 #default 60 days 
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(config_json):
        return ConfigModel(
            id=config_json["id"],
            tokenExpirationInDay=config_json["tokenExpirationInDay"],
            firstModified=config_json["firstModified"],
            lastModified=config_json["lastModified"]
        )

    def to_json(self):
        load = {
            "id": self.id,
            "tokenExpirationInDay" : self.tokenExpirationInDay,
            "firstModified": self.firstModified,
            "lastModified": self.lastModified
        }

        return load
