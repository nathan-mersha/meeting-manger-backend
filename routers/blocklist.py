from http.client import HTTPException
from fastapi import APIRouter, Header, Request
import uuid
from dal.blocklist import BlockListUsModelDAL
from model.blocklist import BlockListModel
from lib.email import Emails

blockList_model_dal = BlockListUsModelDAL()

router = APIRouter(
    prefix="/server/blockList",
    tags=["blockList"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create():
    pass

@router.get("/find")
async def get_meetings_hosted(status:str, request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    pass

@router.delete("/delete/{blockListId}")
async def delete_meeting(blockListId : str, request:Request, token:str=Header(None)):
    pass

