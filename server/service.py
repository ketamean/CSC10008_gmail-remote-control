import wmi
import subprocess
import os
import time
import keyboard
from AppOpener import open, close
from pynput.keyboard import Listener
from PIL import ImageGrab
from PIL import Image


def listRunningProcess():
    runningProcess = []
    f = wmi.WMI()
    for process in f.Win32_Process():
        processInfo = {"PID": process.ProcessId, "Name": process.Name}
        runningProcess.append(processInfo)
    outputDir = os.path.join("ServiceOutput", "list_processes.txt")
    sortedProcess = sorted(runningProcess, key=lambda process: process["Name"])
    with open(outputDir, "w") as file:
        for process in sortedProcess:
            file.write(process + "\n")
    return 1


def listRunningApplication():
    runningApp = []
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout = proc.communicate()

    for line in stdout[0].decode().split("\n"):
        line = line.strip()
        if line:
            runningApp.append(line)

    outputDir = os.path.join("ServiceOutput", "list_app.txt")
    with open(outputDir, "w") as file:
        for app in runningApp:
            if app != "Description" and app != "-----------":
                file.write(app + "\n")
    return 1


def screenshot():
    screenshotImage = ImageGrab.grab()
    curDir = os.getcwd()
    screenshotDir = os.path.join(curDir, "Screenshot")
    id = len(os.listdir(screenshotDir))
    name = "screenshot" + str(id) + ".png"
    screenshotImage.save(os.path.join(screenshotDir, name))
    return 1


def keylogger(duration):
    recorded_keys = []
    escape = False

    def on_key_event(e):
        nonlocal escape
        if e.event_type == keyboard.KEY_UP:
            key = e.name
            if key == "esc":
                escape = True
            else:
                recorded_keys.append(key)

    keyboard.hook(on_key_event)
    start = time.time()
    while (time.time() - start) < duration and not escape:
        pass

    keyboard.unhook_all()
    outputDir = os.path.join("ServiceOutput", "key_logger.txt")
    with open(outputDir, "w") as file:
        for kl in recorded_keys:
            file.write(kl + " ")
    return 1


def shutdown():
    outputDir = os.path.join("ServiceOutput", "shut_down.txt")
    with open(outputDir, "w") as file:
        file.write("The computer is shutting down")
    os.system("shutdown /s /t 1")


def logout():
    outputDir = os.path.join("ServiceOutput", "log_out.txt")
    with open(outputDir, "w") as file:
        file.write("The computer is logging out")
    os.system("shutdown -l")


def removeSpace(string):
    return string.replace(" ", "")


def closeApplication(process_name):
    process_name = removeSpace(process_name)
    close(process_name.lower())


def openApplication(appName):
    open(appName.lower())
