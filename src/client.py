from flask import Flask, render_template, url_for, request, redirect
import gmail_api
import os # operating system
import helper
import time
import threading

app = Flask('G-Controller')

def initEnvironment():
    helper.Info.ServerCreds = gmail_api.authenticate('token_anonymous')
    helper.Info.ServerProfile, _ = gmail_api.checkAuthenticated( helper.Info.ServerCreds )
initEnvironment()

SERVER_GMAIL_ADDRESS = 'chiemthoica@gmail.com'

class SubjectMail:
    COMMAND = 'PCRC working'
    REGISTER = 'PCRC register'
    LOGIN = 'PCRC authentication'

def initAccount(tokenFile):
    try:
        helper.Info.Creds = gmail_api.authenticate(tokenFile=tokenFile)
    except gmail_api.HttpError:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    helper.Info.Profile, auth = gmail_api.checkAuthenticated( helper.Info.Creds )
    if auth == False:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    helper.Info.GmailAddress = helper.Info.Profile.get('emailAddress')

@app.route("/register/", methods=['GET', 'POST'])
def register():
    helper.Flag.Register = False
    try:
        if os.path.exists('config/token.json'):
            os.remove('config/token.json')
        creds = gmail_api.authenticate(tokenFile='token')
    except gmail_api.HttpError:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    profile, auth = gmail_api.checkAuthenticated( creds )
    if auth == False:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    gmail_address = profile.get('emailAddress')
    msg_obj, err = gmail_api.sendMail(
        receiver=SERVER_GMAIL_ADDRESS, sender=SERVER_GMAIL_ADDRESS, subject=SubjectMail.REGISTER,
        msg_content=gmail_address, Creds=helper.Info.ServerCreds
    )
    if err:
        print('Regiter | send err: ', err)
        return redirect( url_for('login') )
    res = None
    while True:
        res = gmail_api.readMail_register(
            Creds=helper.Info.ServerCreds, threadId=gmail_api.getThreadId(msg_obj)
        )
        if res == True:
            break
        time.sleep(3)
    if res == True:
        helper.Info.Creds = creds
        helper.Info.Profile = profile
        helper.Info.GmailAddress = gmail_address
        helper.Flag.Register = True
        helper.Flag.Anonymous = None
        helper.Flag.LoggedIn = True
        helper.Info.HTMLFileName = helper.FULL_HTML_FILENAME
        return redirect( url_for(control) )
    else:
        helper.Flag.Register = False
        print("Register error: ", res)
    return redirect( url_for('login') )

@app.route("/rememberUser_YES", methods=['GET', 'POST'])
def rememberUser_YES():
    helper.Flag.RememberAccount = True
    return redirect( url_for('login') )

@app.route("/rememberUser_NO", methods=['GET', 'POST'])
def rememberUser_NO():
    helper.Flag.RememberAccount = False
    return redirect( url_for('login') )

@app.route("/", methods=['GET', 'POST'])
@app.route("/login/", methods=['GET', 'POST'])
def login():
    helper.Flag.LoginAuthentication = None
    helper.Info.HTMLFileName = None
    helper.resetUserInfo(del_token=not helper.Flag.RememberAccount)
    if helper.Flag.AuthenState == 'failed':
        helper.Flag.AuthenState = None
        if helper.Flag.Anonymous == True:
            helper.Flag.Anonymous = None
            return render_template(
                "login.html", successAuthen=False, isAnonymous=True, remember_me=helper.Flag.RememberAccount
            )
        else:
            return render_template(
                "login.html", successAuthen=False, isAnonymous=False, remember_me=helper.Flag.RememberAccount
            )
    elif (helper.Flag.Register != False and helper.Flag.Register != True):
        # helper.Flag.Register is containing an error while register
        return render_template(
            "login.html", register_error=True, remember_me=helper.Flag.RememberAccount
        )
    # else:
    return render_template("login.html", remember_me=helper.Flag.RememberAccount)

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    helper.Flag.Anonymous = True
    if not os.path.exists('config/token_anonymous.json'):
        helper.Info.ServerProfile = helper.Info.ServerCreds = None
        print('cannot find /config/token_anonymous.json')
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    
    helper.Info.Profile = helper.Info.ServerProfile
    helper.Info.Creds = helper.Info.ServerCreds

    helper.Flag.LoggedIn = True
    helper.Info.HTMLFileName = helper.ANONYMOUS_HTML_FILENAME
    return redirect( url_for('control') )

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    helper.Flag.Anonymous = None
    helper.Flag.LoginAuthentication = None
    initAccount('token')
    # msg_obj, err = gmail_api.sendMail(
    #     receiver=SERVER_GMAIL_ADDRESS, sender=SERVER_GMAIL_ADDRESS, subject='PCRC authentication',
    #     msg_content=helper.Info.GmailAddress, Creds=helper.Info.ServerCreds
    # )
    # if err:
    #     print('Cannot authenticate account.')
    #     return redirect( url_for('login') )
    # auth = None
    # while True:
    #     auth = gmail_api.readMail_authentication(
    #         Creds=helper.Info.ServerCreds, threadId=gmail_api.getThreadId(msg_obj=msg_obj)
    #     )
    #     if auth != None:
    #         break
    #     time.sleep(3)
    # print(auth)
    auth = True             # delete this line if you want to run the above block of code
    if not auth:
        helper.Flag.AuthenState = 'failed'
        helper.Flag.Anonymous = False
        return redirect( url_for('login') )
    elif auth == False:
        helper.Flag.LoginAuthentication = False
    elif auth == True:
        helper.Flag.LoggedIn = True
        helper.Info.HTMLFileName = helper.FULL_HTML_FILENAME
        return redirect( url_for('control') )

@app.route("/control/", methods=['GET', 'POST'])
def control():
    req_success = helper.Flag.SuccessRequest
    helper.Flag.SuccessRequest = False
    try:
        if helper.Info.Profile == None or helper.Flag.LoggedIn != True:
            return render_template(helper.Info.HTMLFileName, isAuthor=False)
        elif helper.Flag.SendMsgError:
            helper.Flag.SendMsgError = None
            return render_template(
                helper.Info.HTMLFileName, send_error=True, client_email=helper.Info.GmailAddress,
                isAuthor=True, isAnonymous=helper.Flag.Anonymous, timeouterror=helper.Flag.TimeOutRespond
            )
        else:
            return render_template(
                helper.Info.HTMLFileName, client_email=helper.Info.GmailAddress, send_error=None, isAuthor=True,
                isAnonymous=helper.Flag.Anonymous, timeouterror=helper.Flag.TimeOutRespond, successRequest=req_success
            )
    except Exception as e:
        print(e)
        return redirect( url_for('login') )

@app.route("/send_mail_handler/", methods=['GET', 'POST'])
def send_mail_handler():
    helper.Flag.SuccessRequest = False
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
        # helper.Info.Timer = helper.calcMaxWaitTime(msg)
        helper.Info.SentMsgObject, helper.Flag.SendMsgError = gmail_api.sendMail(
            receiver=SERVER_GMAIL_ADDRESS, sender=helper.Info.GmailAddress, subject=SubjectMail.COMMAND,
            msg_content=msg, Creds=helper.Info.Creds
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
    print('threadId: ', gmail_api.getThreadId(helper.Info.SentMsgObject))
    # helper.Flag.TimeOutRespond = False
    try:
        resultPath = helper.createResultDir()
        # start_time = time.time()
        while True:
            # if helper.duration(start_time=start_time, end_time=time.time()) >= helper.Info.Timer:
            #     helper.Info.SentMsgObject = None
            #     helper.Info.Timer = 0
            #     helper.Flag.TimeOutRespond = True
            #     return redirect( url_for('control') )
            flag, err = gmail_api.readMail_command(
                Creds=helper.Info.Creds, resultPath=resultPath,
                threadId=gmail_api.getThreadId(helper.Info.SentMsgObject),
            )
            if flag == True:
                break
            if flag == False and err != False:
                print(err)
                helper.makeTextFile(dir_path=resultPath, content=str(err), filename = "error")
                break
            time.sleep(2)
        helper.Info.SentMsgObject = None
        helper.Info.Timer = 0
        helper.Flag.SuccessRequest = True
        helper.openFolder(resultPath)
        return redirect( url_for('control') )
    except Exception as e:
        print(e)
        return redirect( url_for('login') )