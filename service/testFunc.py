import func
import os

while True:
    os.system('cls')
    print("1. List running application.")
    print("2. List running processes.")
    print("3. Keylogger")
    print("4. Screenshot")
    print("5. Shut down")
    choose = input()
    
    if int(choose) == 1:
        testtt = func.listRunningApplication()
        for app in testtt:
            if app != "Description" and app != "-----------":
                print(app)
    elif int(choose) == 2:
        testtt = func.listRunningProcess()
        sorted_processes = sorted(testtt, key=lambda process: process["Name"])
        for process in sorted_processes:
            print(process)
    elif int(choose) == 4:
        func.screenshot()
    elif int(choose) == 3:
        testtt = func.keylogger()
        for kl in testtt:
            print(kl)
    elif int(choose) == 5:
        func.shutdown()
    
    input()