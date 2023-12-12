import os
import re
import winreg

ANONYMOUS_HTML_FILENAME = 'control_anonymous.html'
FULL_HTML_FILENAME = 'control_full.html'

class Info:
    GmailAddress = None             # client's Gmail address
    Profile =  None                 # is reserved for future use
    Creds = None
    Service = None                  # mail service
    SentMsgObject = None            # Message object, including: 'id', 'threadId' and 'labelIds'
    HTMLFileName = None             # [str] name of the html file to be rendered
    ServerCreds = None              # creds of server gmail account
    ServerProfile = None            # profile object of server gmail account
    ServerService = None            # mail service of server's gmail account

class Flag:
    # process flag
    SendMsgError = None             # error caused by sending messages; is None if there is no error
    SuccessRequest = False          # mark whether the process of receiving response after sending request is done (all the files are downloaded)

    # login flag
    AuthenState = None              # keep the state of authentication
    Anonymous = None                # mark if user is using app anonymously, True | None
    LoggedIn = None
    Register = False                # register result: True if success; otherwise, False
    RememberAccount = False         # mark if remember user account (do not delete token.json file)
    LoginAuthentication = None      # True if the account has been registered and allowed to log in; if not, False

def extractTimeKeylogger(msg: str):
    return re.findall(r'\n*\s*\[key_logger\]\s+(\d|\d\d)\s*\n+', msg)

def checkKeylogger(msg: str):
    """
        check whether there is a singular valid key-logger command

        [`Bool`]    returns `True` if there is;

                    returns `False` if there are more than one

        [`None`]    returns `None` if there is no key-logger command
    """
    match = extractTimeKeylogger(msg)
    # valid = re.findall('[0-9]', msg)
    if len(match) == 0:
        return None
    if len(match) > 1: # or (len(match) == 1 and len(valid) > 2)
        return False
    return True

def resetUserInfo(del_token):
    """
        reset user info after re-login
        [None]
    """
    Info.GmailAddress = None
    Info.Profile = None
    if del_token and os.path.exists('config/token.json'):
        os.remove('config/token.json')
    Info.Creds = None
    Info.Service = None
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

def makeDir(path: str):
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

def resolveDupName(name: str):
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
    os.startfile(filepath=abs_path, operation="open")

def makeTextFile(dir_path: str, content: str, filename: str):
    with open(os.path.join(dir_path, filename + '.txt'), 'w') as f:
        f.write(content)

def duration(start_time, end_time):
    return end_time - start_time

def isEmptyDir(dir_path):
    """
        dir_path: abs path to the directory

        returns True: is an empty dir | False: is not empty
    """
    if len(os.listdir(dir_path)) == 0:
        return True
    return False