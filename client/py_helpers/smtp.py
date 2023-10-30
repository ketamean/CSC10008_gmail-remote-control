# for sending gmail without authentication
import smtplib

session = smtplib.SMTP('smtp.gmail.com', 587)         # stmp session for sending mails anonymously
session.starttls()

def sendMailAnonymous(message):
    session.login('chiemthoica@gmail.com', 'nrwd imjb rnak kotl')    
    # sending the mail
    session.sendmail("chiemthoica@gmail.com", "truongthanhtoan2003@gmail.com", message)
    
    # remember to terminate the session when close the app
    session.quit()