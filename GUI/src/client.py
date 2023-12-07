from flask import Flask, render_template, url_for, request, redirect
from gmail_api import *
import os # operating system
import helper

app = Flask('G-Controller')

# SERVER_GMAIL_ADDRESS = 'truongthanhtoan2003@gmail.com'
SERVER_GMAIL_ADDRESS = 'chiemthoica@gmail.com'
SUBJECT_MAIL = 'PCRC ne hehe'

def initAccount(tokenFile):
    try:
        helper.Info.Creds = authenticate(tokenFile)
    except HttpError:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    helper.Info.Profile, auth = checkAuthenticated( helper.Info.Creds )
    if auth == False:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    helper.Info.GmailAddress = helper.Info.Profile.get('emailAddress')

@app.route("/", methods=['GET', 'POST'])
def login():
    helper.resetUserInfo()
    if helper.Flag.AuthenState == 'failed':
        helper.Flag.AuthenState = None
        if helper.Flag.Anonymous == True:
            helper.Flag.Anonymous = None
            return render_template("login.html", successAuthen=False, isAnonymous=True)
        else:
            return render_template("login.html", successAuthen=False, isAnonymous=False)
    else:
        return render_template("login.html")

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    helper.Flag.Anonymous = True
    if not os.path.exists('config/token_anonymous.json'):
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    initAccount('token_anonymous')
    helper.Flag.LoggedIn = True
    return redirect( url_for('control') )

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    helper.Flag.Anonymous = None
    initAccount('token')
    helper.Flag.LoggedIn = True
    return redirect( url_for('control') )

@app.route("/control/", methods=['GET', 'POST'])
def control():
    if helper.Info.Profile == None or helper.Flag.LoggedIn != True:
        return render_template("control.html", isAuthor=False)
    elif helper.Flag.SendMsgError:
        return render_template("control.html", isAuthor=True, send_error=True)
    else:
        return render_template("control.html", client_email=helper.Info.GmailAddress, send_error=None, isAuthor=True, isAnonymous=helper.Flag.Anonymous)

@app.route("/send_mail_handler/", methods=['GET', 'POST'])
def send_mail_handler():
    msg = request.form.get('msg-content')
    if not msg:
        print('cannot find message content')
        helper.Flag.SendMsgError = True
        return redirect( url_for('control') )
    if len(msg) == 0:
        helper.Flag.SendMsgError = None
        return redirect( url_for('control') )
    msg = 'request\n' + msg
    if helper.checkKeylogger(msg) == False:
        helper.Flag.SendMsgError = True
        return redirect( url_for('control') )
    helper.Info.SendMsgObject, helper.Flag.SendMsgError = sendMail(
        receiver=SERVER_GMAIL_ADDRESS, sender=helper.Info.GmailAddress, subject=SUBJECT_MAIL, msg_content=msg,
        Creds=helper.Info.Creds, #msgId='18c3fcc853e040cb'
    )
    if helper.Flag.SendMsgError:
        print('Msg Error: ', helper.Flag.SendMsgError)
        return redirect( url_for('control') )
    return redirect( url_for('get_response') )

@app.route("/get_response/", methods=['GET', 'POST'])
def get_response():
    resultPath = helper.createResultDir()
    while readRepliedMail(Creds=helper.Info.Creds, resultPath=resultPath, threadId=getThreadId(helper.Info.SendMsgObject)) != True:
        pass
    helper.Info.SendMsgObject = None
    helper.openFolder(resultPath)
    return redirect( url_for('control') )

w_attachment = {
        'id': '18c330e54537ee01', 'historyId': '90623',
        'messages': [
            {
                'id': '18c333571559bce4', 'threadId': '18c333571559bce4',
                'labelIds': ['UNREAD', 'SENT', 'INBOX'], 'snippet': '[screen_capture]',
                'payload': {
                    'partId': '', 'mimeType': 'multipart/alternative', 'filename': '',
                    'headers': [
                        {'name': 'Received', 'value': 'from 275361750661 named unknown by gmailapi.google.com with HTTPREST; Sun, 3 Dec 2023 21:03:09 -0800'},
                        {'name': 'Content-Type', 'value': 'multipart/alternative; boundary="===============7253091662189088045=="'},
                        {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'To', 'value': 'chiemthoica@gmail.com'}, {'name': 'From', 'value': 'chiemthoica@gmail.com'},
                        {'name': 'Subject', 'value': 'PCRC'}, {'name': 'Date', 'value': 'Sun, 3 Dec 2023 21:03:09 -0800'},
                        {'name': 'Message-Id', 'value': '<CANDETtmgaPvxuVUpEkXb7ND3CxW=Muszj_7xRtNwT3nzCveq8w@mail.gmail.com>'}
                    ],
                    'body': {'size': 0},
                    'parts': [
                        {
                            'partId': '0', 'mimeType': 'text/plain', 'filename': '',
                            'headers': [
                                {'name': 'Content-Type', 'value': 'text/plain; charset="us-ascii"'},
                                {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}
                            ],
                            'body': {'size': 16, 'data': 'W3NjcmVlbl9jYXB0dXJlXQ=='}
                        },
                        {
                            'partId': '1',
                            'mimeType': 'application/octet-stream',
                            'filename': 'graph.png',
                            'headers': [
                                {'name': 'Content-Type', 'value': 'application/octet-stream; Name="graph.png"'},
                                {'name': 'MIME-Version', 'value': '1.0'},
                                {'name': 'Content-Transfer-Encoding', 'value': 'base64'},
                                {'name': 'Content-Disposition', 'value': 'attachment; filename="graph.png"'}
                            ],
                            'body': {
                                'attachmentId': 'ANGjdJ_iokCVRR3TbOzt3_DvC4coujmzTRXVKSbsXf__A09Vq3WHop97bUomf4nmEi0o8n9nv69EiMNlrNhayR1vg9C-RSNaBvguoTH_Q5YZud9w1m-Pz7TEURfCo2YpJ0ZDMrqwmHh-UoAHqGVL7D6W54DjEJZNmCBRhVtl-uWa3xat-BCq9Mrnih7YN0rXL-nOWi70IURLAw8wKXMmZjaXMMen0_fex7PqFbU2SqcHXuDvFJAhhozVtcR7Tf2_femcZeoMKI94rFgSW2D9fWxQVLIWNzzm9b8gQufrU3eJhbnI-P3Wxwm6mE_eEz0h0xisrdm__h1FSOF3GBtBlmpabqvCVkDFVo-jr79MjtCS9xa5i-N5-H1Vc4wXM3n78kOCCjn8goM-DyGSwRV2',
                                'size': 27383
                            }
                        }
                    ]
                },
                'sizeEstimate': 37810, 'historyId': '49400', 'internalDate': '1701666189000'
            }  
        ]
}