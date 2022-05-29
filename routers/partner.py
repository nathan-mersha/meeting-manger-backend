from fastapi import APIRouter, Header, Request, BackgroundTasks
from dal.partner import PartnerModelDAL
from dal.user import UserModelDAL
from lib.shared import SharedFuncs
from model.partner import PartnerModel, CreatePartners
import uuid

partner_model_dal = PartnerModelDAL()
user_model_dal = UserModelDAL()
sharedFuncs = SharedFuncs()

router = APIRouter(
    prefix="/server/partner",
    tags=["partner"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create(partners: CreatePartners, request : Request,background_tasks: BackgroundTasks, token:str=Header(None)):
    userId = request.headers["userId"]
    creationResponses = {}
    print(f"len of partners : {len(partners.partners)}")
    for partnerId in partners.partners:
        print(f"loping for : {partnerId}")
        isUserBlocked = sharedFuncs.isUserBlocked(userId, partnerId)
        
        if isUserBlocked:
            creationResponses[partnerId] = "you can not add this person as a partner"
            continue

        newPartnerQuery = {"id" : partnerId}
        partnersData = user_model_dal.read(query=newPartnerQuery, limit=1)
        if len(partnersData) == 0:
            creationResponses[partnerId] = "user not found"
            continue
            
        partnerData = partnersData[0]

        subjectQuery = {"id" : userId}
        subjectsData = user_model_dal.read(query=subjectQuery, limit=1)
        if len(subjectsData) == 0:
            creationResponses[partnerId] = "user subject not found"
            continue

        subjectData = subjectsData[0]    

        partnerQuery = {"subject" : userId, "partner" : partnerId}
        partnersData = partner_model_dal.read(query=partnerQuery, limit=1)
        if len(partnersData) > 0:
            creationResponses[partnerId] = "user is already a partner"
            continue


        partnerModel = PartnerModel(
            id=str(uuid.uuid4()),
            subject = userId,
            partner = partnerId
        )
        await partner_model_dal.create(partnerModel)

        email_head = f"{subjectData.firstName} has added you as a partner"
        email_body = f'''
            {subjectData.firstName} has added you as a partner
            if you would like to add this person as a partner click on the link below
            https://mmserver.ml/server/partner/respond_as_a_partner/{userId}/{partnerId}
        '''

        background_tasks.add_task(partnerData.email, email_body, email_head)
        creationResponses[partnerId] = "partner successfully created"
        
    return creationResponses

@router.get("/find/i_added")
async def get_meetings_hosted(request:Request,page:int=1,limit:int= 12,sort="firstModified",populate="true", token:str=Header(None)):
    userId = request.headers["userId"]
    partnersQuery = {"subject" : userId}
    partnersData = partner_model_dal.read(query=partnersQuery,limit=limit, page=page, sort=sort, populate=populate)

    return partnersData

@router.get("/find/people_added_me")
async def get_meetings_hosted(request:Request,page:int=1,limit:int= 12,sort="firstModified",populate="true", token:str=Header(None)):
    userId = request.headers["userId"]
    partnersQuery = {"partner" : userId}
    partnersData = partner_model_dal.read(query=partnersQuery,limit=limit, page=page, sort=sort, populate=populate)
    return partnersData

@router.get("/respond_as_a_partner/{partnerId}/{subjectId}")
async def respond_as_a_partner(partnerId:str, subjectId: str):
    partnerModel = PartnerModel(
        id=str(uuid.uuid4()),
        subject=subjectId,
        partner=partnerId
    )
    partner_query = {"subject" : subjectId, "partner" : partnerId}
    partnersData = partner_model_dal.read(query=partner_query, limit=1)
    
    if len(partnersData) > 0:
        return {"message" : "user is already a partner"}

    await partner_model_dal.create(partnerModel)
    return {"message" : f"You are now a partner with : {partnerId}"}

@router.delete("/delete/{partnerId}")
async def delete_meeting(partnerId : str, request:Request, token:str=Header(None)):
    userId = request.headers["userId"]
    # only admins can delete message
    partnerQuery = {"subject" : userId, "partner" : partnerId}
    # deleting contact us message
    partner_model_dal.delete(query=partnerQuery)

    return {"message" : "partner has been successfully deleted"}

