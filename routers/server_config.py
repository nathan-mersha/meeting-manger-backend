from fastapi import APIRouter, Header, Request
import configparser

from model.server_config import ConfigModel


router = APIRouter(
    prefix="/server/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)

config = configparser.ConfigParser()
config.read("./cred/config.ini")
config_id = config["secrets"]["config_id"]


@router.put("/")
async def update_config(request:Request, updateConfig:ConfigModel, token:str=Header(None)):
    config_query = {"id" : config_id}
    
    # update config

@router.get("/")
async def get_config(token:str=Header(None)):
    pass