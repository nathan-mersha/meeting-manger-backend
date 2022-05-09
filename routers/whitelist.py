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
    print(f"User id from tokenn : {userId}")
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
        note = createWhiteList.note
    )
    whiteList_model_dal.create(whiteList)

    email_recipient = partyB.email
    email_head = f"{partyA.firstName} has requested you to be in his white list"
    email_body = f'''
        {partyA.firstName} has requested you to be in his white list
        When you are a white list you can access one others schedules
        Note : {createWhiteList.note}

        to Accept click here https://mmserver.ml/server/whitelist/accept/{whiteListId}
        to Deny click here https://mmserver.ml/server/whitelist/deny/{whiteListId}
    '''
    Emails.send_email(email_recipient, email_body, email_head)
    return {"message" : "White list successfully requsted"}


