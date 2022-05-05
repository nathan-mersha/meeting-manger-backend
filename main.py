from starlette.datastructures import MutableHeaders
import jwt
from datetime import datetime
from dateutil import parser
from dal.config import ConfigModelDAL
from dal.user import UserModelDAL
from routers import server_config, user, meeting
import configparser
import re
from model.server_config import ConfigModel
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
user_model_dal = UserModelDAL()
config_model_dal = ConfigModelDAL()

config = configparser.ConfigParser()
config.read("./cred/config.ini")

token_encrypter_secret = config["secrets"]["token_encrypter_secret"]
config_id = config["secrets"]["config_id"]

app.include_router(user.router)
app.include_router(server_config.router)
app.include_router(meeting.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def validate_token(request: Request, call_next):
    # list of exception routes where validate_token will not be called
    exception_routes = [
        "server/user/signup",
        "server/user/login",
        "server/user/forgot_password",
        "server/user/reset_password",
        "server/user/verify/email",
        "server/user/verify/phone_number",
        "server/user/request/verification/email",
        "server/user/request/verification/phone_number",
        "server/meeting/confirm_meeting/*",
        "docs",
        "openapi.json",
        "favicon.ico"
    ]
    route = str(request.url).replace(str(request.base_url),"")
    for exception_route in exception_routes:
        matches = re.findall(exception_route, route)
        if len(matches) > 0:
            response = await call_next(request)
            return response
   
    
    token = request.headers["token"]
    user_id = validate_token_and_get_user(token)
    if "token" in user_id:
        return JSONResponse(content={"message" : user_id}, status_code=401,)

    user_query = {"id" : user_id}
    user_data = user_model_dal.read(query=user_query)
    if len(user_data) == 0:
        return JSONResponse(content={"message" : "No user by token found"}, status_code=401,)

    first_user = user_data[0]
    if not first_user.isEmailVerified:
        return JSONResponse(content={"message" : "User email is not verified"}, status_code=400,)
    if first_user.isAccountDeactivated:
        return JSONResponse(content={"message" : "User account is deactivated"}, status_code=401,)
    if first_user.isAccountLocked:
        return JSONResponse(content={"message" : "User account is locked"}, status_code=401,)
       
    # attaching the userid on the request object
    new_header = MutableHeaders(request._headers)
    new_header["userId"] = str(user_id)
    request._headers = new_header
    request.scope.update(headers=request.headers.raw)
    response = await call_next(request)
    return response

@app.get("/server")
async def read_root():
    return {"Message": "This is meeting manager's backend by fast api, go to https://mmserver.ml/docs"}

@app.on_event("startup")
async def startup_event():
    # check if server oconfig exists else create new configuration
    await initialize_config()

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

    # todo : check if user is verified or not
    return user_id

async def initialize_config():
    print("initializing server config")
    config_query = {"id" : config_id}
    config_data = config_model_dal.read(query=config_query)
    if len(config_data) == 0:
        print("Config has not yet been created...")
        config_model = ConfigModel(
            id=config_id,
            tokenExpirationInDay=60
        )
        await config_model_dal.create(config_model=config_model)
        print("New default server config created")
        return
    print("Config data already exists")    