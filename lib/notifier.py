from collections import UserDict
from random import random
from typing import Dict, List
import uuid
from starlette.websockets import WebSocket
import json
from dal.notification import NotificationModelDAL

from model.notification import NotificationModel


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict] = []
        self.notification_model_dal = NotificationModelDAL()

    async def connect(self, websocket: WebSocket):
        print("Socket connected ----->")
        await websocket.accept()
        userId = await websocket.receive_text()
        print("Socket connected -----> id ", userId)
        data = {
            "websocket": websocket,
            "userId": userId
        }
        self.active_connections.append(data)
        # ,"sent":False
        notification = {"userId": userId, "sent": False}
        notificationData = self.notification_model_dal.read(notification)
        print(len(notificationData))
        for notification in notificationData:
            res_from_sock = await self.send_personal_message(notification.payload, notification.user_id)
            if res_from_sock == True:
                notification = {"id": notification.id}
                notificationUpdate = {"sent": True}
                self.notification_model_dal.update(
                    query=notification, update_data=notificationUpdate)

    def disconnect(self, websocket: WebSocket):
        print("Socket disconnected ----->")
        for active_connection in self.active_connections:
            if active_connection["websocket"] == websocket:
                self.active_connections.remove(active_connection)

    async def send_personal_message(self, message: dict, userId: str):
        print(f"message is : {message}")
        print(f"user id is : {userId}")
        if(len(self.active_connections) == 0):
            return await self.save(userId, message)
        isFound = False
        for active_connection in self.active_connections:
            if active_connection["userId"] == userId:
                isFound = True
                
                message["id"] =random.sample(range(10, 30), 10)
                res=await active_connection["websocket"].send_text(json.dumps(message))
                print("res save 1234")
                if res == "None":  # user is not connected, save to db to notify the next time he does
                    print("res save last")
                    return await self.save(userId, message)
                else:
                    return True
        if not isFound:
            return await self.save(userId, message)

    async def save(self, userId, message):
        notification_data=NotificationModel(
                        id=str(uuid.uuid4()),
                        user_id=userId,
                        payload=message,  # this message is a json string
                        sent=False,
                        first_modified=str(datetime.now().isoformat()),
                        last_modified=str(datetime.now().isoformat()))
        await self.notification_model_dal.create(notification_data)
        return False

    async def broadcast(self, message: str):
        print("Broadcasting ------>")
        for connection in self.active_connections:
            await connection["websocket"].send_text(message)
