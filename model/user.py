from datetime import datetime, time
from pydantic import BaseModel, validator
from typing import List, Optional
import enum

from pytz import timezone

class AvailableDays(int, enum.Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THRUSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

class UserType(str, enum.Enum):
    USER = "user"
    OPERATOR = "operator"
    ADMINISTRATOR = "administrator"
    
class UserModel(BaseModel):
    id: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName : Optional[str] = None
    title : Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    gender : Optional[str] = None
    dob : Optional[str] = None
    profilePicture : Optional[str] = None
    availableFrom: Optional[str] = None
    availableTo: Optional[str] = None
    userType: Optional[UserType] = UserType.USER
    workingDays : Optional[List[AvailableDays]] = [AvailableDays.MONDAY, AvailableDays.TUESDAY, AvailableDays.WEDNESDAY, AvailableDays.THRUSDAY, AvailableDays.FRIDAY]
    password: Optional[str] = None
    isEmailVerified:Optional[bool] = False
    isPhoneVerified:Optional[bool] = False
    isPublic:Optional[bool] = True
    payload: Optional[dict] = {}
    planType: Optional[str] = "basic"
    countryCode: Optional[str] = None
    timezone:Optional[str] = "UTC"
    meetingInAMouth: Optional[int] = 0
    meetingTotal: Optional[int] = 0
    meetingMouth: Optional[str] = None
    country: Optional[str] = None
    nationalHoliday : Optional[str] = None
    isAccountDeactivated: Optional[bool] = False
    isAccountLocked: Optional[bool] = False
    planTypeIsActiveTill: Optional[datetime] = None
    firstModified: Optional[datetime] = datetime.now()
    lastModified: Optional[datetime] = datetime.now()

    @validator('email')
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("email must contain @")
        return v

        
    @staticmethod
    def to_model_out(user_json):
        return UserModel(
            id=user_json["id"] if "id" in user_json else None,
            firstName=user_json["firstName"] if "firstName" in user_json else None,
            lastName=user_json["lastName"] if "lastName" in user_json else None,
            companyName=user_json["companyName"] if "companyName" in user_json else None,
            title=user_json["title"] if "title" in user_json else None,
            email=user_json["email"] if "email" in user_json else None,
            phoneNumber=user_json["phoneNumber"] if "phoneNumber" in user_json else None,
            gender=user_json["gender"] if "gender" in user_json else None,
            dob=user_json["dob"] if "dob" in user_json else None,
            profilePicture=user_json["profilePicture"] if "profilePicture" in user_json else None,
            availableFrom=user_json["availableFrom"] if "availableFrom" in user_json else None,
            availableTo=user_json["availableTo"] if "availableTo" in user_json else None,
            userType=user_json["userType"] if "userType" in user_json else None,
            workingDays=user_json["workingDays"] if "workingDays" in user_json else None,
            isEmailVerified=user_json["isEmailVerified"] if "isEmailVerified" in user_json else None,
            isPhoneVerified=user_json["isPhoneVerified"] if "isPhoneVerified" in user_json else None,
            isPublic=user_json["isPublic"] if "isPublic" in user_json else True,
            payload=user_json["payload"] if "payload" in user_json else None,
            planType=user_json["planType"] if "planType" in user_json else None,
            countryCode=user_json["countryCode"] if "countryCode" in user_json else None,
            country=user_json["country"] if "country" in user_json else None,
            timezone=user_json["timezone"] if "timezone" in user_json else "UTC",
            meetingInAMouth=user_json["meetingInAMouth"] if "meetingInAMouth" in user_json else 0,
            meetingTotal=user_json["meetingTotal"] if "meetingTotal" in user_json else 0,
            meetingMouth=user_json["meetingMouth"] if "meetingMouth" in user_json else None,
            nationalHoliday=user_json["nationalHoliday"] if "nationalHoliday" in user_json else None,
            isAccountDeactivated=user_json["isAccountDeactivated"] if "isAccountDeactivated" in user_json else None,
            isAccountLocked=user_json["isAccountLocked"] if "isAccountLocked" in user_json else None,
            planTypeIsActiveTill=user_json["planTypeIsActiveTill"] if "planTypeIsActiveTill" in user_json else None,
            firstModified=user_json["firstModified"] if "firstModified" in user_json else None,
            lastModified=user_json["lastModified"] if "lastModified" in user_json else None
        )
    @staticmethod
    def to_model(user_json):
        return UserModel(
            id=user_json["id"] if "id" in user_json else None,
            firstName=user_json["firstName"] if "firstName" in user_json else None,
            lastName=user_json["lastName"] if "lastName" in user_json else None,
            companyName=user_json["companyName"] if "companyName" in user_json else None,
            title=user_json["title"] if "title" in user_json else None,
            email=user_json["email"] if "email" in user_json else None,
            phoneNumber=user_json["phoneNumber"] if "phoneNumber" in user_json else None,
            gender=user_json["gender"] if "gender" in user_json else None,
            dob=user_json["dob"] if "dob" in user_json else None,
            profilePicture=user_json["profilePicture"] if "profilePicture" in user_json else None,
            availableFrom=user_json["availableFrom"] if "availableFrom" in user_json else None,
            availableTo=user_json["availableTo"] if "availableTo" in user_json else None,
            userType=user_json["userType"] if "userType" in user_json else None,
            workingDays=user_json["workingDays"] if "workingDays" in user_json else None,
            password=user_json["password"] if "password" in user_json else None,
            isEmailVerified=user_json["isEmailVerified"] if "isEmailVerified" in user_json else None,
            isPhoneVerified=user_json["isPhoneVerified"] if "isPhoneVerified" in user_json else None,
            isPublic=user_json["isPublic"] if "isPublic" in user_json else True,
            payload=user_json["payload"] if "payload" in user_json else None,
            planType=user_json["planType"] if "planType" in user_json else None,
            countryCode=user_json["countryCode"] if "countryCode" in user_json else None,
            country=user_json["country"] if "country" in user_json else None,
            timezone=user_json["timezone"] if "timezone" in user_json else "UTC",
            meetingInAMouth=user_json["meetingInAMouth"] if "meetingInAMouth" in user_json else 0,
            meetingTotal=user_json["meetingTotal"] if "meetingTotal" in user_json else 0,
            meetingMouth=user_json["meetingMouth"] if "meetingMouth" in user_json else None,
            nationalHoliday=user_json["nationalHoliday"] if "nationalHoliday" in user_json else None,
            isAccountDeactivated=user_json["isAccountDeactivated"] if "isAccountDeactivated" in user_json else None,
            isAccountLocked=user_json["isAccountLocked"] if "isAccountLocked" in user_json else None,
            planTypeIsActiveTill=user_json["planTypeIsActiveTill"] if "planTypeIsActiveTill" in user_json else None,
            firstModified=user_json["firstModified"] if "firstModified" in user_json else None,
            lastModified=user_json["lastModified"] if "lastModified" in user_json else None
        )

    def to_json(self):

        load = {}

        if self.id != None: load["id"] = self.id
        if self.firstName != None: load["firstName"] = self.firstName
        if self.lastName != None: load["lastName"] = self.lastName
        if self.companyName != None: load["companyName"] = self.companyName
        if self.title != None: load["title"] = self.title
        if self.email != None: load["email"] = self.email
        if self.phoneNumber != None: load["phoneNumber"] = self.phoneNumber
        if self.gender != None: load["gender"] = self.gender
        if self.dob != None: load["dob"] = self.dob
        if self.profilePicture != None: load["profilePicture"] = self.profilePicture
        if self.availableFrom != None: load["availableFrom"] = self.availableFrom    
        if self.availableTo != None: load["availableTo"] = self.availableTo
        if self.userType != None: load["userType"] = self.userType
        if self.planTypeIsActiveTill != None: load["planTypeIsActiveTill"] = self.planTypeIsActiveTill
        if self.workingDays != None: load["workingDays"] = self.workingDays
        if self.password != None: load["password"] = self.password
        if self.isEmailVerified != None: load["isEmailVerified"] = self.isEmailVerified
        if self.isPhoneVerified != None: load["isPhoneVerified"] = self.isPhoneVerified
        if self.isPublic != None: load["isPublic"] = self.isPublic
        if self.payload != None: load["payload"] = self.payload
        if self.planType != None: load["planType"] = self.planType
        if self.countryCode != None: load["countryCode"] = self.countryCode
        if self.country != None: load["country"] = self.country
        if self.timezone != None: load["timezone"] = self.timezone
        if self.meetingInAMouth != None: load["meetingInAMouth"] = self.meetingInAMouth
        if self.meetingTotal != None: load["meetingTotal"] = self.meetingTotal
        if self.meetingMouth != None: load["meetingMouth"] = self.meetingMouth
        if self.nationalHoliday != None: load["nationalHoliday"] = self.nationalHoliday
        if self.isAccountDeactivated != None: load["isAccountDeactivated"] = self.isAccountDeactivated
        if self.isAccountLocked != None: load["isAccountLocked"] = self.isAccountLocked
        if self.firstModified != None: load["firstModified"] = self.firstModified
        if self.lastModified != None: load["lastModified"] = self.lastModified
        
        return load

class SignUpModel(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName : Optional[str] = None
    title : Optional[str] = None
    userType: Optional[UserType] = UserType.USER
    email: str
    phoneNumber : Optional[str] = None
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
    emailOrPhoneNumber: str
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
    isPublic: Optional[bool] = True
    availableFrom: Optional[time] = None
    availableTo: Optional[time] = None
    workingDays : Optional[List[AvailableDays]] = [AvailableDays.MONDAY, AvailableDays.TUESDAY, AvailableDays.WEDNESDAY, AvailableDays.THRUSDAY, AvailableDays.FRIDAY]
    countryCode: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = "UTC"
    nationalHoliday: Optional[str] = None

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
        if self.isPublic != None: load["isPublic"] = self.isPublic
        if self.availableFrom != None: load["availableFrom"] = self.availableFrom    
        if self.availableTo != None: load["availableTo"] = self.availableTo
        if self.workingDays != None: load["workingDays"] = self.workingDays
        if self.countryCode != None: load["countryCode"] = self.countryCode
        if self.country != None: load["country"] = self.country
        if self.timezone != None: load["timezone"] = self.timezone
        if self.nationalHoliday != None: load["nationalHoliday"] = self.nationalHoliday
        return load


