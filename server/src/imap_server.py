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
    imap.select("inbox", readonly=False)
    return imap

def smtp_login():
    # establish connection
    email = "chiemthoica@gmail.com"
    password = "gsno jiro wfgv esus"
    smtp = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
    smtp.login(email, password)
    return smtp

def mail_list_login():
    my_mail_list = []
    with open("usermail.txt", "r") as mailFile:
            for mail in mailFile:
                my_mail_list.append(mail.rstrip())
    return my_mail_list

def destructor(imap, smtp, my_mail_list):
    imap.close()
    imap.logout()
    smtp.quit()
    with open("usermail.txt", "w") as mailFile:
        for mail in my_mail_list:
            mailFile.write(mail + "\n")



def imap_search_mail(imap, search_criteria):
    ret, messages = imap.search(None, '(UNSEEN) ' + search_criteria)
    return (ret, messages) 

def validate_body(body, type_of_work):
    if type_of_work == "working":
        temp = body.splitlines()
        if temp[0] == "request":
            return True
    if type_of_work == "register":
        if body.find("already existed") == -1 and body.find("added") == -1:
            return True
    if type_of_work == "login":
        if body.find("YES") == -1 and body.find("NO") == -1:
            return True
    return False

def check_mail(imap, ret, messages, type_of_work):
    nmessages = messages[0].decode().split(' ')
    if ret == "OK" and nmessages[0] != '':
        for num in nmessages:
            res, msg = imap.fetch(str(num), "(RFC822)")
            imap.store(str(num), '-FLAGS', '\\Seen')
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
                    print("From:", From)
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
                                
                                if validate_body(body, type_of_work):
                                    imap.store(str(num), '+FLAGS', '\\Seen')
                                    return body, From, messageId
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # return only text email parts
                            if validate_body(body, type_of_work):
                                imap.store(str(num), '+FLAGS', '\\Seen')
                                return body, From, messageId
                    print("="*100)
    return "No mail","",""
    

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

    smtp.sendmail("chiemthoica@gmail.com",to_mail, message.as_string())

def handle_work_list(work_list, from_mail):
    print("handle work")
    is_keylog = False
    is_anonymous = False
    if (from_mail == "chiemthoica@gmail.com"):
        is_anonymous = True
    for task in work_list:
        if task.find("[key_logger]") != -1:
            if is_keylog == False:
                is_keylog = True
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
            return "[shut_down]"
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
            return "[log_out]"
            pass
        if task.find("[start_app]") != -1 and is_anonymous == False:
            appName = task[12:]
            service.openApplication(appName)
        if task.find("[close_app]") != -1 and is_anonymous == False:
            appName = task[12:]
            service.closeApplication(appName)
    return "nothing"

def handle_register_mail(mail, mail_list):
    is_appear = False
    for old_mail in mail_list:
        if old_mail == mail:
            is_appear = True
    if is_appear == True:
        return "already existed"
    else:
        mail_list.append(mail)
        return "added"

def handle_login_mail(mail, mail_list):
    is_appear = False
    for old_mail in mail_list:
        if old_mail == mail:
            is_appear = True
            break 
    if is_appear:
        return "YES"
    return "NO"

def server_checking(imap, smtp, mail_list):
    #check working mail
    ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC working")')
    body, from_mail, messagesId = check_mail(imap, ret, messages, "working")
    print(body)
    if body != "No mail":
        command = handle_work_list(body.splitlines(), from_mail)
        create_send_mail(smtp, "working", from_mail, messagesId, "This is the result")
        if (command == "[shut_down]"):
            service.shutdown()
        elif (command == "[log_out]"):
            service.logout()

    #check register mail
    ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC register")')
    body, from_mail, messageId = check_mail(imap, ret, messages, "register")
    if body != "No mail":
        mail_content = handle_register_mail(body.rstrip(), mail_list)
        create_send_mail(smtp, "register", from_mail, messageId, mail_content)

    #check login mail
    ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC authentication")')
    body, from_mail, messageId = check_mail(imap, ret, messages, "login")
    if body != "No mail":
        mail_content = handle_login_mail(body.rstrip(), mail_list)
        print(body.rstrip())
        create_send_mail(smtp, "authentication", from_mail, messageId, mail_content)



def operate_server(imap, smtp, my_mail_list):
    server_checking(imap, smtp, my_mail_list)
    print("I am checking mail")

# imap = imap_login()
# smtp = smtp_login()
# my_mail_list = mail_list_login()
# operate_server(imap, smtp, my_mail_list)
# destructor(imap, smtp, my_mail_list)