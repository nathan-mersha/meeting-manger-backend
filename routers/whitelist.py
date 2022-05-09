from http.client import HTTPException
from fastapi import APIRouter, Header, Request
import uuid
from model.whitelist import CreateWhiteListModel, WhiteListModel
from lib.email import Emails
from dal.whitelist import WhiteListModelDAL
from dal.user import UserModelDAL

whiteList_model_dal = WhiteListModelDAL()
user_model_dal = UserModelDAL()

router = APIRouter(
    prefix="/server/whitelist",
    tags=["whiteList"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create(createWhiteList: CreateWhiteListModel,request : Request,  token:str=Header(None)):
    userId = request.headers["userId"]
    whiteListQuery = {
        "partyA" : userId,
        "partyB" : createWhiteList.to
    }
    whiteListDatas = whiteList_model_dal.read(query=whiteListQuery, limit=1)
    if len(whiteListDatas) > 0:
        return {"message" : "white list already exists"}

    partyAQuery = {"id" : userId}
    userDatasA = user_model_dal.read(query=partyAQuery, limit=1)
    if len(userDatasA) == 0:
        return {"message" : "Your account does not exist or may have been deleted"}

    partyA = userDatasA[0]

    partyBQuery = {"id" : createWhiteList.to}
    userDatasB = user_model_dal.read(query=partyBQuery, limit=1)
    if len(userDatasB) == 0:
        return {"message" : "user requested to be a whitelist does not exist"}

    partyB = userDatasB[0]

    whiteListId = str(uuid.uuid4())
    whiteList = WhiteListModel(
        id = whiteListId,
        partyA = userId,
        partyB = createWhiteList.to,
        partyAAccepted = True,
        partyBAccepted = False,
        responded=False,
        note = createWhiteList.note
    )
    await whiteList_model_dal.create(whiteList)

    email_recipient = partyB.email
    email_head = f"{partyA.firstName} has requested you to be in his white list"
    email_body = f'''
        {partyA.firstName} has requested you to be in his white list
        When you are a white list you can access one others schedules
        Note : {createWhiteList.note}

        to Accept click here https://mmserver.ml/server/whitelist/request/accept/{whiteListId}
        to Deny click here https://mmserver.ml/server/whitelist/request/deny/{whiteListId}
    '''
    Emails.send_email(email_recipient, email_body, email_head)
    return {"message" : "White list successfully requsted"}


@router.get("/request/{status}/{whiteListId}")
async def respond_to_whitelist_request(status:str,whiteListId:str):
    whiteListQuery = {"id" : whiteListId}
    whiteListDatas = whiteList_model_dal.read(query=whiteListQuery, limit=1)
    if len(whiteListDatas) == 0:
        return {"message" : "white list request does not exist"}

    whiteListData = whiteListDatas[0]

    if whiteListData.responded == True:
        return {"message" : "You have already reponded to this request"}

    partyAQuery = {"id" : whiteListData.partyA}
    userDatasA = user_model_dal.read(query=partyAQuery, limit=1)
    if len(userDatasA) == 0:
        return {"message" : "user, party a not found"}
    partyA = userDatasA[0]

    partyBQuery = {"id" : whiteListData.partyB}
    userDatasB = user_model_dal.read(query=partyBQuery, limit=1)
    if len(userDatasB) == 0:
        return {"message" : "user, party b not found"}
    partyB = userDatasB[0]


    whiteListQuery = {"id" : whiteListId}
    whiteListUpdateData = {"partyBAccepted" : True if status == "accept" else False, "responded" : True}
    whiteList_model_dal.update(query=whiteListQuery, update_data=whiteListUpdateData)

    emailRecipients = partyA.email
    emailHead = f'{partyB.firstName} has {"accepted" if status == "accept" else "denied"} your whitelist request'
    emailBody = f'''
        {partyB.firstName} has {"accepted" if status == "accept" else "denied"} your whitelist request
    '''

    Emails.send_email(emailRecipients, emailBody, emailHead)
    return {"message" : f"Your {status} response was successful"}
    
@router.get("/find/{status}")
async def get_my_whitelists(status:str, request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    whiteListQuery = {}
    if status == "accepted":
        whiteListQuery = {"$or" : [{"partyA" : userId}, {"partyB" : userId}], "$and" : [{"partyAAccepted" : True}, {"partyBAccepted" : True}]}
    else:
        whiteListQuery = {"$or" : [{"partyA" : userId}, {"partyB" : userId}], "$or" : [{"partyAAccepted" : False}, {"partyBAccepted" : False}]}    
    whiteListDatas = whiteList_model_dal.read(query=whiteListQuery, limit=limit, page=page,sort=sort)
    return whiteListDatas


@router.delete("/delete/{whiteListeId}")
async def delete_whitelist(whiteListId: str,request: Request, token:str=Header(None)):
    userId = request.headers["userId"]
    whiteListQuery = {"id" : whiteListId}
    whiteListDatas = whiteList_model_dal.read(query=whiteListQuery, limit=1)
    if len(whiteListDatas) == 0:
        return {"message" : "whitelist not found"}
    whiteListData = whiteListDatas[0]
    
    if whiteListData.partyA != userId and whiteListData.partyB != userId:
        return HTTPException(status_code=401, detail="user not allowed to delete white list data")
    
    whiteList_model_dal.delete(query=whiteListQuery)

    return {"message" : "whitelist record delete"}
