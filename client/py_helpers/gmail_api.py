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

SERVICE = None                                  # keeps gmail service of user's gmail account
                                                # in case NOT ANONYMOUS

def buildService(tokenFile):
    """
        let user authenticate and authorize this app with Google

        then build gmail SERVICE
    """
    ############### try: ###############
    global SERVICE
    creds = None
    tokenFile = 'config/' + tokenFile + '.json'
    if os.path.exists(tokenFile):
        creds = Credentials.from_authorized_user_file(tokenFile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenFile, 'w') as token:
            token.write(creds.to_json())
    SERVICE = build('gmail', 'v1', credentials=creds)

def checkAuthenticated():
    """
        check if user has authenticated and authorized

        returns account's profile and a boolean to show whether user has authenticated
    """
    global SERVICE
    try:
        profile = SERVICE.users().getProfile(userId='me').execute()
        return profile, True
    except HttpError as error:
        print('[Check authentication success] An error occurred: %s' % error)
        return None, False

def sendMail():
    print('alo')

################################################################
################################################################