from http.client import HTTPException
from fastapi import APIRouter, Header, Request
from dal.group import GroupModelDAL
from lib.email import Emails
from lib.shared import SharedFuncs

from model.group import GroupModel, UpdateGroupModel


group_model_dal = GroupModelDAL()
sharedFuncs = SharedFuncs()

emails = Emails()
router = APIRouter(
    prefix="/server/group",
    tags=["group"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create(createGroup: GroupModel, request:Request, token:str=Header(None)):
    user_id = request.headers["userId"]
    createGroup.owner = user_id
    
    # removing members that are blocked
    # todo : think of a better way...
    for member in createGroup.members:
        isBlocked = sharedFuncs.isUserBlocked(user_id, member)
        if isBlocked:
            
            createGroup.members.remove(member)

    await group_model_dal.create(createGroup)
    return {"message" : "Successfully created group"}

@router.get("/find/my_groups/owner")
async def get_my_groups_owner(request:Request,page:int=1, limit:int=12, sort="fistModified",sortType = -1, token:str=Header(None)):
    userId = request.headers["userId"]

    groupQuery = {"owner" : userId}
    groups = group_model_dal.read(groupQuery, page=page, limit=limit, sort=sort)
    groupDatas = GroupModel.to_json_list(groups)
    return groupDatas;

@router.get("/find/my_groups/member")
async def get_my_groups_member(request:Request,page:int=1, limit:int=12, sort="fistModified",sortType = -1, token:str=Header(None)):
    userId = request.headers["userId"]

    groupQuery = {"members" : {"$in"  : [userId]}}
    groups = group_model_dal.read(groupQuery, page=page, limit=limit, sort=sort)
    groupDatas = GroupModel.to_json_list(groups)
    return groupDatas;

@router.put("/update/{groupId}")
async def update_group(updateGroup:UpdateGroupModel, groupId:str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
    groupQuery = {"id" : groupId}
    groupDatas = group_model_dal.read(query=groupQuery, limit=1)
    if len(groupDatas) == 0:
        return HTTPException(status_code=400, detail="No group found by id")

    groupData = groupDatas[0]    
    if groupData["owner"] != userId:
        return HTTPException(status_code=401, detail="You are not allowed to update group")

    updateData = updateGroup.to_json()
    group_model_dal.update(query=groupQuery, update_data=updateData)
    return {"message" : "successfully updated group"}

@router.delete("/delete/{groupId}")
async def delete_group(groupId:str,request:Request,token:str=Header(None)):
    userId = request.headers["userId"]
    groupQuery = {"id" : groupId}
    groupDatas = group_model_dal.read(query=groupQuery, limit=1)
    if len(groupDatas) == 0:
        return {"message" : "no group found"}
    groupData = groupDatas[0]
    if groupData.owner != userId:
        return HTTPException(status_code=401,detail="You are not authorized to delete this group")

    group_model_dal.delete(query=groupQuery)
    return {"message" : "successfully deleted group"}         
