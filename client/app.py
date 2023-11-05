from flask import Flask, render_template, url_for, request, redirect
from py_helpers import gmail_api
import os

app = Flask(__name__)

user_info = {
    'gmailAddress': None,   # client's Gmail address
    'profile': None,        # is reserved for future use
}

flags = {
    'authenticationState': None,            # keep the state of authentication
    'sendMsgError': None,                   # error caused by sending messages; is None if there is no error
    'msg_object': None,                     # Message object, including: 'id', 'threadId' and 'labelIds'
    'anonymous': None,                      # mark if user is using app anonymously, True | None
}

# SERVER_GMAIL_ADDRESS = 'truongthanhtoan2003@gmail.com'
SERVER_GMAIL_ADDRESS = 'chiemthoica@gmail.com'

def initAccount(tokenFile):
    try:
        gmail_api.authenticate(tokenFile)
        gmail_api.buildService()
    except gmail_api.HttpError:
        flags['authenticationState'] = 'failed'
        return redirect( url_for('login') )
    user_info['profile'], auth = gmail_api.checkAuthenticated()
    if auth == False:
        flags['authenticationState'] = 'failed'
        return redirect( url_for('login') )
    user_info['gmailAddress'] = user_info['profile'].get('emailAddress')

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    flags['anonymous'] = True
    initAccount('token_anonymous')
    return redirect( url_for('control') )

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    flags['anonymous'] = None
    initAccount('token')
    return redirect( url_for('control') )

@app.route("/control/", methods=['GET', 'POST'])
def control():
    if user_info['profile'] == None:
        return render_template("control.html", isAuthor=False)
    elif flags['sendMsgError']:
        err = flags['sendMsgError']
        flags['sendMsgError'] = None
        return render_template("control.html", send_error=err, isAuthor=True)
    else:
        return render_template("control.html", client_email=user_info['gmailAddress'], send_error=None, isAuthor=True)

@app.route("/send_mail_handler/", methods=['GET', 'POST'])
def send_mail_handler():
    msg = request.form['msg-content']
    if len(msg) == 0:
        return redirect( url_for('control') )
    flags['msg_object'], flags['sendMsgError'] = gmail_api.sendMail(
        receiver=SERVER_GMAIL_ADDRESS, sender=user_info['gmailAddress'], subject=SUBJECT_MAIL, msg_content=msg
    )
    # print(flags['msg_object'])
        # msg_object.id
        # msg_object.threadId
    if flags['sendMsgError'] == None:
        return redirect( url_for('response') )

@app.route("/response/", methods=['GET', 'POST'])    
def response():
    return render_template('response.html')


from py_helpers.gmail_api import *
def resetUserInfo():
    user_info['gmailAddress'] = None
    user_info['profile'] = None
    flags['anonymous'] = None
    flags['authenticationState'] = None
    if os.path.exists('config/token.json'):
        os.remove('config/token.json')
    
    global Service, Creds
    Service = None
    Creds = None

@app.route("/", methods=['GET', 'POST'])
def login():
    resetUserInfo()
    if flags['authenticationState'] == 'failed':
        flags['authenticationState'] = None
        if flags['anonymous'] == True:
            return render_template("login.html", successAuthen=False, isAnonymous=True)
        else:
            return render_template("login.html", successAuthen=False, isAnonymous=False)
    else:
        return render_template("login.html", successAuthen=True)