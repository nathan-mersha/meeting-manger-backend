from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Emails():

    @staticmethod
    def send_email(recipients, body, subject):
        try:
            message = MIMEMultipart()
            message['From'] = "arrangemeet@gmail.com"
            message['To'] = recipients
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
            session.starttls() #enable security
            session.login("arrangemeet@gmail.com", "axsltblavsirgdeh") #login with mail_id and password
            text = message.as_string()
            session.sendmail("arrangemeet@gmail.com", recipients, text)
            session.quit()

        except Exception as e:
            print(e)
            print("Error: unable to send email") 
