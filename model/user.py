from datetime import datetime
from optparse import Option
from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    id: Optional[str] = 'none'
    firstName: Optional[str] = 'none'
    lastName: Optional[str] = 'none'
    companyName : Optional[str] = 'none'
    title : Optional[str] = 'none'
    email: str
    phoneNumber: Optional[str] = 'none'
    gender : Optional[str] = 'none'
    dob : Option[str] = 'none'
    profilePicture : Optional[str] = 'none'
    password: str
    payload: Optional[dict] = {}
    firstModified: Optional[str] = str(datetime.now().isoformat())
    lastModified: Optional[str] = str(datetime.now().isoformat())

    @staticmethod
    def to_model(user_json):
        return UserModel(
            id=user_json["id"],
            firstName=user_json["firstName"],
            lastName=user_json["lastName"],
            companyName=user_json["companyName"],
            title=user_json["title"],
            email=user_json["email"],
            phoneNumber=user_json["phoneNumber"],
            gender=user_json["gender"],
            dob=user_json["dob"],
            profilePicture=user_json["profilePicture"],
            password=user_json["password"],
            payload=user_json["payload"],
            firstModified=user_json["firstModified"],
            lastModified=user_json["lastModified"]
        )

    def to_json(self):
        load = {
            "id": self.id,
            "firstName" : self.firstName,
            "lastName" : self.lastName,
            "companyName" : self.companyName,
            "title" : self.title,
            "email" : self.email,
            "phoneNumber" : self.phoneNumber,
            "gender" : self.gender,
            "dob" : self.dob,
            "profilePicture" : self.profilePicture,
            "password" : self.password,
            "payload" : self.payload,
            "firstModified": self.first_modified,
            "lastModified": self.last_modified
        }

        return load

class LoginModel(BaseModel):
    email: str
    password: str        

class ForgotPasswordModel(BaseModel):
    email: str    

class ResetPasswordModel(BaseModel):
    email: str
    reset_code: str
    new_password: str

class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str

class UpdateUserModel(BaseModel):
    name: Optional[str] = None

    def to_json(self):
        load = {}
        if self.name != None:
            load["name"] = self.name
        return load


