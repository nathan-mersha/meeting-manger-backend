import configparser
from twilio.rest import Client


class SMS():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./cred/config.ini")
        
        self.account_sid = str(self.config['twilio']['account_sid'])
        self.auth_token = str(self.config['twilio']['auth_token'])
        self.phone_number = str(self.config['twilio']['phone_number'])

        self.client = Client(self.account_sid, self.auth_token)

    def send(self, to, message):
        try:
            self.client.messages.create(from_=self.phone_number, body=message, to=to)
        except Exception as e:

            print(f"error while sending sms : {str(e)}")

    def get(self, sid):
        status = self.client.messages.get(sid)
        # print(status.status)
        print(vars(status))

