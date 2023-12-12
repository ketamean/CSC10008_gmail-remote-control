from flask import Flask, render_template, url_for, request, redirect
import gmail_api
import os
import helper
import time

app = Flask('G-Controller')

def initEnvironment():
    helper.Info.ServerCreds = gmail_api.authenticate('token_anonymous')
    helper.Info.ServerService = gmail_api.buildService(helper.Info.ServerCreds)
    helper.Info.ServerProfile, _ = gmail_api.checkAuthenticated( helper.Info.ServerCreds, helper.Info.ServerService )
initEnvironment()

SERVER_GMAIL_ADDRESS = 'chiemthoica@gmail.com'

class SubjectMail:
    COMMAND = 'PCRC working'
    REGISTER = 'PCRC register'
    LOGIN = 'PCRC authentication'

def initAccount(tokenFile):
    try:
        helper.Info.Creds = gmail_api.authenticate(tokenFile=tokenFile)
        helper.Info.Service = gmail_api.buildService(helper.Info.Creds)
    except gmail_api.HttpError:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    helper.Info.Profile, auth = gmail_api.checkAuthenticated( helper.Info.Creds, helper.Info.Service )
    if auth == False:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    helper.Info.GmailAddress = helper.Info.Profile.get('emailAddress')

@app.route("/register/", methods=['GET', 'POST'])
def register():
    helper.Flag.SuccessRequest = False
    helper.Flag.Register = False
    try:
        if os.path.exists('config/token.json'):
            os.remove('config/token.json')
        creds = gmail_api.authenticate(tokenFile='token')
        service = gmail_api.buildService(creds)
    except gmail_api.HttpError:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    profile, auth = gmail_api.checkAuthenticated( creds, service )
    if auth == False:
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    gmail_address = profile.get('emailAddress')
    msg_obj, err = gmail_api.sendMail(
        receiver=SERVER_GMAIL_ADDRESS, sender=SERVER_GMAIL_ADDRESS, subject=SubjectMail.REGISTER,
        msg_content=gmail_address, Creds=helper.Info.ServerCreds, Service=helper.Info.ServerService
    )
    print('register: sent')
    if err:
        print('Regiter | send err: ', err)
        return redirect( url_for('login') )
    reg = None
    while True:
        reg = gmail_api.readMail(
            Creds=helper.Info.ServerCreds, Service=helper.Info.ServerService, threadId=gmail_api.getThreadId(msg_obj=msg_obj),
            query="added|already existed",  task_if_not_match_query=gmail_api.notMatchQuery_readMailRegister
        )
        if reg != None:
            break
        time.sleep(2)
    if reg == True or reg == False:
        helper.Info.Creds = creds
        helper.Info.Service = service
        helper.Info.Profile = profile
        helper.Info.GmailAddress = gmail_address
        helper.Flag.Register = True
        helper.Flag.Anonymous = None
        helper.Flag.LoggedIn = True
        helper.Info.HTMLFileName = helper.FULL_HTML_FILENAME
        return redirect( url_for('control') )
    else:
        helper.Flag.Register = False
        print("Register error: ", reg)
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
    elif helper.Flag.LoginAuthentication == False:
        helper.Flag.LoginAuthentication = None
        return render_template(
            "login.html", remember_me=helper.Flag.RememberAccount, authen_login=False
        )
    # else:
    return render_template("login.html", remember_me=helper.Flag.RememberAccount)

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    helper.Flag.Anonymous = True
    if not os.path.exists('config/token_anonymous.json'):
        helper.Info.ServerProfile = helper.Info.ServerCreds = None
        print('control_anonymous: cannot find /config/token_anonymous.json')
        helper.Flag.AuthenState = 'failed'
        return redirect( url_for('login') )
    
    helper.Info.Profile = helper.Info.ServerProfile
    helper.Info.Creds = helper.Info.ServerCreds
    helper.Info.Service = helper.Info.ServerService
    helper.Info.GmailAddress = helper.Info.Profile.get('emailAddress')

    helper.Flag.LoggedIn = True
    helper.Info.HTMLFileName = helper.ANONYMOUS_HTML_FILENAME
    return redirect( url_for('control') )

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    helper.Flag.Anonymous = None
    helper.Flag.LoginAuthentication = None
    initAccount('token')
    msg_obj, err = gmail_api.sendMail(
        receiver=SERVER_GMAIL_ADDRESS, sender=SERVER_GMAIL_ADDRESS, subject='PCRC authentication',
        msg_content=helper.Info.GmailAddress, Creds=helper.Info.ServerCreds, Service=helper.Info.ServerService
    )
    print('control_with_gmail: sent')
    if err:
        print('control_with_gmail: cannot authenticate account.')
        return redirect( url_for('login') )
    auth = None
    while True:
        auth = gmail_api.readMail(
            Creds=helper.Info.ServerCreds, Service=helper.Info.ServerService, threadId=gmail_api.getThreadId(msg_obj=msg_obj),
            query="YES|NO",
        )
        if auth != None:
            break
        time.sleep(2)
    print('control_with_gmail: auth = ', auth)
    if not auth:
        helper.Flag.AuthenState = 'failed'
        helper.Flag.Anonymous = False
        return redirect( url_for('login') )
    elif auth == False:
        helper.Flag.AuthenState = None
        helper.Flag.LoginAuthentication = False
        return redirect( url_for('login') )
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
                isAuthor=True, isAnonymous=helper.Flag.Anonymous
            )
        else:
            return render_template(
                helper.Info.HTMLFileName, client_email=helper.Info.GmailAddress, send_error=None, isAuthor=True,
                isAnonymous=helper.Flag.Anonymous, successRequest=req_success
            )
    except Exception as e:
        print('def control(): ', e)
        return redirect( url_for('login') )

@app.route("/send_mail_handler/", methods=['GET', 'POST'])
def send_mail_handler():
    helper.Flag.SuccessRequest = False
    try:
        msg = request.form.get('msg-content')
        if len(msg) == 0:
            helper.Flag.SendMsgError = None
            return redirect( url_for('control') )
        msg = 'request\n' + msg

        chk_keylog = helper.checkKeylogger(msg)
        if chk_keylog == False:
            helper.Flag.SendMsgError = True
            return redirect( url_for('control') )
        helper.Info.SentMsgObject, helper.Flag.SendMsgError = gmail_api.sendMail(
            receiver=SERVER_GMAIL_ADDRESS, sender=helper.Info.GmailAddress, subject=SubjectMail.COMMAND,
            msg_content=msg, Creds=helper.Info.Creds, Service=helper.Info.Service
        )
        print('send_mail_handler: sent')
        if helper.Flag.SendMsgError:
            print('send_mail_handler | Msg Error: ', helper.Flag.SendMsgError)
            return redirect( url_for('control') )
        return redirect( url_for('get_response') )
    except Exception as e:
        print('send_mail_handler | exception: ', e)
        return redirect( url_for('login') )

@app.route("/get_response/", methods=['GET', 'POST'])
def get_response():
    try:
        resultPath = helper.createResultDir()
        while True:
            # flag, err = gmail_api.readMail_command(
            #     Creds=helper.Info.Creds, resultPath=resultPath,
            #     threadId=gmail_api.getThreadId(helper.Info.SentMsgObject),
            # )
            res = gmail_api.readMail(
                Creds=helper.Info.Creds, Service=helper.Info.Service, threadId=gmail_api.getThreadId(helper.Info.SentMsgObject),
                query='This is the result', work_w_plain_text_mail=False, resultPath=resultPath
            )
            # res == True | False | str(err)
            if res == True:
                break
            if res and res != False: # so that res == str(err)
                print('get_response | send mail err: ', res)
                helper.makeTextFile(dir_path=resultPath, content=res, filename = "error")
                break
            time.sleep(2)
        helper.Info.SentMsgObject = None
        helper.Flag.SuccessRequest = True
        if helper.isEmptyDir(resultPath):
            os.rmdir(resultPath)
        else:
            helper.openFolder(resultPath)
        return redirect( url_for('control') )
    except Exception as e:
        print('get_response | exception: ', e)
        return redirect( url_for('login') )