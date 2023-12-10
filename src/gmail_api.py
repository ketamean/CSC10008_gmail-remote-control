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
        double check if user has authenticated and authorized

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
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {'raw': encoded_message}
        if threadId:
            create_message['threadId'] = threadId
        # pylint: disable=E1101
        send_message = (Service.users().messages().send
                        (userId="me", body=create_message).execute())
        # print(F'Message Id: {send_message["id"]}')
    except HttpError as err:
        print(F'An error occurred: {err}')
        return None, err
    return send_message, None

def getMessagesInThread(Creds, threadId):
    try:
        threadData = getThreadData(Creds=Creds, threadId=threadId)
        messages = threadData.get('messages', [])
        return messages
    except Exception as error:
        print(f'An error occurred: {error}')

def readMail_command(Creds, resultPath, threadId):
    """
        read the reply mail that contains results of the sent request.

        [bool], [bool] | [error]
            True: if got and downloaded; otherwise, False
            
            None | [error]: False if there is no error
    """
    try:
        Service = buildService(Creds)
        messages = getMessagesInThread(Creds=Creds, threadId=threadId)
        if not messages:
            # an empty thread
            return False, False
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
            if not parts:
                # plain text mail => has no attachments or cannot obtain attachments
                return False, False
            flag = 0
            for part in parts:
                if part['filename'] == '':
                    data = part['body'].get('data')
                    if data:
                        text = base64.urlsafe_b64decode(data).decode("utf-8")
                        myAr = text.splitlines()
                        if myAr[0] != 'This is the result':
                            continue
                        else:
                            flag = flag + 1
                            break
                    else:
                        # there is a part without filename but has no `data` key => incorrect behavior
                        return False, False
            if flag == 0:
                # there is no text in the msg => invalid mail
                return False, False
            for part in parts:
                att_id = part['body'].get('attachmentId')
                if not att_id:
                    continue
                att = Service.users().messages().attachments().get(userId='me', messageId=message['id'],id=att_id).execute()
                file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
                #path = resultPath + part['filename']
                with open(os.path.join(resultPath, part['filename']), 'wb') as f:
                    f.write(file_data)
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
            return True, False
    except HttpError as error:
        print(f'An error occurred: {error}')
        return False, error
    return None, None

def readMail_register(Creds, threadId):
    try:
        Service = buildService(Creds)
        messages = getMessagesInThread(Creds=Creds, threadId=threadId)
        if not messages:
            # an empty thread
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
            # now, this is an UNREAD mail and flag == 1
            # check the subject
            parts = message['payload'].get('parts', [])
            if not parts:
                # plain text mail
                content = base64.urlsafe_b64decode(message['payload']['body']['data']).decode("utf-8")
                if content == 'added' or content == 'already existed':
                    markMsgAsRead(Creds=Creds, msg_obj=message)
                    return True
                else:
                    markMsgAsRead(Creds=Creds, msg_obj=message)
                    return False
            else:
                # multipart mail
                for part in parts:
                    data = part['body'].get('data')
                    if data:
                        content = base64.urlsafe_b64decode(data).decode("utf-8")
                        if content == 'added' or content == 'already existed':
                            markMsgAsRead(Creds=Creds, msg_obj=message)
                            return True
                        else:
                            markMsgAsRead(Creds=Creds, msg_obj=message)
                            return False
            markMsgAsRead(Creds=Creds, msg_obj=message)
        return None
    except HttpError as error:
        print(f'An error occurred: {error}')
        return error
    return None # regularize function's behaviour 

def markMsgAsRead(Creds, msg_obj):
    Service = buildService(Creds=Creds)
    tmp = (
        Service.users()
        .messages()
        .modify(
            userId="me",
            id=msg_obj["id"],
            body={"removeLabelIds": ["UNREAD"]},
        )
        .execute()
    )

def readMail_authentication(Creds, threadId):
    """
        fyi: authentication is a processed that is invoked when "loging in with user's gmail account" to ensure that account has already been registered.

        read the replied mail from server in authentication

        returns None | True | False | [str]error
    """
    try:
        Service = buildService(Creds)
        messages = getMessagesInThread(Creds=Creds, threadId=threadId)
        if not messages:
            # an empty thread
            return None
        
        for message in messages:
            flag = 0
            lbls = message.get('labelIds', [])
            for lbl in lbls:
                if lbl == 'UNREAD':
                    flag = flag + 1
                    break
            if flag == 0: # there is no UNREAD msg
                continue  # skip to the next msg
            # now, this is an UNREAD mail and flag == 1
            # check the subject
            parts = message['payload'].get('parts', [])
            if not parts:
                # plain text mail
                content = base64.urlsafe_b64decode(message['payload']['body']['data']).decode("utf-8")
                if content == 'YES':
                    markMsgAsRead(Creds=Creds, msg_obj=message)
                    return True
                elif content == 'NO':
                    markMsgAsRead(Creds=Creds, msg_obj=message)
                    return False
                else:
                    continue
            else:
                # multipart mail
                for part in parts:
                    data = part['body'].get('data')
                    if data:
                        content = base64.urlsafe_b64decode(data).decode("utf-8")
                        if content == 'YES':
                            markMsgAsRead(Creds=Creds, msg_obj=message)
                            return True
                        elif content == 'NO':
                            markMsgAsRead(Creds=Creds, msg_obj=message)
                            return False
                        else:
                            continue
    except HttpError as error:
        print(f'An error occurred: {error}')
        return error
    return None # regularize function's behaviour 


def getThreadId(msg_obj):
    try:
        return msg_obj.get('threadId')
    except:
        return None

def getThreadData(Creds, threadId):
    try:
        Service = buildService(Creds)
        return Service.users().threads().get(userId='me', id=threadId).execute()
    except:
        return None