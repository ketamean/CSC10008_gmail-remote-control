from flask import Flask, render_template, url_for, request, redirect
from gmail_api import *
import os # operating system
import helper
import time
import threading

app = Flask('G-Controller')

# SERVER_GMAIL_ADDRESS = 'truongthanhtoan2003@gmail.com'
SERVER_GMAIL_ADDRESS = 'chiemthoica@gmail.com'
class SubjectMail:
    COMMAND = 'PCRC'
    REGISTER = 'PCRC register'
    LOGIN = 'PCRC authentication'

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
@app.route("/login/", methods=['GET', 'POST'])
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
    try:
        if helper.Info.Profile == None or helper.Flag.LoggedIn != True:
            return render_template("control.html", isAuthor=False)
        elif helper.Flag.SendMsgError:
            return render_template("control.html", isAuthor=True, send_error=True)
        else:
            return render_template("control.html", client_email=helper.Info.GmailAddress, send_error=None, isAuthor=True, isAnonymous=helper.Flag.Anonymous, timeouterror=helper.Flag.TimeOutRespond)
    except Exception as e:
        print(e)
        return redirect( url_for('login') )

@app.route("/send_mail_handler/", methods=['GET', 'POST'])
def send_mail_handler():
    try:
        msg = request.form.get('msg-content')
        if not msg:
            print('cannot find message content')
            helper.Flag.SendMsgError = True
            return redirect( url_for('control') )
        if len(msg) == 0:
            helper.Flag.SendMsgError = None
            return redirect( url_for('control') )
        msg = 'request\n' + msg

        chk_keylog = helper.checkKeylogger(msg)
        if chk_keylog == False:
            helper.Flag.SendMsgError = True
            return redirect( url_for('control') )
        helper.Info.Timer = helper.calcMaxWaitTime(msg)
        helper.Info.SentMsgObject, helper.Flag.SendMsgError = sendMail(
            receiver=SERVER_GMAIL_ADDRESS, sender=helper.Info.GmailAddress, subject=SubjectMail.COMMAND, msg_content=msg,
            Creds=helper.Info.Creds, #msgId='18c3fcc853e040cb'
        )
        if helper.Flag.SendMsgError:
            print('Msg Error: ', helper.Flag.SendMsgError)
            return redirect( url_for('control') )
        return redirect( url_for('get_response') )
    except Exception as e:
        print(e)
        return redirect( url_for('login') )
@app.route("/get_response/", methods=['GET', 'POST'])
def get_response():
    helper.Flag.TimeOutRespond = False
    #try:
    resultPath = helper.createResultDir()
    start_time = time.time()
    while True:
        if helper.duration(start_time=start_time, end_time=time.time()) >= helper.Info.Timer:
            helper.Info.SentMsgObject = None
            helper.Info.Timer = 0
            helper.Flag.TimeOutRespond = True
            return redirect( url_for('control') )
        flag, err = readMail_command(
            Creds=helper.Info.Creds, resultPath=resultPath, threadId=getThreadId(helper.Info.SentMsgObject)
        )
        if flag == True:
            break
        if flag == False and err != None:
            print(err)
            helper.makeTextFile(dir_path=resultPath, content=str(err), filename = "error")
            break
    helper.Info.SentMsgObject = None
    helper.Info.Timer = 0
    helper.openFolder(resultPath)
    return redirect( url_for('control') )
    # except Exception as e:
    #     print(e)
    #     return redirect( url_for('login') )