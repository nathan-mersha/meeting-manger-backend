import configparser
import hashlib
import random
import uuid
import jwt
from datetime import date
from dal.user import UserModelDAL
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, File, Header, HTTPException, Request, BackgroundTasks
from lib.email import Emails
from lib.sms import SMS
from model.user import (ChangePasswordModel, ForgotPasswordModel, LoginModel,
                        RequestVerificationEmail,
                        RequestVerificationPhoneNumber, ResetPasswordModel,
                        SignUpModel, UpdateUserModel, UserModel, UserType,
                        VerifyEmailModel, VerifyPhoneNumberModel)

from pydantic import BaseModel, ValidationError

user_model_dal = UserModelDAL()
hash_256 = hashlib.sha256()
sms = SMS()
config = configparser.ConfigParser()
config.read("./cred/config.ini")

token_encrypter_secret = config["secrets"]["token_encrypter_secret"]
file_upload_path = config["file"]["file_upload_path"]

router = APIRouter(
    prefix="/server/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

# user API's
@router.post("/signup")
async def sign_up_user(signUpData: SignUpModel, background_tasks: BackgroundTasks):
    # checking if user email does not already exists
    user_datas = user_model_dal.read({"email" : signUpData.email})

    if len(user_datas) > 0:
        raise HTTPException(status_code=400, detail="user by that email already exists")

    if signUpData.phoneNumber != None:
        user_phone_query =  {"phoneNumber" : signUpData.phoneNumber}
        user_datas_phone = user_model_dal.read(user_phone_query,limit=1)
        if len(user_datas_phone) > 0:
            raise HTTPException(status_code=400, detail="user by that phone number already exists") 

    user = None
    try:
        user = UserModel(
        firstName = signUpData.firstName,
        lastName = signUpData.lastName,
        companyName = signUpData.companyName,
        title = signUpData.title,
        email = signUpData.email,
        password = signUpData.password,
        phoneNumber = signUpData.phoneNumber,
        isEmailVerified = False,
        isPhoneVerified = False
        )
    except ValidationError as e:
        return HTTPException(status_code=400, detail=str(e))    

    # hash user password
    hashed_password = hashlib.sha256(str(user.password).encode('utf-8'))
    user.password = hashed_password.hexdigest()
    
    # create user id
    user.id = str(uuid.uuid4())
    user.planType = "basic"

    emailVerification = str(random.randint(111111,999999))
    phoneVerification = str(random.randint(111111,999999))
    user.payload = {
        "emailVerification" : emailVerification,
        "phoneNumberVerification" : phoneVerification
    }
    # create user
    await user_model_dal.create(user_model=user)
    email_body = f"Welcome to Arrange Meeting \n your verification code is {emailVerification}"
    email_head = "This is a welcome email from Arrange Meeting";
    background_tasks.add_task(Emails.send_email, user.email, email_body, email_head)
    # Emails.send_email(user.email, email_body, email_head)
    
    # send verification for phone number
    if user.phoneNumber != None:
        message = f"Your Arrange meeting verification code is : {phoneVerification}"
        # sms.send(to=user.phoneNumber, message=message)
        background_tasks.add_task(sms.send, user.phoneNumber, message)
        print(f"SMS verification message : {message}")

    # remove password
    user.password = None
    return user.to_json()

@router.post("/verify/email")
async def verifiy_email(verifyEmail: VerifyEmailModel, background_tasks: BackgroundTasks):
    user_query = {"email" : verifyEmail.email}
    users =  user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email does not exist") 
    user = users[0]
    if user.payload["emailVerification"] != verifyEmail.verificationCode:
        return HTTPException(status_code=401, detail="Email verification is not correct")

    user.isEmailVerified = True
    user_model_dal.update(query=user_query, update_data=user.to_json())

    email_body = "Your email is verified"
    email_head = "Your email is verified"
    background_tasks.add_task(Emails.send_email, user.email, email_body, email_head)
    
    # generate token
    after_six_months = date.today() + relativedelta(months=+6)
    encoded_jwt = jwt.encode({
        "id" : user.id,
        "expiration" : str(after_six_months)
    }, token_encrypter_secret, algorithm="HS256")

    return {
        "message" : "user email verified",
        "token" : str(encoded_jwt).replace("b'","").replace("'",""), 
        "userId" : user.id,
        "email" : user.email
        }

@router.post("/verify/phone_number")
async def verifiy_phoneNumber(verifyPhoneNumber: VerifyPhoneNumberModel, background_tasks: BackgroundTasks):
    user_query = {"phoneNumber" : verifyPhoneNumber.phoneNumber}
    users =  user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="Phone number does not exist") 
    user = users[0]
    if user.payload["phoneNumberVerification"] != verifyPhoneNumber.verificationCode:
        return HTTPException(status_code=401, detail="Phone number verification is not correct")

    user.isPhoneVerified = True
    user_model_dal.update(query=user_query, update_data=user.to_json())

    email_body = "Your phone number is verified"
    email_head = "Your phone number is verified"
    background_tasks.add_task(Emails.send_email, user.email, email_body, email_head)
    return {"message" : "user phone number verified"}

@router.post("/request/verification/email")
async def request_email_verification_code(requestVerificationEmail: RequestVerificationEmail, background_tasks: BackgroundTasks):
    user_query = {"email" : requestVerificationEmail.email}
    users =  user_model_dal.read(query=user_query, limit=1)
    
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email does not exist") 
    user = users[0]

    if user.isEmailVerified:
        return HTTPException(status_code=401, detail="email already verified") 

    emailVerification = str(random.randint(111111,999999))
    update_data = {"payload" : {"emailVerification" : emailVerification}}
    
    # update the user
    user_model_dal.update(query=user_query, update_data=update_data)
    
    email_body = f"Your email verification code is {emailVerification}"
    email_head = "Verification Code";
    background_tasks.add_task(Emails.send_email, user.email, email_body, email_head)
    return {"message" : "verification code sent via email"}

@router.post("/request/verification/phone_number")
async def request_phone_number_verification_code(requestVerificationPhoneNumber: RequestVerificationPhoneNumber, background_tasks : BackgroundTasks):
    user_query = {"phoneNumber" : requestVerificationPhoneNumber.phoneNumber}
    users =  user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="phone number does not exist") 
    user = users[0]
    if user.isPhoneVerified:
        return HTTPException(status_code=400, detail="phone number already verified") 

    phoneNumberVerification = str(random.randint(111111,999999))
    existing_payload = user.payload
    existing_payload["phoneNumberVerification"] = phoneNumberVerification
    update_data = {"payload" : existing_payload}
    
    # update the user
    user_model_dal.update(query=user_query, update_data=update_data)
    
    # sending sms
    to = user.phoneNumber
    message = f"Your Arrange verification code is : {phoneNumberVerification}"
    background_tasks.add_task(sms.send, to, message)

    # todo : send twillio sms here
    return {"message" : "verification code sent via phone number"}

@router.post("/login")
async def login_user(loginModel: LoginModel):
   # compare hash of password
    hashed_password = hashlib.sha256(str(loginModel.password).encode('utf-8')).hexdigest()
    user_query = {"email" : loginModel.emailOrPhoneNumber}

    if "@" in loginModel.emailOrPhoneNumber:
        user_query = {"email" : loginModel.emailOrPhoneNumber}
    else:
        user_query = {"phoneNumber" : loginModel.emailOrPhoneNumber}

    users =  user_model_dal.read(query=user_query, limit=1)
    
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email/phoneNumber does not exist") 

    user = users[0]
    # user cant login if it has not verified email and password

    if not user.isEmailVerified:
        return HTTPException(status_code=401, detail = "user needs to verifiy email")

    if (user.phoneNumber != None and str(user.phoneNumber).strip() != "" ) and not user.isPhoneVerified:
        return HTTPException(status_code=401, detail = "user needs to verify phone number")

    if user.password != hashed_password:
        return HTTPException(status_code=401, detail="email/phoneNumber and password do not match")
   
    # generate token
    after_six_months = date.today() + relativedelta(months=+6)
    encoded_jwt = jwt.encode({
        "id" : user.id,
        "expiration" : str(after_six_months)
    }, token_encrypter_secret, algorithm="HS256")

    user.password = None
    return {
        "token" : str(encoded_jwt).replace("b'","").replace("'",""),
        "email" : user.email,
        "user" : user.to_json()
    }

@router.post("/forgot_password")
async def forgot_password(forgotModel: ForgotPasswordModel, background_tasks: BackgroundTasks): 
    user_email = forgotModel.email
    reset_code = random.randint(111111, 999999)
    user_query = {"email" : user_email}
    users =  user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email does not exist") 
    user = users[0]
    user_payload = user.payload
    user_payload["resetCode"] = reset_code
    update_data = { 'payload': user_payload}
    # update user here
    user_model_dal.update(query=user_query, update_data=update_data)

    email_body = f"Your reset code is : {reset_code}"
    email_head = "You have requested reset code"
    background_tasks.add_task(Emails.send_email, user.email, email_body, email_head)
    
    return {"message" : "your reset code has been sent"}

@router.get("/detail")
async def get_user_detail(request:Request, token:str=Header(None)):
    user_id = request.headers["userId"]
    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=404, detail="user not found")
    return users[0]

@router.get("/all")
async def get_all_users(token:str=Header(None), page:int=1, limit:int=12,sort="firstModified"):
    userData = user_model_dal.read(query={}, page=page, limit=limit, sort=sort)
    return userData

@router.post("/reset_password")
async def reset_password(resetPassword: ResetPasswordModel, background_tasks: BackgroundTasks):
    # check if the reset code is correct
    user_query = {"email" : resetPassword.email}
    
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=400, detail="user by email not found")

    user = users[0]
    user_payload = user.payload

    if str(user_payload["resetCode"]) != str(resetPassword.reset_code):
        return HTTPException(status_code=401, detail="reset code is not correct")

    new_hashed_password = hashlib.sha256(str(resetPassword.new_password).encode('utf-8')).hexdigest()
    update_data = {'password' : new_hashed_password}
    user_model_dal.update(query=user_query, update_data=update_data) # password successfuly updated and hashed
    
    # send email to user
    email_body = "Your password has been changed, if this is not you then report here."
    email_head = "Your password has been changed"
    background_tasks.add_task(Emails.send_email, user.email,email_body, email_head)
    return {"message" : "your password has been changed"}

@router.post("/change_password")
async def change_password(request:Request, changePassword: ChangePasswordModel, background_tasks: BackgroundTasks, token: str = Header(None)):
    user_id = request.headers["userId"]    
   
    hashed_incomming_old_password = hashlib.sha256(str(changePassword.old_password).encode('utf-8')).hexdigest()
    user_query = {"id": user_id}

    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")

    user = users[0]
    if user.password != hashed_incomming_old_password:
        return HTTPException(status_code=400, detail="user old password is not correct")

    hashed_new_password = hashlib.sha256(str(changePassword.new_password).encode('utf-8')).hexdigest()
    update_data = {'password' : hashed_new_password}
    user_model_dal.update(query=user_query, update_data=update_data)

    email_body = "Your password has been changed"
    email_head = "Your password has been successfully changed"
    background_tasks.add_task(Emails.send_email, user.email, email_body, email_head)
    return {"message": "password successfully changed"}
    
@router.put("/update_profile")
async def update_profile(request:Request, updateUser: UpdateUserModel,background_tasks:BackgroundTasks, token: str=Header(None) ):
    user_id = request.headers["userId"]    
    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")

    user = users[0]
    updatedDataJSON = updateUser.to_json()

    payload = {}
    if updateUser.email != None and user.email != updateUser.email: # new email has been updated        
        updatedDataJSON["isEmailVerified"] = False
        emailVerification = str(random.randint(111111,999999))
        payload["emailVerification"] = emailVerification
        email_body = f"your verification code is {emailVerification}"
        email_title = f"your verificaion code is {emailVerification}"
        background_tasks.add_task(Emails.send_email, updateUser.email, email_body, email_title)

    if updateUser.phoneNumber != None and user.phoneNumber != updateUser.phoneNumber: # new email has been updated        
        updatedDataJSON["isPhoneVerified"] = False
        phoneVerification = str(random.randint(111111,999999))
        payload["phoneNumberVerification"] = phoneVerification
        txt_message = f"Your verification code is : {phoneVerification}"
        background_tasks.add_task(sms.send, updateUser.phoneNumber, txt_message)
        # todo send verification code via twillio

    
    updatedDataJSON["payload"] = payload
    user_model_dal.update(query=user_query,update_data=updatedDataJSON)
    return {"message" : "user successfully updated"}

@router.post("/uploadfile")
async def upload_file(file: bytes=File(...), token:str=Header(None)):
    name = f"{str(uuid.uuid4())}.jpg"
    fileName = f"{file_upload_path}/{name}"
    with open(fileName,'wb') as image:
        image.write(file)
        image.close()

    
    return {"filePath" : f"https://mmserver.ml/images/{name}"}
# get users with pagination
# delete users


@router.post("/admin/create")
async def create_user(request:Request,userModel: UserModel,background_tasks: BackgroundTasks,token: str=Header(None)):
    validate=await validate_permission(request)
    if(not validate):
       return HTTPException(status_code=401, detail="permission denied")
    
    # checking if user email does not already exists
    user_datas = user_model_dal.read({"email" : userModel.email})
    plan_password=userModel.password
    if len(user_datas) > 0:
        raise HTTPException(status_code=400, detail="user by that email already exists")

    if userModel.phoneNumber != None:
        user_phone_query =  {"phoneNumber" : userModel.phoneNumber}
        user_datas_phone = user_model_dal.read(user_phone_query,limit=1)
        if len(user_datas_phone) > 0:
            raise HTTPException(status_code=400, detail="user by that phone number already exists") 

    # hash user password
    hashed_password = hashlib.sha256(str(userModel.password).encode('utf-8'))
    userModel.password = hashed_password.hexdigest()
    
    # create user id
    userModel.id = str(uuid.uuid4())
    # create user
    await user_model_dal.create(user_model=userModel)
    email_body = f"Welcome to Arrange Meeting \n your password is {plan_password} please change your password"
    email_head = "This is a welcome email from Arrange Meeting";
    background_tasks.add_task(Emails.send_email, userModel.email, email_body, email_head)
    
    return userModel.to_json()



@router.put("/admin/update_user/{id}")
async def update_user(request:Request,id:str,updateUser: UpdateUserModel,background_tasks:BackgroundTasks, token: str=Header(None) ):
    validate=await validate_permission(request)
    if(not validate):
       return HTTPException(status_code=401, detail="permission denied")

    user_id = id    
    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")

    updatedDataJSON = updateUser.to_json()
    user_model_dal.update(query=user_query,update_data=updatedDataJSON)
    return {"message" : "user successfully updated"}


class deactivatedUserModel(BaseModel):
    id : str
    isAccountDeactivated: bool
    def to_json(self):
        load = {}
        if self.id != None: load["id"] = self.id
        if self.isAccountDeactivated != None: load["isAccountDeactivated"] = self.isAccountDeactivated
        return load
@router.put("/admin/changeUserAccountStatus")
async def change_user_account_status(request:Request,deactivatedUser: deactivatedUserModel,background_tasks:BackgroundTasks, token: str=Header(None) ):
    validate=await validate_permission(request)
    if(not validate):
       return HTTPException(status_code=401, detail="permission denied")
    user_id = deactivatedUser.id    
    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")
    updatedDataJSON = deactivatedUser.to_json()
    user_model_dal.update(query=user_query,update_data=updatedDataJSON)
    if(not deactivatedUser.isAccountDeactivated):
        return {"message" : "user activated successfully"}
    
    return {"message" : "user deactivated successfully"}

class ChangeUserType(BaseModel):
    id : str
    userType: UserType

async def validate_permission(request: Request):
    user_id = request.headers["userId"]    
    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    print(users,UserType.ADMINISTRATOR)
    if len(users) == 0:
        return False
    elif users[0].userType != UserType.ADMINISTRATOR:
        return False
    return True

@router.put("/admin/changeUserAccountType")
async def change_user_account_status(request:Request,changeUserType: ChangeUserType,background_tasks:BackgroundTasks, token: str=Header(None) ):
    validate=await validate_permission(request)
    if(not validate):
       return HTTPException(status_code=401, detail="permission denied")
    user_id = changeUserType.id    
    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=401, detail="user does not exist")
    updatedDataJSON={}
    updatedDataJSON["userType"] = changeUserType.userType
    user_model_dal.update(query=user_query,update_data=updatedDataJSON)
    
    return {"message" : "user type changed successfully"}

class DeleteUserModel(BaseModel):
    email : str

@router.delete("/delete_for_debug")
async def delete_user_for_debug(deleteUserModel:DeleteUserModel):
    user_model_dal.delete(query={"email" : deleteUserModel.email})
    return {"message" : f"user {deleteUserModel.email} deleted"}
