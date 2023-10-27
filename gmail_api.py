from __future__ import print_function

import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import mimetypes
import os
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

service = None                                  # keeps gmail service of user's gmail account
                                                # in case NOT ANONYMOUS

def buildService():
    """
        let user authenticate and authorize this app with Google

        then build gmail service
    """
    ############### try: ###############
    global service
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)

def checkAuthenticated():
    """
        check if user has authenticated and authorized

        returns account's profile and a boolean to show whether user has authenticated
    """
    global service
    try:
        profile = service.users().getProfile(userId='me').execute()
        return profile, True
    except HttpError as error:
        print('[Check authentication success] An error occurred: %s' % error)
        return None, False
    
def sendMail():
    print('alo')

################################################################
################################################################
# for sending gmail without authentication
import smtplib

s = smtplib.SMTP('smtp.gmail.com', 587)         # stmp session for sending mails anonymously
s.starttls()
s.login('chiemthoica@gmail.com', 'nrwd imjb rnak kotl')

def sendMailAnonymous(message):    
    # sending the mail
    s.sendmail("chiemthoica@gmail.com", "truongthanhtoan2003@gmail.com", message)
    
    # remember to terminate the session when close the app
    # s.quit()

# while True:
#     choice = input('choose y/n:')
#     if choice == 'y':
#         sendMailAnonymous("Message_you_need_to_send")
#     else:
#         s.quit()
#         break