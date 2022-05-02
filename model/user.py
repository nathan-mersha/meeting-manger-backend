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
    dob : Optional[str] = 'none'
    profilePicture : Optional[str] = 'none'
    password: str
    isEmailVerified:bool
    isPhoneVerified:bool
    payload: Optional[dict] = {}

    meetings: Optional[list] = []
    planType: Optional[dict] = {}
    partners: Optional[list] = []
    whiteList: Optional[list] = []
    groups: Optional[list] = []
    blockList: Optional[list] = []
    countryCode: Optional[str] = 'none'
    isAccountDeactivated: Optional[bool] = False
    isAccountLocked: Optional[bool] = False

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
            isEmailVerified=user_json["isEmailVerified"],
            isPhoneVerified=user_json["isPhoneVerified"],
            payload=user_json["payload"],

            # todo : Continue from here
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
            "isEmailVerified" : self.isEmailVerified,
            "isPhoneVerified" : self.isPhoneVerified,
            "payload" : self.payload,
            "firstModified": self.firstModified,
            "lastModified": self.lastModified
        }

        return load

class SignUpModel(BaseModel):
    firstName: Optional[str] = 'none'
    lastName: Optional[str] = 'none'
    companyName : Optional[str] = 'none'
    title : Optional[str] = 'none'
    email: str
    password: str

class RequestVerificationEmail(BaseModel):
    email:str
    
class RequestVerificationPhoneNumber(BaseModel):
    phoneNumber:str
    
class VerifyEmailModel(BaseModel):
    email: str
    verificationCode: str

class VerifyPhoneNumberModel(BaseModel):
    phoneNumber: str
    verificationCode: str

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
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    profilePicture: Optional[str] = None
    
    def to_json(self):
        load = {}
        if self.firstName != None: load["firstName"] = self.firstName
        if self.lastName != None: load["lastName"] = self.lastName
        if self.companyName != None: load["companyName"] = self.companyName
        if self.title != None: load["title"] = self.title
        if self.email != None: load["email"] = self.email
        if self.phoneNumber != None: load["phoneNumber"] = self.phoneNumber
        if self.gender != None: load["gender"] = self.gender
        if self.dob != None: load["dob"] = self.dob
        if self.profilePicture != None: load["profilePicture"] = self.profilePicture
        return load


