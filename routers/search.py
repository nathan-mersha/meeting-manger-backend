from fastapi import APIRouter, Header
from dal.user import UserModelDAL


userModelDAL = UserModelDAL()

router = APIRouter(
    prefix="/server/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def create(token:str=Header(None), query="", page:int=1, limit:int=12,sort="firstModified"):
    if query == "":
        return {}
    
    print(f"Query is : {query}")
    userQuery = {"$text" : {"$search" : query}}

    userData = userModelDAL.read(query=userQuery, page=page, limit=limit, sort=sort)
    return userData
