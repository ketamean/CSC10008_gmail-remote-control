import PySimpleGUI as sg
import server

layout = [
    [sg.Text("Log: ")],
    [sg.Output(size=(90, 20), key="-OUTPUT-")],
    [sg.Button("Start"), sg.Button("Stop"), sg.Button("Exit")],
]

# create the window
window = sg.Window("Pc Remote Control Server", layout, margins=(10, 10))
creds = server.main()
started = False
timecount = 0
while True:
    if started == True:
        event, values = window.read(timeout=3000)
        server.CheckMail(creds)
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
    if timecount == 10:
        timecount = 0
        window["-OUTPUT-"].update("")
window.close()