from datetime import datetime
from distutils.command.config import config
from pydantic import BaseModel
from typing import Optional


class ConfigModel(BaseModel):
    id: Optional[str] = None
    tokenExpirationInDay: Optional[int] = 60 #default 60 days 
    pricingPlan : dict
    promoPeriod : Optional[int] = 0
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @staticmethod
    def to_model(config_json):
        return ConfigModel(
            id=config_json["id"],
            tokenExpirationInDay=config_json["tokenExpirationInDay"],
            pricingPlan=config_json["pricingPlan"],
            promoPeriod=config_json["promoPeriod"],
            firstModified=config_json["firstModified"],
            lastModified=config_json["lastModified"]
        )

    def to_json(self):
        load = {}

        if self.id != None: load["id"] = self.id
        if self.tokenExpirationInDay != None: load["tokenExpirationInDay"] = self.tokenExpirationInDay
        if self.pricingPlan != None: load["pricingPlan"] = self.pricingPlan
        if self.promoPeriod != None: load["promoPeriod"] = self.promoPeriod
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified

        return load
