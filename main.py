import configparser
import re
from datetime import datetime
import jwt
from dateutil import parser
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders

from dal.blocklist import BlockListModelDAL

from dal.config import ConfigModelDAL
from dal.group import GroupModelDAL
from dal.meeting import MeetingModelDAL
from dal.user import UserModelDAL
from dal.whitelist import WhiteListModelDAL
from dal.partner import PartnerModelDAL
from dal.schedule import ScheduleModelDAL
from model.server_config import ConfigModel
from routers import blocklist, schedule, contact_us, group, meeting, partner, server_config, user, whitelist, search

app = FastAPI()

blockList_model_dal = BlockListModelDAL()
partner_model_dal = PartnerModelDAL()
user_model_dal = UserModelDAL()
meeting_model_dal = MeetingModelDAL()
group_model_dal = GroupModelDAL()
white_list_model_dal = WhiteListModelDAL()
config_model_dal = ConfigModelDAL()
schedule_model_dal = ScheduleModelDAL()

config = configparser.ConfigParser()
config.read("./cred/config.ini")

token_encrypter_secret = config["secrets"]["token_encrypter_secret"]
config_id = config["secrets"]["config_id"]

app.include_router(user.router)
app.include_router(server_config.router)
app.include_router(meeting.router)
app.include_router(group.router)
app.include_router(contact_us.router)
app.include_router(partner.router)
app.include_router(whitelist.router)
app.include_router(blocklist.router)
app.include_router(search.router)
app.include_router(schedule.router)



@app.middleware("http")
async def validate_token(request: Request, call_next):
    # list of exception routes where validate_token will not be called
    exceptionRoutes = [
        "server/user/signup",
        "server/user/login",
        "server/user/forgot_password",
        "server/user/reset_password",
        "server/user/verify/email",
        "server/user/verify/phone_number",
        "server/user/request/verification/email",
        "server/user/request/verification/phone_number",
        "server/user/delete_for_debug",
        "server/meeting/confirm_meeting/*",
        "server/contactUs/create",
        "server/partner/respond_as_a_partner/*",
        "server/whitelist/request/*",
        "server/schedule/find/available_time",
        "docs",
        "openapi.json",
        "favicon.ico"
    ]
    route = str(request.url).replace(str(request.base_url),"")
    
    for exception_route in exceptionRoutes:
        matches = re.findall(exception_route, route)
        if len(matches) > 0:
            response = await call_next(request)
            return response

    token = None

    try:
        token = request.headers["token"]
    except:
        return JSONResponse(content={"message" : "no token provided"}, status_code=401,)

    print(f"token is : {token}")
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
    print("New headers .... ")
    print(str(request._headers))
    request.scope.update(headers=request.headers.raw)
    response = await call_next(request)
    return response

@app.get("/server")
async def read_root():
    return {"Message": "This is meeting manager's backend by fast api, go to https://mmserver.ml/docs"}

# @app.on_event("startup")
# async def startup_event():
#     await initialize_config()
#     await create_indexes()

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

async def create_indexes():
    print("Creating indexes ...")
    await blockList_model_dal.create_index()
    await group_model_dal.create_index()
    await meeting_model_dal.create_index()
    await partner_model_dal.create_index()
    await schedule_model_dal.create_index()
    await user_model_dal.create_index()
    await white_list_model_dal.create_index()
    
async def initialize_config():
    print("initializing server config")
    
    config_data = config_model_dal.read()
    if config_data == None:
        print("Config has not yet been created...")
        pricingPlan = {
            "basic" : {
                "name" : "basic",
                "description" : "basic package",
                "allowedNoOfActiveMeetings" : 10,
                "allowedNoOfAttendees" : 3,
                "monthlyPrice" : 0,
                "yearlyPrice" : 0
            },
            "premium" : {
                "name" : "premium",
                "description" : "premium package",
                "allowedNoOfActiveMeetings" : 100,
                "allowedNoOfAttendees" : 30,
                "monthlyPrice" : 10,
                "yearlyPrice" : 100
            },
            "vip" : {
                "name" : "vip",
                "description" : "vip package",
                "allowedNoOfActiveMeetings" : 1000,
                "allowedNoOfAttendees" : 300,
                "monthlyPrice" : 100,
                "yearlyPrice" : 1000
            }
        }
        config_model = ConfigModel(
            id=config_id,
            tokenExpirationInDay=60,
            pricingPlan = pricingPlan,
            promoPeriod = 0

        )
        await config_model_dal.create(config_model=config_model)
        print("New default server config created")
        return
    print("Config data already exists")    
