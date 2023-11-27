# test header
import gmail_api

Creads = gmail_api.authenticate('')
Service = gmail_api.buildService(Creads)

gmail_api.readMails(Creds=Creads, Service=Service, sbj_mail='')