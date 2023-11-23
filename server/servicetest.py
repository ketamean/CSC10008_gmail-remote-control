import service

while True:
    print("1. List running application.")
    print("2. List running processes.")
    print("3. Keylogger")
    print("4. Screenshot")
    print("5. Shut down")
    print("6. Open App")
    choose = input()

    if int(choose) == 1:
        service.listRunningApplication()
    elif int(choose) == 2:
        service.listRunningProcess()
    elif int(choose) == 4:
        service.screenshot()
    elif int(choose) == 3:
        service.keylogger(5)
    elif int(choose) == 5:
        service.shutdown()
    elif int(choose) == 6:
        appName = input()
        service.openApplication(appName)
