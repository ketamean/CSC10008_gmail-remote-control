import imaplib
import email
import os
import webbrowser
from email.header import decode_header
import service
import re
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
                                return body, From, subject, messageId
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
                            return body, From, subject, messageId
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

def handle_work_list(work_list, from_mail):
    is_keylog = False
    is_anonymous = False
    if (from_mail == "chiemthoica@gmail.com"):
        is_anonymous = True

def handle_server(imap):
    #check working mail
    ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC working")')
    body, from_mail, subject, messagesId = check_mail(imap, ret, messages)
    handle_work_list(body.splitlines(), from_mail)

imap = imap_login()

ret, messages = imap_search_mail(imap, '(SUBJECT "PCRC working")')

check_mail(imap, ret, messages)