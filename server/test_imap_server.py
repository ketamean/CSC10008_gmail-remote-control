import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import mimetypes
import os

def send_mail(email, password, FROM, TO, msg):
    # initialize the SMTP server
    # in our case it's for Microsoft365, Outlook, Hotmail, and live.com
    server = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
    # connect to the SMTP server as TLS mode (secure) and send EHLO
    # login to the account using the credentials
    server.login(email, password)
    # send the email
    server.sendmail(FROM, TO, msg.as_string())
    # terminate the SMTP session
    server.quit()

# your credentials
email = "chiemthoica@gmail.com"
password = "gsno jiro wfgv esus"
# the sender's email
FROM = email
# the receiver's email
TO   = "chiemthoica@gmail.com"
# the subject of the email (subject)
subject = "PCRC working"

msgID = "<CANDETtmbVi7nYuw7mEKgcf-hWg_jmfMqZDDCBvuiq=y0zbfaUA@mail.gmail.com>"

message = MIMEMultipart()
message["From"] = FROM
message["To"] = TO
message["Subject"] = subject
message["In-Reply-To"] = msgID
message["References"] = msgID
content = "This is the result"
body = MIMEText(content, "plain")
message.attach(body)

directory = os.listdir("Screenshot")

for file in directory:
    attachment_filename = file
    if attachment_filename == "save_folder.txt":
        continue
    # guessing the MIME type
    type_subtype, _ = mimetypes.guess_type(attachment_filename)
    maintype, subtype = type_subtype.split("/")

    with open(os.path.join("Screenshot", attachment_filename), "rb") as fp:
        part = MIMEApplication(
            fp.read(),
            Name=os.path.basename(
                os.path.join("Screenshot", attachment_filename)
            ),
        )
        part["Content-Disposition"] = 'attachment; filename="{}"'.format(
            os.path.basename(os.path.join("Screenshot", attachment_filename))
        )
    message.attach(part)

send_mail(email, password, FROM, TO, message)