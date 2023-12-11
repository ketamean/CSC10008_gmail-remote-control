import wmi
import subprocess
import os
import logging
import keyboard
import cv2 as cv
import time
import AppOpener
import psutil
import pygetwindow
from AppOpener.features import AppNotFound
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

def getApplicationName(window_title):
    last_dash_index = window_title.rfind(" - ") 
    if last_dash_index != -1:
        app_name = window_title[last_dash_index + 3:] 
        return app_name.strip()
    return window_title 

def listRunningApplications():
    running_apps = set()
    windows = pygetwindow.getAllTitles()
    for window in windows:
        app_name = getApplicationName(window)
        running_apps.add(app_name)
        
    return sorted(list(running_apps))


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

def getLastWord(name):
    word = name.split()
    return word[-1]

def closeApplication(appName):
    app_name = getLastWord(appName)
    isKilled = False
    for proc in psutil.process_iter(['pid', 'name']):
        if app_name.lower() in proc.info['name'].lower():
            process = psutil.Process(proc.info['pid'])
            process.terminate()
            isKilled = True
    if isKilled == True:
        return f"{app_name} is closed."
    return (f"{app_name} is not running or not installed.")

                
                
def openApplication(appName):
    try:
        AppOpener.open(appName.lower(), throw_error=True)
    except AppNotFound:
        return f"{appName} is not installed or cannot be found"
    
