from fastapi import APIRouter, Header, Request
import configparser
from dal.config import ConfigModelDAL

from model.server_config import ConfigModel


router = APIRouter(
    prefix="/server/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)

config = configparser.ConfigParser()
config.read("./cred/config.ini")
config_id = config["secrets"]["config_id"]
configModelDal = ConfigModelDAL()

@router.put("/")
async def update_config(request:Request, updateConfig:ConfigModel, token:str=Header(None)):
    config_query = {"id" : config_id}
    configModelDal.update(query=config_query, update_data=updateConfig)
    return {"message" : "config updated"}

@router.get("/")
async def get_config(token:str=Header(None)):
    configQuery = {"id" : config_id}
    configData = configModelDal.read(query=configQuery, limit=1)
    return configData