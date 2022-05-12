import uuid
from fastapi import APIRouter, Header, Request
from dal.schedule import ScheduleModelDAL
from dal.whitelist import WhiteListModelDAL
from model.schedule import ScheduleModel, UpdateScheduleModel
from datetime import datetime

schedule_model_dal = ScheduleModelDAL()
whiteList_model_dal = WhiteListModelDAL()

router = APIRouter(
    prefix="/server/schedule",
    tags=["schedule"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create/multiple")
async def create(createSchedules: list[ScheduleModel], request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
    
    for createSchedule in createSchedules:
        if createSchedule.id == None:
            createSchedule.id = str(uuid.uuid4())
        createSchedule.userId = userId
        createSchedule.firstModified = str(datetime.now().isoformat())
        createSchedule.lastModified = str(datetime.now().isoformat())

    await schedule_model_dal.createMultiple(createSchedules)
    return {"message" : "successfully created schedule"}
    

@router.get("/find/my_schedules")
async def find_my_schedules(request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    scheduleQuery = {"userId" : userId}
    scheduleMessages = schedule_model_dal.read(query=scheduleQuery,page=page,limit=limit, sort=sort)
    scheduleDatas = ScheduleModel.to_json_list(scheduleMessages)
    return scheduleDatas

@router.get("/find/my_whitelist_schedules/{whiteListUserId}")
async def find_my_schedules(whiteListUserId: str, request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    
    # check if the user is whitelisted
    whiteListQuery = {"$or" : [{"partyA" : userId, "partyB" : whiteListUserId}, {"partyA" : whiteListUserId, "partyB" : userId}]}
    whiteListDatas = whiteList_model_dal.read(query=whiteListQuery, limit=1)
    if len(whiteListDatas) == 0:
        return {"message" : "you can not access this persons schedules"}

    scheduleQuery = {"userId" : whiteListUserId}
    scheduleMessages = schedule_model_dal.read(query=scheduleQuery,page=page,limit=limit, sort=sort)
    scheduleDatas = ScheduleModel.to_json_list(scheduleMessages)
    return scheduleDatas    

@router.put("/update/{scheduleId}")
async def update_meeting(updateSchedule: UpdateScheduleModel,scheduleId:str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]

    scheduleQuery = {"id" : scheduleId, "userId" : userId}
    schedule_model_dal.update(query=scheduleQuery, update_data=updateSchedule.to_json())
    return {"message" : "schedule successfully updated"}

@router.delete("/delete/{scheduleId}")
async def delete_meeting(scheduleId : str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
   
    scheduleQuery = {"id" : scheduleId, "userId" : userId}
    schedule_model_dal.delete(query=scheduleQuery)

    return {"message" : "schedule has been successfully deleted"}

