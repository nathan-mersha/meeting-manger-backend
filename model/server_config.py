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
            id=config_json["id"] if "id" in config_json else None,
            tokenExpirationInDay=config_json["tokenExpirationInDay"] if "tokenExpirationInDay" in config_json else None,
            pricingPlan=config_json["pricingPlan"] if "pricingPlan" in config_json else None,
            promoPeriod=config_json["promoPeriod"] if "promoPeriod" in config_json else None,
            firstModified=config_json["firstModified"] if "firstModified" in config_json else None,
            lastModified=config_json["lastModified"] if "lastModified" in config_json else None,
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
