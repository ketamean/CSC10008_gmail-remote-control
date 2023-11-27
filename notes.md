User begins at root page "/" (login.html)

If user chooses login without gmail:
    redirect to "/control_anonymous/" and use the prepared `token_anonymous.json` of chiemthoica@gmail.com to send mails
else:
    redirect to "/control_with_gmail/", then let user login and authenticate so that we have a token.json file used for sending mails

Both of these pages will be then redirected to "/control/" (control.html)

## Template + Static
`general.css`: style for ***common*** elements in both `login.html` and `control.html`

## How to run
- activate venv: `.venv/scripts/activate`
- go to dir client `cd client`
- run file app.py `flask --app app run`

## Notes read and send mails
- At the beginning, user sends an email to create a thread
- Then server gets the mail and **reply** to that mail (such that all the mails are in the same thread)
- Concurrently, client constantly checks mail until get the result FROM THE INITIAL THREAD (but maximum *xx* seconds)

root
|-- __init__.py
|-- service.py
|-- folderA
|   |-- __init__.py
|   |-- functionA.py
|   |-- ui.py
|-- folderB
|   |-- __init__.py
|   |-- functionB.py