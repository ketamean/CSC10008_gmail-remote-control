import wmi
import subprocess
import os
import time
import keyboard
import AppOpener
from PIL import ImageGrab


def listRunningProcess():
    runningProcess = []
    f = wmi.WMI()
    for process in f.Win32_Process():
        processInfo = {"PID": process.ProcessId, "Name": process.Name}
        runningProcess.append(processInfo)
    sortedProcess = sorted(runningProcess, key=lambda process: process["Name"])

    curDir = os.getcwd()
    saveDir = os.path.join(curDir, "ServiceOutput")
    id = len(os.listdir(saveDir))
    name = "list_proceses" + str(id) + ".txt"
    outputDir = os.path.join(saveDir, name)

    with open(outputDir, "w") as file:
        for process in sortedProcess:
            file.write(str(process) + "\n")


def listRunningApplication():
    runningApp = []
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout = proc.communicate()

    for line in stdout[0].decode().split("\n"):
        line = line.strip()
        if line:
            runningApp.append(line)

    curDir = os.getcwd()
    saveDir = os.path.join(curDir, "ServiceOutput")
    id = len(os.listdir(saveDir))
    name = "list_app" + str(id) + ".txt"
    outputDir = os.path.join(saveDir, name)

    with open(outputDir, "w") as file:
        for app in runningApp:
            if app != "Description" and app != "-----------":
                file.write(app + "\n")


def screenshot():
    screenshotImage = ImageGrab.grab()
    curDir = os.getcwd()
    screenshotDir = os.path.join(curDir, "Screenshot")
    id = len(os.listdir(screenshotDir))
    name = "screenshot" + str(id) + ".png"
    screenshotImage.save(os.path.join(screenshotDir, name))


def keylogger(duration):
    curDir = os.getcwd()
    saveDir = os.path.join(curDir, "ServiceOutput")
    id = len(os.listdir(saveDir))
    name = "key_logger" + str(id) + ".txt"
    outputDir = os.path.join(saveDir, name)
    if duration < 0 or duration > 99:
        with open(outputDir, "w") as file:
            for kl in recorded_keys:
                file.write(
                    "Invalid time duration. Please input time duration greater than 0 and lower than 99."
                )
        pass
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

    with open(outputDir, "w") as file:
        for kl in recorded_keys:
            file.write(kl + " ")


def shutdown():
    os.system("shutdown /s /t 1")


def logout():
    os.system("shutdown -l")


def removeSpace(string):
    return string.replace(" ", "")


def closeApplication(process_name):
    process_name = removeSpace(process_name)

    curDir = os.getcwd()
    saveDir = os.path.join(curDir, "ServiceOutput")
    id = len(os.listdir(saveDir))
    name = "closed" + str(id) + ".txt"
    outputDir = os.path.join(saveDir, name)

    try:
        AppOpener.close(process_name.lower(), match_closest=True, throw_error=True)
        with open(outputDir, "w") as file:
            file.write(process_name + " is closed" + "\n")
    except Exception as er:
        with open(outputDir, "w") as file:
            file.write(process_name + " is not running or not opened" + "\n")


def openApplication(appName):
    curDir = os.getcwd()
    saveDir = os.path.join(curDir, "ServiceOutput")
    id = len(os.listdir(saveDir))
    name = "start_app" + str(id) + ".txt"
    outputDir = os.path.join(saveDir, name)

    try:
        AppOpener.open(appName.lower(), throw_error=True, match_closest=True)
        with open(outputDir, "w") as file:
            file.write(appName + " opened" + "\n")
    except Exception as er:
        with open(outputDir, "w") as file:
            file.write(appName + "is not installed or cannot be found" + "\n")
