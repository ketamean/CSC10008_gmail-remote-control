from flask import Flask, render_template, url_for, request, redirect
from gmail_api import *
import os

app = Flask(__name__)

user_info = {
    'gmailAddress': None,   # client's Gmail address
    'profile': None,        # is reserved for future use
    'Service': None,
    'Creds': None,
}

flags = {
    'authenticationState': None,            # keep the state of authentication
    'sendMsgError': None,                   # error caused by sending messages; is None if there is no error
    'msg_object': None,                     # Message object, including: 'id', 'threadId' and 'labelIds'
    'anonymous': None,                      # mark if user is using app anonymously, True | None
    'logged_in': None
}

# SERVER_GMAIL_ADDRESS = 'truongthanhtoan2003@gmail.com'
SERVER_GMAIL_ADDRESS = 'chiemthoica@gmail.com'
SUBJECT_MAIL = 'PCRC'

def initAccount(tokenFile):
    try:
        user_info['Creds'] = authenticate(tokenFile)
        user_info['Service'] = buildService( user_info['Creds'] )
    except HttpError:
        flags['authenticationState'] = 'failed'
        return redirect( url_for('login') )
    user_info['profile'], auth = checkAuthenticated( user_info['Service'] )
    if auth == False:
        flags['authenticationState'] = 'failed'
        return redirect( url_for('login') )
    user_info['gmailAddress'] = user_info['profile'].get('emailAddress')

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    flags['anonymous'] = True
    if not os.path.exists('config/token_anonymous.json'):
        flags['authenticationState'] = 'failed'
        return redirect( url_for('login') )
    initAccount('token_anonymous')
    flags['logged_in'] = True
    return redirect( url_for('control') )

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    flags['anonymous'] = None
    initAccount('token')
    flags['logged_in'] = True
    return redirect( url_for('control') )

@app.route("/control/", methods=['GET', 'POST'])
def control():
    if flags['logged_in'] != True:
        return redirect( url_for('login') )
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
    flags['msg_object'], flags['sendMsgError'] = sendMail(
        receiver=SERVER_GMAIL_ADDRESS, sender=user_info['gmailAddress'], subject=SUBJECT_MAIL, msg_content=msg,
        Creds=user_info['Creds'], Service=user_info['Service']
    )
    # print(flags['msg_object'])
        # msg_object.id
        # msg_object.threadId
    if flags['sendMsgError'] == None:
        return redirect( url_for('response') )

@app.route("/response/", methods=['GET', 'POST'])    
def response():
    return render_template('response.html')

def resetUserInfo():
    user_info['gmailAddress'] = None
    user_info['profile'] = None
    if os.path.exists('config/token.json'):
        os.remove('config/token.json')
    user_info['Service'] = None
    user_info['Creds'] = None
    flags['logged_in'] = None

@app.route("/", methods=['GET', 'POST'])
def login():
    resetUserInfo()
    if flags['authenticationState'] == 'failed':
        flags['authenticationState'] = None
        if flags['anonymous'] == True:
            flags['anonymous'] = None
            return render_template("login.html", successAuthen=False, isAnonymous=True)
        else:
            return render_template("login.html", successAuthen=False, isAnonymous=False)
    else:
        return render_template("login.html")