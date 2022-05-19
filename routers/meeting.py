from datetime import date
import email
from http.client import HTTPException
from random import random
import hashlib
from fastapi import APIRouter, Header, Request, BackgroundTasks
import uuid
from dal.meeting import MeetingModelDAL
from dal.user import UserModelDAL
from lib.shared import SharedFuncs
from lib.sms import SMS
from model.user import UserModel
from model.meeting import MeetingAttendeStatus, MeetingAttendees, MeetingModel, UpdateAttendee, UpdateMeetingModel
from model.schedule import ScheduleModel
from dal.schedule import ScheduleModelDAL
from lib.email import Emails
import phonenumbers
import random

meeting_model_dal = MeetingModelDAL()
user_model_dal = UserModelDAL()
schedule_model_dal = ScheduleModelDAL()

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

    for meetingAttendee in createMeeting.attendees:
        attendeeUserQuery = {}
        isUserBlocked = False
        
        if "@" in meetingAttendee:
            attendeeUserQuery = {"email" : meetingAttendee}
        else:
            attendeeUserQuery = {"id" : meetingAttendee}    
            isUserBlocked = sharedFuncs.isUserBlocked(user_id, meetingAttendee)
        
        if isUserBlocked:
            break

        attendeeDatas = user_model_dal.read(query=attendeeUserQuery, limit=1)
        parsedPhoneNumber = None
        isPhoneNumber = None
        try:
            parsedPhoneNumber = phonenumbers.parse(meetingAttendee)
            isPhoneNumber = phonenumbers.is_valid_number(parsedPhoneNumber)
        except :
            pass    

        
        if len(attendeeDatas) == 0 and "@" in meetingAttendee: # user is new and here by invitation by email
            # user is new
            # create account for user
            # get id and append
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
            Date : {createMeeting.date}
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
                Date : {createMeeting.date}
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
                    date = meetingData.date,
                    duration = meetingData.duration,
                    title = meetingData.title,
                    note = meetingData.note,
                    mode = meetingData.mode
                )
                print("creating schedule")
                await schedule_model_dal.create(scheduleData)

                break
   
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
            Date : {meetingData.date}
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
            Date : {meetingData.date}
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
            break
   
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
            Date : {meetingData.date}
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
            Date : {meetingData.date}
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
                    break
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
                    break
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
       
        Date : {updateMeeting.date}
        Note : {updateMeeting.note}
        Meeting Link : {updateMeeting.meetingLink}
    '''
    background_tasks.add_task(Emails.send_email, email_recipients, email_body, email_head)
    return {"message" : "meeting successfully updated"}

@router.put("/update_attendee/{meetingId}")
async def update_attendee(updateAttendees: UpdateAttendee, meetingId: str, request:Request,background_tasks:BackgroundTasks, token:str=Header(None)):
    userId = request.headers["userId"]
    meetingQuery = {"id" : meetingId}
    meetingDatas = meeting_model_dal.read(query=meetingQuery, limit=1)
    if len(meetingDatas) == 0:
        return {"message" : "no meeting found"}

    meetingData = meetingDatas[0]
    if meetingData.host != userId:
        return HTTPException(status_code=401,detail="You are not authorized to update this meeting")

    removed_attendees = []
    newAttendeeData = []

    for oldAttendees in meetingData.attendees:
        if oldAttendees.userId not in updateAttendees.attendees: # this user has been removed
            removed_attendees.append(oldAttendees.email)
        else:
            newAttendeeData.append(oldAttendees)    

    for updateAttendee in updateAttendees.attendees:
        if not isAttendeeInTheExistingList(updateAttendee, meetingData.attendees): # newly added attendee           
            attendeeQuery = {"id" : updateAttendee}
            attendeeDatas = user_model_dal.read(query=attendeeQuery, limit=1)

            if len(attendeeDatas) == 0:
                break
            attendeeData = attendeeDatas[0]
            ma = MeetingAttendees(
                id = str(uuid.uuid4()),
                userId=attendeeData.id,
                email=attendeeData.email,
                status=MeetingAttendeStatus.pending
            )    
            newAttendeeData.append(ma)
            # todo sending email for newly added attendee
            email_head = f"Request meeting : {meetingData.title}"
            email_body = f'''
                Meeting title : {meetingData.title}
            Meeting description : {meetingData.description}
            Attendees No : {len(updateAttendees)}
            Date : {meetingData.date}
            Note : {meetingData.note}
            Meeting Link : {meetingData.meetingLink}
            Are you comming ?
            Yes I am comming (twss) -> click here https://mmserver.ml/server/meeting/confirm_meeting/{meetingData.id}/{attendeeData.id}/accept
            No am not comming -> click here https://mmserver.ml/server/meeting/confirm_meeting/{meetingData.id}/{attendeeData.id}/reject
            '''
            background_tasks.add_task(Emails.send_email, attendeeData.email, email_body, email_head)

    new_meeting_update_data = {"attendees" : MeetingAttendees.to_json_list(newAttendeeData)}
    meeting_model_dal.update(query=meetingQuery, update_data=new_meeting_update_data)

    if len(removed_attendees) > 0:
        # email added attendees
        email_recipients_removed = ", ".join(removed_attendees)
        email_head_removed = f"You have been removed from meeting, {meetingData.title}"
        email_body_removed = f'''
            You have been removed from meeting, {meetingData.title}
        '''
        background_tasks.add_task(Emails.send_email, email_recipients_removed, email_body_removed, email_head_removed)

    return {"message" : "successfully updated attedees"}

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
