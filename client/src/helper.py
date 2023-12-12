import os
import re
import winreg
import gmail_api

ANONYMOUS_HTML_FILENAME = 'control_anonymous.html'
FULL_HTML_FILENAME = 'control_full.html'

class Info:
    GmailAddress = None             # client's Gmail address
    Profile =  None                 # is reserved for future use
    Creds = None
    SentMsgObject = None            # Message object, including: 'id', 'threadId' and 'labelIds'
    Timer = 0                       # [int] maximum ammount of time to wait the replied mail after sending request
    HTMLFileName = None             # [str] name of the html file to be rendered
    ServerCreds = None              # creds of server gmail account
    ServerProfile = None            # profile object of server gmail account

class Flag:
    # process flag
    SendMsgError = None             # error caused by sending messages; is None if there is no error
    TimeOutRespond = False          # mark whether the process of getting respond after sending request is time-out
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
    Info.Timer = 0
    Info.GmailAddress = None
    Info.Profile = None
    if del_token and os.path.exists('config/token.json'):
        os.remove('config/token.json')
    Info.Creds = None
    Info.SendMsgObject = None
    Flag.LoggedIn = None
    Flag.SendMsgError = None
    Flag.TimeOutRespond = False

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

# def calcMaxWaitTime(msg_content: str):
#     """
#         [int] seconds

#         we cannot permanently wait for the response after sending request

#         this function helps us to calc the maximum time to wait

#         suppose that:
            
#             - it takes 15s to get the mail from mail server
#             - it takes 1.5s each command, excluding keylogger (relatively)
#             - it takes 0.8s to download result for each command

#         prerequiste: this function is called if and only if there is a singular valid key-logger command in the msg content
#     """
#     # extract the number in key-logger command
#     time_keylog = extractTimeKeylogger(msg=msg_content)
#     msgs = [el for el in msg_content.splitlines() if el != '']
    
#     if len(time_keylog) == 1:
#         return 20 + 1.5 * (len(msgs) - 1) + 0.8 * len(msgs) + int(time_keylog[0])
#     return 20 + 1.5 * (len(msgs) - 1) + 0.8 * len(msgs)