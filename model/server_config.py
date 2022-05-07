from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ConfigModel(BaseModel):
    id: Optional[str] = None
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
        load = {}

        if self.id != None: load["id"] = self.id
        if self.tokenExpirationInDay != None: load["tokenExpirationInDay"] = self.tokenExpirationInDay
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load
