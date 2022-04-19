import hashlib
import uuid
import smtplib
import random

import jwt
from datetime import date,datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dal.user import UserModelDAL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Header
from model.user import LoginModel, UserModel, ForgotPasswordModel, ResetPasswordModel, ChangePasswordModel, UpdateUserModel
from fastapi.middleware.cors import CORSMiddleware

import json

app = FastAPI()
user_model_dal = UserModelDAL()
hash_256 = hashlib.sha256()
token_encrypter_secret = "jopavaeiva3ser223av21r233fascat890"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/server")
async def read_root():
    return {"Message": "This is meeting managers backend by fast api, go to https://mmserver.ml/docs"}

# user API's
@app.post("/server/user/signup")
async def sign_up_user(user: UserModel):

    # checking if user email does not already exists
    user_datas = user_model_dal.read({"email" : user.email})

    if len(user_datas) > 0:
        raise HTTPException(status_code=400, detail="user by that email already exists")

    # hash user password
    hashed_password = hashlib.sha256(str(user.password).encode('utf-8'))
    user.password = hashed_password.hexdigest()
    
    # create user id
    user.id = str(uuid.uuid4());

    # create user wallet id
    user.wallet_id = random.randint(1111111111, 9999999999)

    # create user
    await user_model_dal.create(user_model=user)
    message = "this is a welcome email from Generic wallet";
    send_email(user.email, message, "Welcome dude")
    
    return user.to_json()

@app.post("/server/user/login")
async def login_user(loginModel: LoginModel):
    
   # compare hash of password
    hashed_password = hashlib.sha256(str(loginModel.password).encode('utf-8')).hexdigest()
    user_query = {"email" : loginModel.email}
    users =  user_model_dal.read(query=user_query, limit=1)
    
    if len(users) == 0:
        return HTTPException(status_code=401, detail="email does not exist") 

    user = users[0] 
    if user.password != hashed_password:
        return HTTPException(status_code=401, detail="email and password do not match")
   
    # generate token
    after_six_months = date.today() + relativedelta(months=+6)
    encoded_jwt = jwt.encode({
        "id" : user.id,
        "expiration" : str(after_six_months)
    }, token_encrypter_secret, algorithm="HS256")

    return {
        "token" : str(encoded_jwt).replace("b'","").replace("'",""),
        "email" : user.email,
        "userId" : user.id
        
        }

@app.post("/server/user/forgot_password")
async def forgot_password(forgotModel: ForgotPasswordModel): 
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
    user_model_dal.update(user_query, update_data)
    send_email(user.email, "You have requested reset code", f"Your reset code is : {reset_code}")
    return {"message" : "your reset code has been sent"}

@app.get("/server/user/detail")
async def get_user_detail(token:str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

    user_query = {"id" : user_id}
    users = user_model_dal.read(query=user_query, limit=1)
    if len(users) == 0:
        return HTTPException(status_code=404, detail="user not found")
    return users[0]

@app.post("/server/user/reset_password")
async def reset_password(resetPassword: ResetPasswordModel):
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
    user_model_dal.update(user_query, update_data) # password successfuly updated and hashed
    
    # send email to user
    send_email(user.email, "Your password has been changed", "Your password has been changed, if this is not you then report here.")
    return {"message" : "your password has been changed"}

@app.post("/server/user/change_password")
async def change_password(changePassword: ChangePasswordModel, token: str = Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

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
    user_model_dal.update(user_query, update_data)

    send_email(user.email, "Your password has been changed", "Your password has been successfully changed")
    return {"message": "password successfully changed"}
    
@app.put("/server/user/update_profile")
async def update_profile(updateUser: UpdateUserModel, token: str=Header(None)):
    user_id = validate_token_and_get_user(token)    
    if "token" in user_id:
        return HTTPException(status_code=400, detail=user_id)

    user_query = {"id" : user_id}
    user_model_dal.update(user_query,updateUser.to_json())
    return {"message" : "user successfully updated"}

def validate_token_and_get_user(token):
    if token == None:
        return "no token provided"

    decoded_token_data = {}
    try:
        decoded_token_data = jwt.decode(token,token_encrypter_secret, algorithms="HS256")
    except Exception as e:
        return "token is corrupted"

    user_id = decoded_token_data["id"]
    expiration = parser.parse(decoded_token_data["expiration"])
    now = datetime.now()

    if expiration < now: # token expired
        return "token has expired"

    return user_id

def send_email(recipients, body, subject):
    try:
        message = MIMEMultipart()
        message['From'] = "nibjobs.com@gmail.com"
        message['To'] = recipients
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login("nibjobs.com@gmail.com", "nkyudfhgucciurcr") #login with mail_id and password
        text = message.as_string()
        session.sendmail("nibjobs.com@gmail.com", recipients, text)
        session.quit()

    except Exception as e:
        print(e)
        print("Error: unable to send email") 