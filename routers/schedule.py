from typing import List
import uuid
from fastapi import APIRouter, Header, Request
from dal.schedule import ScheduleModelDAL
from dal.user import UserModelDAL
from dal.whitelist import WhiteListModelDAL
from lib.notifier import ConnectionManager
from model.meeting import MeetingModeModel
from model.schedule import ScheduleModel, UpdateScheduleModel, RequestAvailableTimeModel
from datetime import datetime
import phonenumbers

schedule_model_dal = ScheduleModelDAL()
whiteList_model_dal = WhiteListModelDAL()
user_model_dal = UserModelDAL()
connectionManager = ConnectionManager()


router = APIRouter(
    prefix="/server/schedule",
    tags=["schedule"],
    responses={404: {"description": "Not found"}},
)


def isMayBePhoneNumber(val):
    parsedPhoneNumber = None
    isPhoneNumber = False
    try:
        parsedPhoneNumber = phonenumbers.parse(val)
        isPhoneNumber = phonenumbers.is_valid_number(parsedPhoneNumber)
    except :
        return isPhoneNumber
    return isPhoneNumber

async def getAvailableTimeOfAttendee(attendee, fromDate, toDate):
    userQuery = {}

    if "@" in attendee:
        userQuery = {"email" : attendee}
    elif isMayBePhoneNumber(attendee):
        userQuery = {"phoneNumber" : attendee}
    else:
        userQuery = {"id" : attendee}

    userDatas = user_model_dal.read(query=userQuery, limit=1)
    if len(userDatas) == 0:
        return None
    userData = userDatas[0]

    schedule_query = {"$and" : [
        {"userId" : userData.id},
        {"toDate" : {"$lt" : toDate}},
        {"fromDate" : {"$gt" : fromDate}}
    ]}

    schedulesOfUser = schedule_model_dal.read(query=schedule_query, limit=1000)

    availableTimes = [{"fromDate" : fromDate, "toDate" : toDate}]
    for schedule in schedulesOfUser:
        fromDate = schedule.fromDate
        toDate = schedule.toDate
    
        for availableTime in availableTimes:
            print(availableTime)
            availableTimeFrom = availableTime["fromDate"]
            availableTimeTo = availableTime["toDate"]
         
            if str(fromDate) >= str(availableTimeFrom) and str(toDate) <= str(availableTimeTo):
                # print(availableTimes)
                newFreeTimeA = {"fromDate" : availableTimeFrom, "toDate" : fromDate}
                newFreeTimeB = {"fromDate" : toDate, "toDate" : availableTimeTo}
                availableTimes.remove(availableTime) # removing the old time
                if availableTimeFrom != fromDate:
                
                    availableTimes.append(newFreeTimeA)

                if toDate != availableTimeTo:    
                    
                    availableTimes.append(newFreeTimeB)
    
    
    return availableTimes

def getIntersectionDates(partyA, partyB):
    intersections = []
    for partyAF in partyA:
        for partyBF in partyB:
            if partyAF["fromDate"].isoformat() >= partyBF["fromDate"].isoformat() and partyAF["toDate"].isoformat() <= partyBF["toDate"].isoformat(): # found my intersection of times
                intersections.append(partyAF)

            elif partyBF["fromDate"] >= partyAF["fromDate"] and partyBF["toDate"] <= partyAF["toDate"]: # found my intersection of times
                intersections.append(partyBF)          

    return intersections

def getAllIntersection(parties):
    newParties = list(parties.values())

    while len(newParties) > 1:
        p1 = newParties[0]
        p2 = newParties[1]
     
        intersectionResults = getIntersectionDates(p1, p2)
        
        newParties.remove(p1)
        newParties.remove(p2)   
        newParties.append(intersectionResults)
 
    return newParties

@router.post("/create/multiple")
async def create_multiple(createSchedules: List[ScheduleModel], request:Request, token:str=Header(None)):
    userId = request.headers["userId"]

    for createSchedule in createSchedules:
        if createSchedule.id == None:
            createSchedule.id = str(uuid.uuid4())
        createSchedule.userId = userId
        if createSchedule.mode == None:
            createSchedule.mode = MeetingModeModel.virtual

        createSchedule.firstModified = datetime.now()
        createSchedule.lastModified = datetime.now()

    await schedule_model_dal.createMultiple(createSchedules)
    return {"message" : "successfully created schedule"}
    
@router.get("/find/my_schedules")
async def find_my_schedules(request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    scheduleQuery = {"userId" : userId}
    scheduleMessages = schedule_model_dal.read(query=scheduleQuery,page=page,limit=limit, sort=sort)
    scheduleDatas = ScheduleModel.to_json_list(scheduleMessages)
    return scheduleDatas

@router.post("/find/available_time")
async def find_available_time(requestAvailbableTime: RequestAvailableTimeModel, request:Request, token: str=Header(None)):
    availableTimes = {}
    for attendee in requestAvailbableTime.attendees:
        availableTimeForAttendee = await getAvailableTimeOfAttendee(attendee, requestAvailbableTime.fromDate, requestAvailbableTime.toDate)
        availableTimes[attendee] = availableTimeForAttendee

    intersections = getAllIntersection(availableTimes)
    
    availableTimes["intersections"] = intersections[0]
    return availableTimes

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
    if updateSchedule.mode == None:
        updateSchedule.mode = MeetingModeModel.virtual
        
    schedule_model_dal.update(query=scheduleQuery, update_data=updateSchedule.to_json())
    return {"message" : "schedule successfully updated"}

@router.delete("/delete/{scheduleId}")
async def delete_meeting(scheduleId : str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
   
    scheduleQuery = {"id" : scheduleId, "userId" : userId}
    schedule_model_dal.delete(query=scheduleQuery)

    return {"message" : "schedule has been successfully deleted"}

