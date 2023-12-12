from __future__ import print_function

import base64
import os.path
import re

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

EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def authenticate(tokenFile = '', mkTokenFile = True):
    """
        let user authenticate and authorize this app with Google
        
        mkTokenFile: write the Creds to a token.json file

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
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            Creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        if mkTokenFile:
            with open(tokenFile, 'w') as token:
                token.write(Creds.to_json())
    return Creds

def buildService(Creds):
    """
        returns gmail `Service`
    """
    return build('gmail', 'v1', credentials=Creds)

def checkAuthenticated(Creds, Service):
    """
        double check if user has authenticated and authorized

        returns profile_obj, True || error, False
    """
    try:
        if not Service:
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

def sendMail(receiver, sender, subject, msg_content, Creds, Service, threadId = None):
    """
        if there is msgId and threadId, the mail to be sent is a reply mail
        returns ([obj]msg obj, [str]error)
    """
    try:
        if not Creds:
            return None, "Creads do not exist: login again."
        if not Service:
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

def getMessagesInThread(Creds, Service, threadId):
    try:
        threadData = getThreadData(Creds=Creds, Service=Service, threadId=threadId)
        messages = threadData.get('messages', [])
        return messages
    except Exception as error:
        print(f'An error occurred: {error}')

def markMsgAsRead(Creds, Service, msg_obj):
    if not Service:
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

def extractQuery(query):
    """
        query = "query_true|query_false"

        returns query_true, query_false
    """
    res = query.split('|')
    if len(res) == 2:
        return res
    elif len(res) == 1:
        return res[0], None
    return None, None

def notMatchQuery_readMailRegister(Creds, Service, msg_obj, content):
    if not Service:
        Service = buildService(Creds=Creds)
    if bool(re.match(EMAIL_PATTERN, content)) == False:
        markMsgAsRead(Creds=Creds, Service=Service, msg_obj=msg_obj)
    return None

def checkQuery(Creds, Service, msg_obj, content, query, task_if_not_match_query):
    """
        return True | False | None | [str]'continue'
    """
    q_true, q_false = extractQuery(query=query)
    if not q_false:
        myAr = content.splitlines()
        if myAr[0] != q_true:
            return 'continue'
        else:
            return 'download'
    else:
        if content == q_true:
            markMsgAsRead(Creds=Creds, Service=Service, msg_obj=msg_obj)
            return True
        elif content == q_false:
            markMsgAsRead(Creds=Creds, Service=Service, msg_obj=msg_obj)
            return False
        elif task_if_not_match_query:
            return task_if_not_match_query(Creds, Service, msg_obj, content)
        return 'continue'

def downloadAttachments(Creds, Service, msg_obj, resultPath):
    parts = msg_obj['payload'].get('parts')
    if not Service:
        Service = buildService(Creds)
    for part in parts:
        att_id = part['body'].get('attachmentId')
        if not att_id:
            continue
        att = Service.users().messages().attachments().get(userId='me', messageId=msg_obj['id'],id=att_id).execute()
        file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
        #path = resultPath + part['filename']
        with open(os.path.join(resultPath, part['filename']), 'wb') as f:
            f.write(file_data)
    markMsgAsRead(Creds=Creds, Service=Service, msg_obj=msg_obj)

def readMail(Creds, Service, threadId, query = '', task_if_not_match_query = None, work_w_plain_text_mail = True, resultPath = None):
    """
        query: [str], format "query_true|query_false"

        task_if_not_match_query: a function to do if mail content does not match
    """
    try:
        if not Service:
            Service = buildService(Creds)
        messages = getMessagesInThread(Creds=Creds, Service=Service, threadId=threadId)
        if not messages:
            # an empty thread
            return False
        flag = False
        for message in messages:
            lbls = message.get('labelIds', [])
            for lbl in lbls:
                if lbl == 'UNREAD':
                    flag = True
                    break
            if flag == False: # there is NO UNREAD msg
                continue  # skip to the next msg
            # now, this is an UNREAD mail, and flag == True
            parts = message['payload'].get('parts', [])
            if not parts: # plain text mail
                if work_w_plain_text_mail:
                    content = base64.urlsafe_b64decode(message['payload']['body']['data']).decode("utf-8")
                    # print('content read mail: ', content)
                    chk = checkQuery(Creds, Service, message, content, query, task_if_not_match_query)
                    if chk == 'continue':
                        continue
                    else:
                        return chk
                else:
                    return False
            else: # multipart mail
                for part in parts:
                    data = part['body'].get('data')
                    if data:
                        content = base64.urlsafe_b64decode(data).decode("utf-8")
                        # print('content read mail: ', content)
                        chk = checkQuery(Creds, Service, message, content, query, task_if_not_match_query)
                    if chk == 'continue':
                        continue
                    elif chk == 'download':
                        flag = 'download'
                        break
                    else:
                        return chk
            if flag == 'download':
                downloadAttachments(Creds, Service, message, resultPath)
                return True
    except HttpError as error:
        print(f'An error occurred: {error}')
        return str(error)
    return None # regularize function's behaviour 

def getThreadId(msg_obj):
    try:
        return msg_obj.get('threadId')
    except:
        return None

def getThreadData(Creds, Service, threadId):
    try:
        if not Service:
            Service = buildService(Creds)
        return Service.users().threads().get(userId='me', id=threadId).execute()
    except:
        return None