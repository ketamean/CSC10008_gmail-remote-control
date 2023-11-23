from __future__ import print_function

import os.path
import base64
import service
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import mimetypes
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]


def handle(myAr, mail):
    print("Handling Mail")
    for task in myAr:
        if task.find("[key_logger]") != -1:
            duration = task[13:]
            service.keylogger(int(duration))
        if task == "[screen_capture]":
            service.screenshot()
        if task == "[list_app]":
            service.listRunningApplication()
        if task == "[list_processes]":
            service.listRunningProcess()
        if task == "[shut_down]":
            curDir = os.getcwd()
            saveDir = os.path.join(curDir, "ServiceOutput")
            id = len(os.listdir(saveDir))
            name = "shut_down" + str(id) + ".txt"
            outputDir = os.path.join(saveDir, name)

            with open(outputDir, "w") as file:
                file.write("The computer is shutting down")
            gmail_send_message(mail)
            service.shutdown()
        if task == "[log_out]":
            curDir = os.getcwd()
            saveDir = os.path.join(curDir, "ServiceOutput")
            id = len(os.listdir(saveDir))
            name = "log_out" + str(id) + ".txt"
            outputDir = os.path.join(saveDir, name)

            with open(outputDir, "w") as file:
                file.write("The computer is logging out")
            gmail_send_message(mail)
            service.logout()
        if task.find("[start_app]") != -1:
            appName = task[12:]
            service.openApplication(appName)
        if task.find("[close_app]") != -1:
            appName = task[12:]
            service.closeApplication(appName)
    gmail_send_message(mail)


# def testoutput():
#     print("hello may cau")


def gmail_send_message(mail):
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEMultipart()

        message["To"] = mail
        message["From"] = "chiemthoica@gmail.com"
        message["Subject"] = "Computer Remote Control Report"
        content = "This is the result"
        body = MIMEText(content, "plain")
        message.attach(body)

        directory = os.listdir("Screenshot")
        # print(directory)
        for file in directory:
            attachment_filename = file
            if attachment_filename == "save_folder.txt":
                continue
            # guessing the MIME type
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            maintype, subtype = type_subtype.split("/")

            with open(os.path.join("Screenshot", attachment_filename), "rb") as fp:
                part = MIMEApplication(
                    fp.read(),
                    Name=os.path.basename(
                        os.path.join("Screenshot", attachment_filename)
                    ),
                )
                part["Content-Disposition"] = 'attachment; filename="{}"'.format(
                    os.path.basename(os.path.join("Screenshot", attachment_filename))
                )
            message.attach(part)
            os.remove(os.path.join("Screenshot", attachment_filename))

        directory = os.listdir("ServiceOutput")
        for file in directory:
            attachment_filename = file
            if attachment_filename == "save_folder.txt":
                continue
            # guessing the MIME type
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            maintype, subtype = type_subtype.split("/")

            with open(os.path.join("ServiceOutput", attachment_filename), "rb") as fp:
                part = MIMEApplication(
                    fp.read(),
                    Name=os.path.basename(
                        os.path.join("ServiceOutput", attachment_filename)
                    ),
                )
                part["Content-Disposition"] = 'attachment; filename="{}"'.format(
                    os.path.basename(os.path.join("ServiceOutput", attachment_filename))
                )
            message.attach(part)
            os.remove(os.path.join("ServiceOutput", attachment_filename))

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


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
                        # using RegEx
                        from_data = re.findall(r"<(.*?)>", values["value"])
                        from_mail = from_data[0]
                        print(from_mail)
                        if msg["payload"].get("parts", -1) != -1:
                            for part in msg["payload"]["parts"]:
                                try:
                                    data = part["body"]["data"]
                                    byte_code = base64.urlsafe_b64decode(data)

                                    text = byte_code.decode("utf-8")
                                    if text.find("div") == -1:
                                        myAr = text.splitlines()
                                        print(myAr)
                                        handle(myAr, from_mail)
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
                            myAr = text.splitlines()
                            handle(myAr, from_mail)
                            # mark the message as read, handle and send gmail message
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

    return creds


if __name__ == "__main__":
    main()
