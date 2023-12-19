import imaplib
import email
import os
import webbrowser
from email.header import decode_header
import service
import re

import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import mimetypes

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def imap_login():
    # establish connection with Gmail
    server ="imap.gmail.com"                     
    imap = imaplib.IMAP4_SSL(server, 993)
    
    # instantiate the username and the password
    username ="chiemthoica@gmail.com" 
    password ="gsno jiro wfgv esus"
    
    # login into the gmail account
    imap.login(username, password)
    return imap

def smtp_login():
    # establish connection
    email = "chiemthoica@gmail.com"
    password = "gsno jiro wfgv esus"
    smtp = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
    smtp.login(email, password)
    return smtp

def destructor(imap, smtp):
    imap.close()
    imap.log_out()
    smtp.quit()


def imap_search_mail(imap, search_criteria):
    imap.select("Inbox")

    ret, messages = imap.search(None, '(UNSEEN) ' + search_criteria)
    return (ret, messages) 

def check_mail(imap, ret, messages):
    nmessages = messages[0].decode().split(' ')
    if ret == "OK" and nmessages[0] != '':
        for num in nmessages:
            print("processing")
            res, msg = imap.fetch(str(num), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])

                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)

                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    #using Regex to validate mail
                    if From.find("<") != -1:
                        From = re.findall(r"<(.*?)>", From)
                        From = From[0]
                    #decode message-Id
                    messageId = msg["Message-Id"]
                    # if isinstance(messageId, bytes):
                    #     messageId = messageId.decode(encoding)
                    print("Subject:", subject)
                    print("From:", From)
                    print("Message-ID:", messageId)
                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # return text/plain emails and skip attachments
                                return body, From, messageId
                            elif "attachment" in content_disposition:
                                # download attachment
                                filename = part.get_filename()
                                if filename:
                                    folder_name = clean(subject)
                                    if not os.path.isdir(folder_name):
                                        # make a folder for this email (named after the subject)
                                        os.mkdir(folder_name)
                                    filepath = os.path.join(folder_name, filename)
                                    # download attachment and save it
                                    open(filepath, "wb").write(part.get_payload(decode=True))
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # return only text email parts
                            return body, From, messageId
                    if content_type == "text/html":
                        # if it's HTML, create a new HTML file and open it in browser
                        folder_name = clean(subject) 
                        if not os.path.isdir(folder_name):
                            # make a folder for this email (named after the subject)
                            os.mkdir(folder_name)
                        filename = "index.html"
                        filepath = os.path.join(folder_name, filename)
                        # write the file
                        open(filepath, "w").write(body)
                        # open in the default browser
                        webbrowser.open(filepath)
                    print("="*100)
    else:
        return "No mail"

def create_send_mail(smtp, type_of_work, to_mail, messageId, mail_content):
    message = MIMEMultipart()
    message["From"] = "chiemthoica@gmail.com"
    message["To"] = to_mail
    message["Subject"] = "PCRC " + type_of_work
    message["In-Reply-To"] = messageId
    message["References"] = messageId
    body = MIMEText(mail_content, "plain")
    message.attach(body)
    if (type_of_work == "working"):
        directory = os.listdir("Screenshot")
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

    smtp.send_mail("chiemthoica@gmail.com",to_mail, message.as_string())

def handle_work_list(work_list, from_mail):
    is_keylog = False
    is_anonymous = False
    if (from_mail == "chiemthoica@gmail.com"):
        is_anonymous = True
    for task in work_list:
        if task.find("[key_logger]") != -1:
            if iskeylog == False:
                iskeylog = True
                duration = task[13:]
                service.keylogger(int(duration))
        if task == "[screen_capture]":
            service.screenshot()
        if task == "[list_apps]":
            service.listRunningApplication()
        if task == "[list_processes]":
            service.listRunningProcess()
        if task == "[shut_down]" and is_anonymous == False:
            curDir = os.getcwd()
            saveDir = os.path.join(curDir, "ServiceOutput")
            id = len(os.listdir(saveDir))
            name = "shut_down" + str(id) + ".txt"
            outputDir = os.path.join(saveDir, name)

            with open(outputDir, "w") as file:
                file.write("The computer is shutting down")
            gmail_send_message_report(mail, msgId, threadId)
            service.shutdown()
            pass
        if task == "[log_out]" and is_anonymous == False:
            curDir = os.getcwd()
            saveDir = os.path.join(curDir, "ServiceOutput")
            id = len(os.listdir(saveDir))
            name = "log_out" + str(id) + ".txt"
            outputDir = os.path.join(saveDir, name)

            with open(outputDir, "w") as file:
                file.write("The computer is logging out")
            gmail_send_message_report(mail, msgId, threadId)
            service.logout()
            pass
        if task.find("[start_app]") != -1 and is_anonymous == False:
            appName = task[12:]
            service.openApplication(appName)
        if task.find("[close_app]") != -1 and is_anonymous == False:
            appName = task[12:]
            service.closeApplication(appName)
    gmail_send_message_report(mail, msgId, threadId)

def handle_server(imap, smtp):
    #check working mail
    ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC working")')
    body, from_mail, messagesId = check_mail(imap, ret, messages)
    if body == "No mail":
        return
    command = handle_work_list(body.splitlines(), from_mail)
    create_send_mail(smtp, "working", from_mail, messagesId)

imap = imap_login()

ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC working")')

check_mail(imap, ret, messages)