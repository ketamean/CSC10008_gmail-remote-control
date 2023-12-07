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
from googleapiclient.http import MediaIoBaseDownload
################################################################
################################################################
SCOPES = ['https://mail.google.com/']

def authenticate(tokenFile):
    """
        let user authenticate and authorize this app with Google

        returns `Creds`
    """
    ############### try: ###############
    Creds = None
    tokenFile = 'config/' + tokenFile + '.json'
    if os.path.exists(tokenFile):
        Creds = Credentials.from_authorized_user_file(tokenFile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not Creds or not Creds.valid:
        if Creds and Creds.expired and Creds.refresh_token:
            Creds.refresh(Request())
        elif not os.path.exists('config/credentials.json') :
            print("Cannot find credentials file")
            return None
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            Creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenFile, 'w') as token:
            token.write(Creds.to_json())
    return Creds

def buildService(Creds):
    """
        returns gmail `Service`
    """
    return build('gmail', 'v1', credentials=Creds)

def checkAuthenticated(Creds):
    """
        check if user has authenticated and authorized

        returns profile_obj, True || error, False
    """
    try:
        Service = buildService(Creds)
        profile = Service.users().getProfile(userId='me').execute()
        return profile, True
    except HttpError as error:
        return error, False

def constructMail(receiver, sender, subject, msg_content):
    message = MIMEMultipart('alternative')
    message['To'] = receiver
    message['From'] = sender
    message['Subject'] = subject
    body = MIMEText(msg_content, 'plain')
    message.attach(body)
    return message

def sendMail(receiver, sender, subject, msg_content, Creds, threadId = None):
    """
        if there is msgId and threadId, the mail to be sent is a reply mail
        returns ([obj]msg obj, [str]error)
    """
    try:
        if not Creds:
            return None, "Creads do not exist: login again."
        Service = buildService(Creds)
        message = constructMail(
            receiver=receiver, sender=sender, subject=subject, msg_content=msg_content
        )
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message,
            'threadId': threadId
        }
        # pylint: disable=E1101
        send_message = (Service.users().messages().send
                        (userId="me", body=create_message).execute())
        # print(F'Message Id: {send_message["id"]}')
    except HttpError as err:
        # print(F'An error occurred: {error}')
        return None, err
    return send_message, None

def readRepliedMail(Creds, resultPath, threadId):
    """
        return [str]msg | None
    """
    try:
        if threadId == None:
            return None
        Service = buildService(Creds)
        threadData = getThreadData(Creds=Creds, threadId=threadId)
        messages = threadData.get('messages', [])
        if not messages:
            return None
        flag = 0
        for message in messages:
            lbls = message.get('labelIds', [])
            for lbl in lbls:
                if lbl == 'UNREAD':
                    flag = flag + 1
                    break
            if flag == 0: # there is no UNREAD msg
                continue  # skip to the next msg
            
            # now, this is an UNREAD mail
            # check the subject
            
            parts = message['payload'].get('parts', [])
            if parts == None:
                return None
            data = parts[0]['body'].get('data')
            if data:
                text = base64.urlsafe_b64decode(data).decode("utf-8")
                myAr = text.splitlines()
                if myAr[0] != 'This is the result':
                    continue
            else:
                return None
            for part in parts:
                att_id = part['body'].get('attachmentId')
                if not att_id:
                    continue
                att = Service.users().messages().attachments().get(userId='me', messageId=message['id'],id=att_id).execute()
                print(att['data'])
                file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
                #path = resultPath + part['filename']
                with open(os.path.join(resultPath, part['filename']), 'w') as f:
                    f.write(base64.b64decode(att['data']).decode('utf-8'))
                # mark the message as read
                tmp = (
                    Service.users()
                    .messages()
                    .modify(
                        userId="me",
                        id=message["id"],
                        body={"removeLabelIds": ["UNREAD"]},
                    )
                    .execute()
                )
            return True
    except HttpError as error:
        print(f'An error occurred: {error}')
        return error

def getThreadId(msg_obj):
    return msg_obj.get('threadId')

def getThreadData(Creds, threadId):
    Service = buildService(Creds)
    return Service.users().threads().get(userId="me", id=threadId).execute()