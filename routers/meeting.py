from datetime import datetime
from http.client import HTTPException
from pickle import NONE
from random import random
import hashlib
from fastapi import APIRouter, Header, Request, BackgroundTasks
import uuid
from dal.config import ConfigModelDAL
from dal.meeting import MeetingModelDAL
from dal.user import UserModelDAL
from lib.notifier import ConnectionManager
from lib.shared import SharedFuncs
from lib.sms import SMS
from model.server_config import ConfigModel
from model.user import UserModel
from model.meeting import MeetingAttendeStatus, MeetingAttendees, MeetingModel, UpdateAttendee, UpdateAttendeeActions, UpdateMeetingModel
from model.schedule import ScheduleModel
from dal.schedule import ScheduleModelDAL
from lib.email import Emails
import phonenumbers
import random

connectionManager = ConnectionManager()
meeting_model_dal = MeetingModelDAL()
user_model_dal = UserModelDAL()
schedule_model_dal = ScheduleModelDAL()
config_model_dal = ConfigModelDAL()

sms = SMS()
sharedFuncs = SharedFuncs()
hash_256 = hashlib.sha256()

router = APIRouter(
    prefix="/server/meeting",
    tags=["meeting"],
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

@router.post("/create")
async def create(createMeeting: MeetingModel,request:Request,background_tasks:BackgroundTasks, token:str=Header(None)):
    user_id = request.headers["userId"]
    createMeeting.id = str(uuid.uuid4())
    createMeeting.host = user_id
    editedAttendees = []
    user_query = {"id" : user_id}
    user_datas = user_model_dal.read(query=user_query,limit=1)
    if len(user_datas) == 0:
        return HTTPException(status_code=400, detail="host by id not found")
    host_data = user_datas[0]
    createMeeting.hostName = host_data.firstName + " " + host_data.lastName
    #checking pricing plan
    serverConfig = config_model_dal.read()
    allowedNoOfAttendeesForHostsPlan = serverConfig.pricingPlan[host_data.planType]["allowedNoOfAttendees"]
    
    if int(allowedNoOfAttendeesForHostsPlan) < len(createMeeting.attendees):
        return {"message" : f"user can only create {allowedNoOfAttendeesForHostsPlan} hosts with {host_data.planType} plan type."}

    
    for meetingAttendee in createMeeting.attendees:
        attendeeUserQuery = {}
        isUserBlocked = False
        
        if "@" in meetingAttendee:
            attendeeUserQuery = {"email" : meetingAttendee}
        else:
            attendeeUserQuery = {"id" : meetingAttendee}    
            isUserBlocked = sharedFuncs.isUserBlocked(user_id, meetingAttendee)
        
        if isUserBlocked:
            continue

        attendeeDatas = user_model_dal.read(query=attendeeUserQuery, limit=1)
        parsedPhoneNumber = None
        isPhoneNumber = None
        try:
            parsedPhoneNumber = phonenumbers.parse(meetingAttendee)
            isPhoneNumber = phonenumbers.is_valid_number(parsedPhoneNumber)
        except :
            pass    

        
        if len(attendeeDatas) == 0 and "@" in meetingAttendee: # user is new and here by invitation by email
            randomPasswordForNewUser = str(random.randint(111111,999999))
            hashed_password = hashlib.sha256(str(randomPasswordForNewUser).encode('utf-8'))
            
            newAttendeeUserId = str(uuid.uuid4())
            newUserData = UserModel(
                id = newAttendeeUserId,
                email = meetingAttendee,
                password = hashed_password.hexdigest()
            )

            await user_model_dal.create(newUserData)

            
            ma = MeetingAttendees(
                id = str(uuid.uuid4()),
                userId=newAttendeeUserId,
                email=meetingAttendee,
                status=MeetingAttendeStatus.pending
            )
            editedAttendees.append(ma.to_json())

            # send email
            email_head = "You have been invited to attend a meeting"
            email_body = f'''
            Hello,
            You have been invited to attend a meeting by {host_data.firstName}
            Meeting title : {createMeeting.title}
            Meeting description : {createMeeting.description}
            Attendees : {len(createMeeting.attendees)}
            Date : {createMeeting.fromDate}
            Note : {createMeeting.note}
            Meeting Link : {createMeeting.meetingLink}
            Login Password is : {str(randomPasswordForNewUser)}
            Are you comming ?
            Yes I am comming (twss) -> click here https://mmserver.ml/server/meeting/confirm_meeting/new_invite/{createMeeting.id}/{newAttendeeUserId}/accept
            No am not comming -> click here https://mmserver.ml/server/meeting/confirm_meeting/new_invite/{createMeeting.id}/{newAttendeeUserId}/reject
            '''
            background_tasks.add_task(Emails.send_email,meetingAttendee, email_body, email_head)
        
        elif len(attendeeDatas) == 0 and isPhoneNumber: # user is new and is invited by phonenumber
            randomPasswordForNewUser = str(random.randint(111111,999999))
            hashed_password = hashlib.sha256(str(randomPasswordForNewUser).encode('utf-8'))
            newAttendeeUserId = str(uuid.uuid4())
            newUserData = UserModel(
                id = newAttendeeUserId,
                phoneNumber = meetingAttendee,
                email="no@email",
                password = hashed_password.hexdigest()
            )

            await user_model_dal.create(newUserData)

            
            ma = MeetingAttendees(
                id = str(uuid.uuid4()),
                userId=newAttendeeUserId,
                phoneNumber=meetingAttendee,
                email="no@email",
                status=MeetingAttendeStatus.pending
            )
            editedAttendees.append(ma.to_json())

            smsMessage = f"Request to join a meeting below link to procceed. https://mmclient.ml/completeProfile/{meetingAttendee} your password is {randomPasswordForNewUser}"
            background_tasks.add_task(sms.send,meetingAttendee, smsMessage)
        else:
            attendeeUser = attendeeDatas[0]
            ma = MeetingAttendees(
                id = str(uuid.uuid4()),
                userId=attendeeUser.id,
                email=attendeeUser.email,
                status=MeetingAttendeStatus.pending
            )
            editedAttendees.append(ma.to_json())
            # send email
            email_head = f"Request meeting from {host_data.firstName}"
            email_body = f'''
                Meeting title : {createMeeting.title}
                Meeting description : {createMeeting.description}
                Attendees : {len(createMeeting.attendees)}
                Date : {createMeeting.fromDate}
                Note : {createMeeting.note}
                Meeting Link : {createMeeting.meetingLink}
                Are you comming ?
                Yes I am comming (twss) -> click here https://mmserver.ml/server/meeting/confirm_meeting/{createMeeting.id}/{attendeeUser.id}/accept
                No am not comming -> click here https://mmserver.ml/server/meeting/confirm_meeting/{createMeeting.id}/{attendeeUser.id}/reject
            '''
            background_tasks.add_task(Emails.send_email, attendeeUser.email, email_body, email_head)

            if attendeeUser.phoneNumber != None:
                sms_message = f"You have been invited to join a meeting from {host_data.firstName}. Check your email for more"
                background_tasks.add_task(sms.send, attendeeUser.phoneNumber, sms_message)

    createMeeting.attendees = MeetingAttendees.to_model_list(editedAttendees)
    
    meeting_data = await meeting_model_dal.create(meeting_model=createMeeting)
   
    if not meeting_data.acknowledged:
        return {"message" : "something went wrong while creating meeting"}

    # todo notify attendees via email about the created meeting
    user_query = {"id" : user_id}
    if(host_data.meetingMouth==f"{datetime.now().month}/{datetime.now().year}"):
       host_data.meetingInAMouth=host_data.meetingInAMouth+1;
    else:
        host_data.meetingInAMouth=1;
        host_data.meetingMouth=f"{datetime.now().month}/{datetime.now().year}";
    host_data.meetingTotal=host_data.meetingInAMouth+1;
    user_model_dal.update(query=user_query,update_data=host_data.to_json())
    message = {
                    "userId" : user_id,
                    "message" : "creating schedule",
                    }
                #json.dumps(message)
    res_from_sock = await connectionManager.send_personal_message(message,user_id)
    return {"message" : "meeting successfully created"} 

@router.get("/confirm_meeting/{meetingId}/{userId}/{status}")
async def confirm_meeting(meetingId: str,userId: str, status: MeetingAttendeStatus, background_tasks: BackgroundTasks):
    if status == MeetingAttendeStatus.pending:
        return {"message" : "meeting status is pending by default"}

    meetingQuery = {"id" : meetingId}
    meetingDatas = meeting_model_dal.read(query=meetingQuery, limit=1)
    if len(meetingDatas) == 0:
        return {"message" : "meeting not found"}

    meetingData = meetingDatas[0]
    for attendee in meetingData.attendees:
        print(f"looping for users : {attendee}")
        if attendee.userId == userId:
            attendee.status = status
            print(f"fstatus is : {status}")
            if status == MeetingAttendeStatus.accept:
                print("status is accept")
                # create new schedule for user
                scheduleData = ScheduleModel(
                    id = str(uuid.uuid4()),
                    userId = attendee.userId,
                    fromDate = meetingData.fromDate,
                    toDate = meetingData.toDate,
                    title = meetingData.title,
                    note = meetingData.note,
                    mode = meetingData.mode
                )
                print("creating schedule")
                await schedule_model_dal.create(scheduleData)
                message = {
                    "userId" : attendee.userId,
                    "message" : "creating schedule",
                    }
                #json.dumps(message)
                res_from_sock = await connectionManager.send_personal_message(message,attendee.userId)
                continue
   
    meetingUpdateData = {"attendees" : MeetingAttendees.to_json_list(meetingData.attendees)}
    meeting_model_dal.update(query=meetingQuery, update_data=meetingUpdateData)

    # query host
    host_query = {"id" : meetingData.host}
    host_datas = user_model_dal.read(query=host_query, limit=1)
    if len(host_datas) == 0:
        return {"message" : f"host not found"}
    host_data = host_datas[0]
    
    # query attendee
    attendee_query = {"id" : userId}
    attendee_datas = user_model_dal.read(query=attendee_query, limit=1)
    if len(attendee_datas) == 0:
        return {"message" : f"attendee not found"}
    attendee_data = attendee_datas[0]

    # send email for host
    host_email_head = f"{attendee_data.firstName} has {status} your invitation"
    host_email_body = f'''
        {attendee_data.firstName} has {status} your invitation
        Meeting title : {meetingData.title}
            Meeting description : {meetingData.description}
            Attendees : {len(meetingData.attendees)}
            Date : {meetingData.fromDate}
            Note : {meetingData.note}
            Meeting Link : {meetingData.meetingLink}
    '''   
    background_tasks.add_task(Emails.send_email,host_data.email, host_email_body, host_email_head)

    # send email for attendee
    attendee_email_head = f"You have {status} meeting of {host_data.firstName}"
    attendee_email_body = f'''
        You have {status} meeting of {host_data.firstName}
        Meeting title : {meetingData.title}
            Meeting description : {meetingData.description}
            Attendees : {len(meetingData.attendees)}
            Date : {meetingData.fromDate}
            Note : {meetingData.note}
            Meeting Link : {meetingData.meetingLink}
    ''' 
    background_tasks.add_task(Emails.send_email, attendee_data.email, attendee_email_body, attendee_email_head)
    return {"message" : f"meeting {status}"}

@router.get("/confirm_meeting/new_invite/{meetingId}/{userId}/{status}")
async def confirm_meeting(meetingId: str,userId: str, status: MeetingAttendeStatus, background_tasks: BackgroundTasks):

    # if the new invite is clicked then the user has verified it's email address
    newUserQuery = {"id" : userId}
    newUserUpdateData = {"isEmailVerified" : True}
    user_model_dal.update(query=newUserQuery, update_data=newUserUpdateData)

    meetingQuery = {"id" : meetingId}

    meetingDatas = meeting_model_dal.read(query=meetingQuery, limit=1)
    if len(meetingDatas) == 0:
        return {"message" : "meeting not found"}

    meetingData = meetingDatas[0]
    for attendee in meetingData.attendees:
        if attendee.userId == userId:
            attendee.status = status
            continue
   
    meetingUpdateData = {"attendees" : MeetingAttendees.to_json_list(meetingData.attendees)}
    meeting_model_dal.update(query=meetingQuery, update_data=meetingUpdateData)

    # query host
    host_query = {"id" : meetingData.host}
    host_datas = user_model_dal.read(query=host_query, limit=1)
    if len(host_datas) == 0:
        return {"message" : f"host not found"}
    host_data = host_datas[0]
    
    # query attendee
    attendee_query = {"id" : userId}
    attendee_datas = user_model_dal.read(query=attendee_query, limit=1)
    if len(attendee_datas) == 0:
        return {"message" : f"attendee not found"}
    attendee_data = attendee_datas[0]

    # send email for host
    host_email_head = f"{attendee_data.firstName} has {status} your invitation"
    host_email_body = f'''
        {attendee_data.firstName} has {status} your invitation
        Meeting title : {meetingData.title}
            Meeting description : {meetingData.description}
            Attendees : {len(meetingData.attendees)}
            Date : {meetingData.fromDate}
            Note : {meetingData.note}
            Meeting Link : {meetingData.meetingLink}
    '''   
    background_tasks.add_task(Emails.send_email,host_data.email, host_email_body, host_email_head)

    # send email for attendee
    attendee_email_head = f"You have {status} meeting of {host_data.firstName}"
    attendee_email_body = f'''
        You have {status} meeting of {host_data.firstName}
        Meeting title : {meetingData.title}
            Meeting description : {meetingData.description}
            Attendees : {len(meetingData.attendees)}
            Date : {meetingData.fromDate}
            Note : {meetingData.note}
            Meeting Link : {meetingData.meetingLink}
    ''' 
    background_tasks.add_task(Emails.send_email, attendee_data.email, attendee_email_body, attendee_email_head)
    return {"message" : f"meeting {status}"}

@router.get("/find/mymeetings/all")
async def get_meetings_hosted(request:Request,page:int=1,populate:str="true",limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]

    hosted_query = {"$or" : [
        {"host" : userId},
        {"attendees" : {"$elemMatch" : {"userId" : userId}}}
    ]}
    hostedMeetings = meeting_model_dal.read(hosted_query,page=page,limit=limit, sort=sort)
    
    if populate == "true":
        for hostedMeeting in hostedMeetings:
            for attendee in hostedMeeting.attendees:
                attendee_query = {"id" : attendee.userId}
                if "@" in attendee.userId:
                    attendee_query = {"email" : attendee.userId}
                elif  isMayBePhoneNumber(attendee.userId):
                    attendee_query = {"phoneNumber" : attendee.userId}

                attendeeDatas = user_model_dal.read(query=attendee_query, limit=1, select={"id" : 1, "firstName" : 1, "lastName" : 1, "companyName" : 1, "title" : 1, "email" : 1, "phoneNumber" : 1, "gender" : 1, "email" : 1, "profilePicture" : 1})
                if len(attendeeDatas) == 0:
                    hostedMeeting.attendees.remove(attendee)
                    continue
                attendeeData = attendeeDatas[0]
                attendee.userId = attendeeData    

    meetingDatas = MeetingModel.to_json_list(hostedMeetings)
    return meetingDatas

@router.get("/find/mymeetings/hosted")
async def get_meetings_hosted(request:Request,page:int=1,populate:str="true",limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    hosted_query = {"host" : userId}
    hostedMeetings = meeting_model_dal.read(hosted_query,page=page,limit=limit, sort=sort)
    
    if populate == "true":
        for hostedMeeting in hostedMeetings:
            for attendee in hostedMeeting.attendees:
                attendee_query = {"id" : attendee.userId}

                if "@" in attendee.userId:
                    attendee_query = {"email" : attendee.userId}
                elif  isMayBePhoneNumber(attendee.userId):
                    attendee_query = {"phoneNumber" : attendee.userId}

                attendeeDatas = user_model_dal.read(query=attendee_query, limit=1, select={"id" : 1, "firstName" : 1, "lastName" : 1, "companyName" : 1, "title" : 1, "email" : 1, "phoneNumber" : 1, "gender" : 1, "email" : 1, "profilePicture" : 1})
                if len(attendeeDatas) == 0:
                    hostedMeeting.attendees.remove(attendee)
                    continue
                attendeeData = attendeeDatas[0]
                attendee.userId = attendeeData    

    meetingDatas = MeetingModel.to_json_list(hostedMeetings)
    return meetingDatas

@router.get("/find/mymeetings/attendee")
async def get_meetings_attendee(request:Request,page:int=1,populate:str="true",limit:int= 12,sort="firstModified",token:str=Header(None)):
    userId = request.headers["userId"]
    hosted_query = {"attendees" : {"$elemMatch" : {"userId" : userId}}}
    hostedMeetings = meeting_model_dal.read(hosted_query,page=page,limit=limit, sort=sort)

    if populate == "true":
        for hostedMeeting in hostedMeetings:
            for attendee in hostedMeeting.attendees:
                attendee_query = {"id" : attendee.userId}
                if "@" in attendee.userId:
                    attendee_query = {"email" : attendee.userId}
                elif  isMayBePhoneNumber(attendee.userId):
                    attendee_query = {"phoneNumber" : attendee.userId}

                attendeeDatas = user_model_dal.read(query=attendee_query, limit=1, select={"id" : 1, "firstName" : 1, "lastName" : 1, "companyName" : 1, "title" : 1, "email" : 1, "phoneNumber" : 1, "gender" : 1, "email" : 1, "profilePicture" : 1})
                if len(attendeeDatas) == 0:
                    hostedMeeting.attendees.remove(attendee)
                attendeeData = attendeeDatas[0]
                attendee.userId = attendeeData 
                
    meetingDatas = MeetingModel.to_json_list(hostedMeetings)
    return meetingDatas

@router.put("/update/{meetingId}")
async def update_meeting(updateMeeting: UpdateMeetingModel,meetingId:str, request:Request,background_tasks:BackgroundTasks, token:str=Header(None)):
    userId = request.headers["userId"]
    meetingQuery = {"id" : meetingId}
    meetingDatas = meeting_model_dal.read(query=meetingQuery, limit=1)
    if len(meetingDatas) == 0:
        return HTTPException(status_code=400, detail="No meeting found by id")

    oldMeetingData = meetingDatas[0]
    if oldMeetingData.host != userId:
        return HTTPException(status_code=401, detail="User is not the host of a meeting")

    meeting_model_dal.update(query=meetingQuery, update_data=updateMeeting.to_json())

    attendees_email = []
    for attendee in oldMeetingData.attendees:
        attendees_email.append(attendee.email)

    email_recipients = ", ".join(attendees_email)
    email_head = f"{updateMeeting.title} meeting has been updated"
    email_body = f'''
        {updateMeeting.title} meeting has been updated
        Meeting title : {updateMeeting.title}
        Meeting description : {updateMeeting.description}
       
        Date : {updateMeeting.fromDate}
        Note : {updateMeeting.note}
        Meeting Link : {updateMeeting.meetingLink}
    '''
    background_tasks.add_task(Emails.send_email, email_recipients, email_body, email_head)
    message = {
        "userId" : userId,
        "message" : "meeting updated",
    }
    #json.dumps(message)
    res_from_sock = await connectionManager.send_personal_message(message,userId)
    print(f"Res from sck is : {res_from_sock}")   
    return {"message" : "meeting successfully updated"}

@router.put("/update_attendee/{action}/{meetingId}")
async def update_attendee(action: UpdateAttendeeActions, updateAttendees: UpdateAttendee, meetingId: str, request:Request,background_tasks:BackgroundTasks, token:str=Header(None)):
    userId = request.headers["userId"]
    meetingQuery = {"id" : meetingId}
    meetingDatas = meeting_model_dal.read(query=meetingQuery, limit=1)
    updateResponse = {}
    if len(meetingDatas) == 0:
        return {"message" : "no meeting found"}

    meetingData = meetingDatas[0]
    if meetingData.host != userId:
        return HTTPException(status_code=401,detail="You are not authorized to update this meeting")

    for attendee in updateAttendees.attendees:
        attendeeQuery = {}
        isPhoneNumber = isMayBePhoneNumber(attendee)
        if "@" in attendee:
            attendeeQuery = {"email" : attendee}
        elif isPhoneNumber:
            attendeeQuery = {"phoneNumber" : attendee}
        else:
            attendeeQuery = {"id" : attendee}

        attendeeDatas = user_model_dal.read(query=attendeeQuery, limit=1)
        print(f"attendee query .... {attendeeQuery}")
        print(f"len of attendee data : {str(len(attendeeDatas))}")
        if len(attendeeDatas) == 0: # user is new
            print("user is new dont hav eaccount ...")
            # user cant be blocked, 
            # user cant be removed from meeting either
            randomPasswordForNewUser = str(random.randint(111111,999999))
            hashed_password = hashlib.sha256(str(randomPasswordForNewUser).encode('utf-8'))
            
            newAttendeeUserId = str(uuid.uuid4())

            newUserData = None
            if "@" in attendee:
                newUserData = UserModel(
                    id = newAttendeeUserId,
                    email = attendee,
                    password = hashed_password.hexdigest()
                )
            elif isMayBePhoneNumber(attendee):
                newUserData = UserModel(
                    id = newAttendeeUserId,
                    email = "no@email.com",
                    phoneNumber = attendee,
                    password = hashed_password.hexdigest()
                )    
            else:
                updateResponse[attendee] = "invite data for new user is neither email nor phone"
                continue

            await user_model_dal.create(newUserData)
            ma = MeetingAttendees(
                id = str(uuid.uuid4()),
                userId=newAttendeeUserId,
                email= attendee if "@" in attendee else "no@email.com",
                status=MeetingAttendeStatus.pending)

            meetingData.attendees.append(ma)

            if "@" in attendee:
                updateResponse[attendee] = "new user invited by email"
                # send email
                email_head = "You have been invited to attend a meeting"
                email_body = f'''
                Hello,
                
                Meeting title : {meetingData.title}
                Meeting description : {meetingData.description}
                Attendees : {len(meetingData.attendees)}
                Date : {meetingData.fromDate}
                Note : {meetingData.note}
                Meeting Link : {meetingData.meetingLink}
                Login Password is : {str(randomPasswordForNewUser)}
                Are you comming ?
                Yes I am comming (twss) -> click here https://mmserver.ml/server/meeting/confirm_meeting/new_invite/{meetingData.id}/{newAttendeeUserId}/accept
                No am not comming -> click here https://mmserver.ml/server/meeting/confirm_meeting/new_invite/{meetingData.id}/{newAttendeeUserId}/reject
                '''
                background_tasks.add_task(Emails.send_email,attendee, email_body, email_head)
            else:
                updateResponse[attendee] = "new user invited by phone number"
                smsMessage = f"You have been invited to a meeting use password : {str(randomPasswordForNewUser)} to login"
                background_tasks.add_task(sms.send,attendee, smsMessage)

            continue

        attendeeData = attendeeDatas[0]        
        if action == UpdateAttendeeActions.add:
            isUserBlocked = sharedFuncs.isUserBlocked(attendeeData.id, userId)
            if isUserBlocked:
                updateResponse[attendee] = "user is blocked or user has blocked you"
                continue

            userAlreadyInMeeting = False
            for attendeesMeeting in meetingData.attendees:
                if attendeesMeeting.userId == attendeeData.id:
                    userAlreadyInMeeting = True

            if userAlreadyInMeeting:
                updateResponse[attendee] = "user already in meeting"
                continue

            ma = MeetingAttendees(
                id = str(uuid.uuid4()),
                userId=attendeeData.id,
                email=attendeeData.email,
                status=MeetingAttendeStatus.pending
            )
            meetingData.attendees.append(ma)
            updateResponse[attendee] = "user is added"
            
            # send email
            email_head = "You have been invited to attend a meeting"
            email_body = f'''
            Hello,
            
            Meeting title : {meetingData.title}
            Meeting description : {meetingData.description}
            Attendees : {len(meetingData.attendees)}
            Date : {meetingData.fromDate}
            Note : {meetingData.note}
            Meeting Link : {meetingData.meetingLink}
           
            Are you comming ?
            Yes I am comming (twss) -> click here https://mmserver.ml/server/meeting/confirm_meeting/{meetingData.id}/{attendeeData.id}/accept
                No am not comming -> click here https://mmserver.ml/server/meeting/confirm_meeting/{meetingData.id}/{attendeeData.id}/reject
            '''
            background_tasks.add_task(Emails.send_email,attendeeData.email, email_body, email_head)

        elif action == UpdateAttendeeActions.remove:
            userAlreadyInMeeting = False
            for attendeesMeeting in meetingData.attendees:
                if attendeesMeeting.userId == attendeeData.id:
                    userAlreadyInMeeting = True

            if not userAlreadyInMeeting:
                updateResponse[attendee] = "user not in meeting"
                continue

            for attendeeMeeting in meetingData.attendees:
                if attendeeMeeting.userId == attendeeData.id:
                    meetingData.attendees.remove(attendeeMeeting)
                    updateResponse[attendee] = "user is removed"

    print("updating meeting.......")
    print(meetingData)
    meetingDataQuery = {"id" : meetingData.id}
    meeting_model_dal.update(query=meetingDataQuery, update_data=meetingData.to_json())            
    print("update response again ....")
    print(updateResponse)
    message = {
        "userId" : meetingData.host,
        "message" : "meeting updated",
    }
    #json.dumps(message)
    res_from_sock = await connectionManager.send_personal_message(message,meetingData.host)
    print(f"Res from sck is : {res_from_sock}")     
    
    return updateResponse
        


    

@router.delete("/delete/{meetingId}")
async def delete_meeting(meetingId : str, request:Request,background_tasks:BackgroundTasks, token:str=Header(None)):
    userId = request.headers["userId"]
    meetingQuery = {"id" : meetingId}
    meetingDatas = meeting_model_dal.read(query=meetingQuery, limit=1)
    if len(meetingDatas) == 0:
        return {"message" : "no meeting found"}

    meetingData = meetingDatas[0]
    if meetingData.host != userId:
        return HTTPException(status_code=401,detail="You are not authorized to delete this meeting")

    # deleting meeting
    meeting_model_dal.delete(query=meetingQuery)
    emails = []
    for attendee in meetingData.attendees:
        emails.append(attendee.email)
            
    # send cancelation email
    cancelation_email_lists = ", ".join(emails)
    cancelation_email_head = f"Meeting has been deleted"
    cancelation_email_body = f'''
        The meeting {meetingId} has been deleted by the host
    '''     
    background_tasks.add_task(Emails.send_email, cancelation_email_lists, cancelation_email_body, cancelation_email_head)       
    return {"message" : "meeting has been successfully deleted"}

def isAttendeeInTheExistingList(attendee,oldList):
    exists = False
    for oldAttendee in oldList:
        if oldAttendee.userId == attendee:
            exists = True
    return exists        
