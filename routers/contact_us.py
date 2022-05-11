from fastapi import APIRouter, Header, Request
from dal.contact_us import ContactUsModelDAL
from model.contact_us import ContactModel


contactUs_model_dal = ContactUsModelDAL()
router = APIRouter(
    prefix="/server/contactUs",
    tags=["contactUs"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create(createMeeting: ContactModel):
    createMeeting.resolved = False
    await contactUs_model_dal.create( createMeeting)
    return {"message" : "message successfully created"} 

@router.get("/find/{status}")
async def get_messages(status:str, request:Request,page:int=1,limit:int= 12,sort="firstModified", token:str=Header(None)):
    userId = request.headers["userId"]
    # allow only admins to access this endpoint
    status_query = {"resolved" : True if status == "read" else False}
    contactUsMessages = contactUs_model_dal.read(status_query,page=page,limit=limit, sort=sort)
    contactUsDatas = ContactModel.to_json_list(contactUsMessages)
    return contactUsDatas

@router.put("/update/{contactUsId}")
async def update_meeting(updateContact: ContactModel,contactUsId:str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
    contactUsQuery = {"id" : contactUsId}
    contactUs_model_dal.update(query=contactUsQuery, update_data=updateContact.to_json())
    return {"message" : "message successfully updated"}

@router.delete("/delete/{contactUsId}")
async def delete_meeting(contactUsId : str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
    # only admins can delete message
    contactUsQuery = {"id" : contactUsId}
    # deleting contact us message
    contactUs_model_dal.delete(query=contactUsQuery)

    return {"message" : "contact us message has been successfully deleted"}

