from flask import Flask, render_template, url_for, request, redirect
from gmail_api import *
import os

app = Flask(__name__)

user_info = {
    'emailAddress': '',
    'profile': None
}

AuthenState = 'failed'    # keep the state of authentication

@app.route("/control_anonymous/", methods=['GET', 'POST'])
def control_anonymous():
    if os.path.exists('token_anonymous.json'):
        creds = Credentials.from_authorized_user_file('token_anonymous.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token_anonymous.json', 'w') as token:
            token.write(creds.to_json())

    global service
    service = build('gmail', 'v1', credentials=creds)

    # user_info['profile'], _ = checkAuthenticated()
    # user_info['emailAddress'] = user_info['profile']['emailAddress']

    user_info['emailAddress'] = 'chiemthoica@gmail.com'
    return redirect(url_for('control'))

@app.route("/control_with_gmail/", methods=['GET', 'POST'])
def control_with_gmail():
    buildService()
    user_info['profile'], auth = checkAuthenticated()
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
    if AuthenState == 'failed':
        AuthenState = None
        return render_template("login.html", successAuthen=False)
    else:
        return render_template("login.html")

# with app.test_request_context():