import wmi
import subprocess
import os
import logging
import keyboard
import cv2 as cv
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
    
    
def keylogger():
    recorded_keys = []
    def on_key_event(e):
        if e.event_type == keyboard.KEY_UP:
            key = e.name
            recorded_keys.append(key)

    keyboard.hook(on_key_event)
    keyboard.wait("esc")

    return recorded_keys


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
