from __future__ import print_function

import os.path
import base64
import time
import service
import mimetypes

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
            res = service.keylogger()
            resString = ""
            for keyword in res:
                resString = resString + keyword
            print(resString)
        if task == "[screen_capture]":
            service.screenshot()
        if task == "[list_app]":
            service.listRunningApplication()
        if task == "[list_processes]":
            service.listRunningProcess()


# def testoutput():
#     print("hello may cau")


def CheckMail(creds):
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
                        if msg["payload"].get("parts", -1) != -1:
                            for part in msg["payload"]["parts"]:
                                try:
                                    data = part["body"]["data"]
                                    byte_code = base64.urlsafe_b64decode(data)

                                    text = byte_code.decode("utf-8")
                                    if text.find("div") == -1:
                                        # print("This is the message: " + str(text))
                                        myAr = text.splitlines()
                                        print(myAr)
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
                        else:
                            data = msg["payload"]["body"]["data"]
                            byte_code = base64.urlsafe_b64decode(data)

                            text = byte_code.decode("utf-8")
                            print(text)
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

    except HttpError as error:
        print(f"An error occurred: {error}")


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

    CheckMail(creds)


if __name__ == "__main__":
    main()
