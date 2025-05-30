from fastapi import APIRouter, Header
from dal.user import UserModelDAL


userModelDAL = UserModelDAL()

router = APIRouter(
    prefix="/server/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def getUsers(token:str=Header(None), query="", page:int=1, limit:int=12,sort="firstModified"):
    if query == "":
        return {}
    userQuery = {"$text" : {"$search" : f"\"{query}\""}}

    userData = userModelDAL.read(query=userQuery, page=page, limit=limit, sort=sort)
    return userData
