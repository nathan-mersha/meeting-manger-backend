
import uuid
from fastapi import APIRouter, BackgroundTasks, Header, Request
from dal.blocklist import BlockListModelDAL
from dal.group import GroupModelDAL
from model.blocklist import BlockListModel
from dal.whitelist import WhiteListModelDAL
from dal.partner import PartnerModelDAL
from dal.meeting import MeetingModelDAL
from model.meeting import MeetingAttendees

blockList_model_dal = BlockListModelDAL()
whiteList_model_dal = WhiteListModelDAL()
partner_model_dal = PartnerModelDAL()
group_model_dal = GroupModelDAL()
meeting_model_dal = MeetingModelDAL()


router = APIRouter(
    prefix="/server/blockList",
    tags=["blockList"],
    responses={404: {"description": "Not found"}},
)

async def delete_from_whiteList(ownerId:str,blockedPersonId:str):
    whiteListQueryA = {"partyA" : ownerId, "partyB" : blockedPersonId}
    whiteListQueryB = {"partyA" : blockedPersonId, "partyB" : ownerId}

    whiteList_model_dal.delete(whiteListQueryA)
    whiteList_model_dal.delete(whiteListQueryB)
    return True

async def delete_from_partner(ownerId:str,blockedPersonId:str):
    partnerQueryA = {"subject" : ownerId, "partner" : blockedPersonId}
    partnerQueryB = {"subject" : blockedPersonId, "partner" : ownerId}

    partner_model_dal.delete(partnerQueryA)
    partner_model_dal.delete(partnerQueryB)
    return True

async def delete_from_groups(ownerId:str,blockedPersonId:str):
    group_query = {"owner" : ownerId, "members" : {"$in" : [blockedPersonId]}}
    groupsData = group_model_dal.read(query=group_query, limit=1000)
    for groupData in groupsData:
        query = {"id" : groupData.id}
        groupData.members.remove(blockedPersonId)
        updateData = {"members" : groupData.members}
        group_model_dal.update(query=query, update_data=updateData)

    return True    

async def delete_from_meetings(ownerId:str,blockedPersonId:str):
    meetingQuery = {"host" : ownerId, "attendees.userId" : {"$in" : [blockedPersonId]}}
    meetingsData = meeting_model_dal.read(query=meetingQuery, limit=1000)
    for meetingData in meetingsData:
        attendees = meetingData.attendees
        for attendee in attendees:
            if attendee.userId == blockedPersonId:
                attendees.remove(attendee)
                continue
        
        updateQuery = {"id" : meetingData.id}
        updateData = {"attendees" : MeetingAttendees.to_json_list(attendees)}
        meeting_model_dal.update(query=updateQuery, update_data=updateData)
    
    return True
        

@router.post("/create/{blockUserId}")
async def create(blockUserId: str, request : Request, background_tasks : BackgroundTasks, token:str=Header(None)):
    userId = request.headers["userId"]
    blockListQuery = {"subject" : userId, "blocked" : blockUserId}
    blockListsData = blockList_model_dal.read(query=blockListQuery, limit=1)

    if len(blockListsData) > 0:
        return {"message" : "user already blocked"}

    blockListData = BlockListModel(
        id = str(uuid.uuid4()),
        subject = userId,
        blocked = blockUserId,
    )

    background_tasks.add_task(blockList_model_dal.create, blockListData)

    background_tasks.add_task(delete_from_whiteList, userId, blockUserId)
    background_tasks.add_task(delete_from_partner, userId, blockUserId)
    background_tasks.add_task(delete_from_groups, userId, blockUserId)
    background_tasks.add_task(delete_from_meetings, userId, blockUserId)
    
    return {"message" : "user successfully blocked"}

    
@router.get("/find/myblocklists")
async def get_blockLists(request:Request,page:int=1,limit:int= 12,sort="firstModified",populate="true", token:str=Header(None)):
    userId = request.headers["userId"]
    blockListQuery = {"subject" : userId}
    blockListDatas = blockList_model_dal.read(query=blockListQuery, limit=limit, page=page, sort=sort, populate=populate)
    return blockListDatas

@router.delete("/delete/{blockedUserId}")
async def delete_meeting(blockedUserId : str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
    blockListQuery = {"subject" : userId, "blocked" : blockedUserId}
    delete_response = blockList_model_dal.delete(blockListQuery)
    print(delete_response)
    return {"message" : "successfully removed blocklist"}