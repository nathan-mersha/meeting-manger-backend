from ast import Num
import calendar as cal
from datetime import datetime
from fastapi import APIRouter, Header, Request
from dal.config import ConfigModelDAL
from dal.contact_us import ContactUsModelDAL
from dal.meeting import MeetingModelDAL
from dal.user import UserModelDAL
from model.contact_us import ContactModel

# & c:/Users/user/Desktop/school/meeting-manger-backend/venv/Scripts/Activate.ps1
user_model_dal = UserModelDAL()
config_model_dal = ConfigModelDAL()
meeting_model_dal = MeetingModelDAL()
router = APIRouter(
    prefix="/server/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)


@router.get("/meetings")
async def status(year: int = datetime.now().year, month: int = 1, token: str = Header(None)):
    totalMeetings = meeting_model_dal.count()
    totalMeetingsChooseYear = get_meeting_status(year, 1, 12)
    meetingsByChooseMonth = get_meeting_status(year, month, month)
    totalMeetingsYear = get_meeting_status(datetime.now().year, 1, 12)
    preTotalMeetingsYear = get_meeting_status(datetime.now().year-1, 1, 12)
    totalMeetingsMonth = get_meeting_status(
        datetime.now().year, datetime.now().month, datetime.now().month)
    preTotalMeetingsMonth = get_meeting_status(
        datetime.now().year, datetime.now().month-1, datetime.now().month-1)
    return {
        "totalMeetings": totalMeetings,
        "meetingsByChooseMonth": meetingsByChooseMonth,
        "totalMeetingsChooseYear": totalMeetingsChooseYear,
        "totalMeetingsYear": totalMeetingsYear,
        "preTotalMeetingsYear": preTotalMeetingsYear,
        "totalMeetingsMonth": totalMeetingsMonth,
        "preTotalMeetingsMonth": preTotalMeetingsMonth
    }


@router.get("/users")
async def status(year: int = datetime.now().year, month: int = 1, token: str = Header(None)):
    totalUsers = user_model_dal.count()
    totalUsersChooseYear = get_user_status(year, 1, 12)
    usersByChooseMonth = get_user_status(year, month, month)
    totalUsersYear = get_user_status(datetime.now().year, 1, 12)
    preTotalUsersYear = get_user_status(datetime.now().year-1, 1, 12)
    totalUsersMonth = get_user_status(
        datetime.now().year, datetime.now().month, datetime.now().month)
    preTotalUsersMonth = get_user_status(
        datetime.now().year, datetime.now().month-1, datetime.now().month-1)
    return {
        "totalUsers": totalUsers,
        "usersByChooseMonth": usersByChooseMonth,
        "totalUsersChooseYear": totalUsersChooseYear,
        "totalUsersYear": totalUsersYear,
        "preTotalUsersYear": preTotalUsersYear,
        "totalUsersMonth": totalUsersMonth,
        "preTotalUsersMonth": preTotalUsersMonth
    }


@router.get("/members")
async def status(token: str = Header(None)):
    config = config_model_dal.read()
    data = {}
    for membership in config.pricingPlan.keys():
        total = user_model_dal.count(query={"planType": membership})
        data[membership] = total
    return data


def get_meeting_status(year: int, fromMonth: int, toMonth: int):
    daysInMonth = cal.monthrange(year, toMonth)[1]
    dateFrom = datetime(year, fromMonth, 1)
    dateTo = datetime(year, toMonth, daysInMonth)
    return meeting_model_dal.count(
        query={"firstModified": {"$gte": dateFrom, "$lte": dateTo}})


def get_user_status(year: int, fromMonth: int, toMonth: int):
    daysInMonth = cal.monthrange(year, toMonth)[1]
    dateFrom = datetime(year, fromMonth, 1)
    dateTo = datetime(year, toMonth, daysInMonth)
    return user_model_dal.count(
        query={"firstModified": {"$gte": dateFrom, "$lte": dateTo}})
