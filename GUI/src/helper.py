import os
import re
import winreg

class Info:
    GmailAddress = None     # client's Gmail address
    Profile =  None         # is reserved for future use
    Creds = None
    SendMsgObject = None    # Message object, including: 'id', 'threadId' and 'labelIds'
    def __init__(self) -> None:
        pass

class Flag:
    AuthenState = None  # keep the state of authentication
    SendMsgError = None # error caused by sending messages; is None if there is no error
    Anonymous = None    # mark if user is using app anonymously, True | None
    LoggedIn = None
    def __init__(self) -> None:
        pass

def checkKeylogger(msg):
    """
        check whether there is a singular valid key-logger command

        [`Bool`]    returns `True` if there is;

                    returns `False` if there are more than one

        [`None`]    returns `None` if there is no key-logger command
    """
    print(msg)
    match = re.findall('\[key_logger\] [0-9][0-9]', msg)
    valid = re.findall('[0-9]', msg)
    print('match: ', match)
    if len(match) == 0:
        return None
    if len(match) > 1 or (len(match) == 1 and len(valid) > 2):
        return False
    return True

def resetUserInfo():
    """
        reset user info after re-login
        [None]
    """
    Info.GmailAddress = None
    Info.Profile = None
    if os.path.exists('config/token.json'):
        os.remove('config/token.json')
    Info.Creds = None
    Info.SendMsgObject = None
    Flag.LoggedIn = None
    Flag.SendMsgError = None

def getDownloadDir():
    """
        [str] the absolute path to the downloads directory in the client's device
    """
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    downloads_path = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
    winreg.CloseKey(reg_key)
    return downloads_path

def makeDir(path):
    """
        making a dir with the given path
        [bool] True if successfully created; otherwise, False
    """
    try:
        os.mkdir(path, 0o666)
    except:
        return False
    return True

class StaticVar:
    val = None

def resolveDupName(name):
    """
        resolve duplicated name when making dir
    """
    if StaticVar.val == None:
        StaticVar.val = 1
    else:
        StaticVar.val += 1
    return str(name) + "(" + str(StaticVar.val) + ")"

def createResultDir():
    """
        return (str) path to the directory that contains all result attachments
    """
    downloads_path = getDownloadDir()
    newDirName = 'Result'
    path = os.path.join(downloads_path, newDirName)
    while makeDir(path) == False:
        name = resolveDupName(newDirName)
        path = os.path.join(downloads_path, name)
    StaticVar.val = None
    return path

def openFolder(abs_path):
    os.startfile(abs_path)