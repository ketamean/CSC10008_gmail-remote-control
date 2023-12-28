import PySimpleGUI as sg
import imap_server

finalize = True
layout = [
    [sg.Text("Log: ")],
    [sg.Output(size=(90, 20), key="-OUTPUT-")],
    [sg.Button("Start"), sg.Button("Stop"), sg.Button("Exit")],
]

# create the window
window = sg.Window("Pc Remote Control Server", layout, margins=(10, 10), finalize=True)
my_mail_list = imap_server.mail_list_login()
started = False
timecount = 0
while True:
    if started == True:
        event, values = window.read(timeout=4000)
        imap = imap_server.imap_login()
        smtp = imap_server.smtp_login()
        imap_server.operate_server(imap, smtp, my_mail_list)
        timecount = timecount + 1
    else:
        event, values = window.read()
    if event == "Start":
        timecount = 0
        started = True
        window["-OUTPUT-"].update("")
        print("Starting Service")
    if event == "Stop":
        started = False
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    if timecount == 20:
        timecount = 0
        window["-OUTPUT-"].update("")
window.close()

imap_server.destructor(imap,smtp, my_mail_list)
