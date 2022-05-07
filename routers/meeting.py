from http.client import HTTPException
from fastapi import APIRouter, Header, Request
import uuid
from dal.meeting import MeetingModelDAL
from dal.user import UserModelDAL
from lib.sms import SMS
from model.meeting import MeetingAttendeStatus, MeetingAttendees, MeetingModel, UpdateAttendee, UpdateMeetingModel
from lib.email import Emails

meeting_model_dal = MeetingModelDAL()
user_model_dal = UserModelDAL()
emails = Emails()
sms = SMS()
router = APIRouter(
    prefix="/server/meeting",
    tags=["meeting"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create(createMeeting: MeetingModel,request:Request, token:str=Header(None)):
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
        attendeeUserQuery = {"id" : meetingAttendee}
        attendeeDatas = user_model_dal.read(query=attendeeUserQuery, limit=1)
        if len(attendeeDatas) == 0:
            break
        attendeeUser = attendeeDatas[0]
        ma = MeetingAttendees(
            id = str(uuid.uuid4()),
            userId=meetingAttendee,
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
            Yes I am comming (twss) -> click here https://mmserver.ml/server/meeting/confirm_meeting/{createMeeting.id}/{meetingAttendee}/accept
            No am not comming -> click here https://mmserver.ml/server/meeting/confirm_meeting/{createMeeting.id}/{meetingAttendee}/reject
        '''
        Emails.send_email(attendeeUser.email, email_body, email_head)

        if attendeeUser.phoneNumber != None:
            sms.send(to=attendeeUser.phoneNumber, message=f"You have been invited to join a meeting from {host_data.firstName}. Check your email for more")

    createMeeting.attendees = MeetingAttendees.to_model_list(editedAttendees)
    meeting_data = await meeting_model_dal.create(meeting_model=createMeeting)
   
    if not meeting_data.acknowledged:
        return {"message" : "something went wrong while creating meeting"}

    
    # todo notify attendees via email about the created meeting
    return {"message" : "meeting successfully created"} 

@router.get("/confirm_meeting/{meetingId}/{userId}/{status}")
async def confirm_meeting(meetingId: str,userId: str, status: str):
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
    Emails.send_email(host_data.email, host_email_body, host_email_head)


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
    Emails.send_email(attendee_data.email, attendee_email_body, attendee_email_head)

    return {"message" : f"meeting {status}"}

@router.get("/find/mymeetings/hosted")
async def get_meetings_hosted(request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    hosted_query = {"host" : userId}
    hostedMeetings = meeting_model_dal.read(hosted_query,page=page,limit=limit, sort=sort)
    meetingDatas = MeetingModel.to_json_list(hostedMeetings)
    return meetingDatas

@router.get("/find/mymeetings/attendee")
async def get_meetings_attendee(request:Request,page:int=1,limit:int= 12,sort="firstModified",sortType = -1, token:str=Header(None)):
    userId = request.headers["userId"]
    hosted_query = {"attendees" : {"$elemMatch" : {"userId" : userId}}}
    hostedMeetings = meeting_model_dal.read(hosted_query,page=page,limit=limit, sort=sort,sort_type=sortType)
    meetingDatas = MeetingModel.to_json_list(hostedMeetings)
    return meetingDatas

@router.put("/update/{meetingId}")
async def update_meeting(updateMeeting: UpdateMeetingModel,meetingId:str, request:Request, token:str=Header(None)):
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
    Emails.send_email(email_recipients,email_body,email_head)
    return {"message" : "meeting successfully updated"}


@router.put("/update_attendee/{meetingId}")
async def update_attendee(updateAttendees: UpdateAttendee, meetingId: str, request:Request, token:str=Header(None)):
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
            Emails.send_email(attendeeData.email, email_body, email_head)

    new_meeting_update_data = {"attendees" : MeetingAttendees.to_json_list(newAttendeeData)}
    meeting_model_dal.update(query=meetingQuery, update_data=new_meeting_update_data)

    if len(removed_attendees) > 0:
        # email added attendees
        email_recipients_removed = ", ".join(removed_attendees)
        email_head_removed = f"You have been removed from meeting, {meetingData.title}"
        email_body_removed = f'''
            You have been removed from meeting, {meetingData.title}
        '''
        Emails.send_email(email_recipients_removed, email_body_removed, email_head_removed)

    return {"message" : "successfully updated attedees"}

@router.delete("/delete/{meetingId}")
async def delete_meeting(meetingId : str, request:Request, token:str=Header(None)):
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
    email_head = f"Meeting has been deleted"
    email_body = f'''
        The meeting {meetingId} has been deleted by the host
    '''            
    Emails.send_email(", ".join(emails), email_body, email_head)
    return {"message" : "meeting has been successfully deleted"}

def isAttendeeInTheExistingList(attendee,oldList):
    exists = False
    for oldAttendee in oldList:
        if oldAttendee.userId == attendee:
            exists = True
    return exists        
