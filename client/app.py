from flask import Flask, render_template, url_for, request, redirect
from py_helpers import gmail_api
# from smtp import *
import os

app = Flask(__name__)

user_info = {
    'emailAddress': '',
    'profile': None
}

AuthenState = 'failed'    # keep the state of authentication

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    gmail_api.buildService('token_anonymous')

    # user_info['profile'], _ = checkAuthenticated()
    # user_info['emailAddress'] = user_info['profile']['emailAddress']

    user_info['emailAddress'] = 'chiemthoica@gmail.com'
    return redirect(url_for('control'))

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    gmail_api.buildService('token')
    user_info['profile'], auth = gmail_api.checkAuthenticated()
    if auth == False:
        global AuthenState
        AuthenState = 'failed'
        return redirect(url_for('login'))
    user_info['emailAddress'] = user_info['profile']['emailAddress']
    return redirect(url_for('control'))

@app.route("/control/", methods=['GET', 'POST'])
def control():
    return render_template("control.html", client_email=user_info['emailAddress'])

@app.route("/", methods=['GET', 'POST'])
def login():
    global AuthenState
    user_info['emailAddress'] = None
    user_info['profile'] = None
    if os.path.exists('config/token.json'):
        os.remove('config/token.json')
    if AuthenState == 'failed':
        AuthenState = None
        return render_template("login.html", successAuthen=False)
    else:
        return render_template("login.html")

# with app.test_request_context():