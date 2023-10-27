User begins at root page "/" (login.html)

If user chooses login without gmail:
    redirect to "/control_anonymous/" and use the prepared `token_anonymous.json` of chiemthoica@gmail.com to send mails
else:
    redirect to "/control_with_gmail/", then let user login and authenticate so that we have a token.json file used for sending mails

Both of these pages will be then redirected to "/control/" (control.html)

## Template + Static
`general.css`: style for ***common*** elements in both `login.html` and `control.html`

## How to run
activate venv: `.venv/scripts/activate`
go to dir gui `cd gui`
run file app.py `flask --app app run`