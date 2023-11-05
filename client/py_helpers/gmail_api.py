from __future__ import print_function

import base64
import os.path
import time

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import mimetypes
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
################################################################
################################################################
SCOPES = ['https://mail.google.com/']

Service = None                                  # keeps gmail service of user's gmail account
                                                # in case NOT ANONYMOUS
Creds = None

def authenticate(tokenFile):
    """
        let user authenticate and authorize this app with Google

        then build gmail service
    """
    ############### try: ###############
    global Service, Creds
    tokenFile = 'config/' + tokenFile + '.json'
    if os.path.exists(tokenFile):
        Creds = Credentials.from_authorized_user_file(tokenFile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not Creds or not Creds.valid:
        if Creds and Creds.expired and Creds.refresh_token:
            Creds.refresh(Request())
        elif not os.path.exists('config/credentials.json'):
            print("Cannot find credentials file")
            return None
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            Creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenFile, 'w') as token:
            token.write(Creds.to_json())

def buildService():
    global Service, Creds
    Service = build('gmail', 'v1', credentials=Creds)

def checkAuthenticated():
    """
        check if user has authenticated and authorized

        returns profile_obj, True || error, False
    """
    global Service
    try:
        profile = Service.users().getProfile(userId='me').execute()
        return profile, True
    except HttpError as error:
        return error, False

def constructMail(receiver, sender, subject, msg_content):
    message = MIMEMultipart()
    message['To'] = receiver
    message['From'] = sender
    message['Subject'] = subject
    body = MIMEText(msg_content, 'plain')
    message.attach(body)
    if os.path.exists('image/'):
        directory = os.listdir('image/')
        for file in directory:
            attachment_filename = file
            # print(attachment_filename)
            # guessing the MIME type
            # type_subtype, _ = mimetypes.guess_type(attachment_filename)
            # maintype, subtype = type_subtype.split('/')
            with open(os.path.join("image", attachment_filename), 'rb') as fp:
                part = MIMEApplication(fp.read(), Name=os.path.basename(
                    os.path.join("image", attachment_filename)))
                part['Content-Disposition'] = 'attachment; filename="{}"'.format(
                    os.path.basename(os.path.join("image", attachment_filename)))
            message.attach(part)
    return message

def sendMail(receiver, sender, subject, msg_content):
    """
        returns [str]msg obj, [str]error
    """
    global Service
    try:
        if not Service:
            buildService()
        message = constructMail(
            receiver=receiver, sender=sender, subject=subject, msg_content=msg_content
        )
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (Service.users().messages().send
                        (userId="me", body=create_message).execute())
        # print(F'Message Id: {send_message["id"]}')
    except HttpError as err:
        # print(F'An error occurred: {error}')
        return None, err
    return send_message, None

def readMails(conditions):
    global Service, Creds
    while True:
        try:
            if not Service:
                buildService()
            results = Service.users().messages().list(userId='me', labelIds=[
                'INBOX', 'UNREAD'], includeSpamTrash='false', ).execute()
            messages = results.get('messages', [])
            if messages:
                for message in messages:
                    msg = Service.users().messages().get(
                        userId='me', id=message['id']).execute()
                    email_data = msg['payload']['headers']
                    for values in email_data:
                        name = values['name']
                        if name == 'From':
                            from_name = values['value']
                            for part in msg['payload']['parts']:
                                try:
                                    data = part['body']["data"]
                                    byte_code = base64.urlsafe_b64decode(data)

                                    text = byte_code.decode("utf-8")
                                    if (text.find("div") == -1):
                                        # print("This is the message: " + str(text))
                                        print(text)
                                        myAr = text.splitlines()
                                        print(myAr)
                                    # mark the message as read
                                    msg = Service.users().messages().modify(userId='me', id=message['id'], body={
                                        'removeLabelIds': ['UNREAD']}).execute()
                                except BaseException as error:
                                    pass
                return None
        except HttpError as error:
            print(f'An error occurred: {error}')
            return error
        time.sleep(6) # read mail for each 6 seconds