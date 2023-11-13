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
        testtt = service.listRunningApplication()
        for app in testtt:
            if app != "Description" and app != "-----------":
                print(app)
    elif int(choose) == 2:
        testtt = service.listRunningProcess()
        sorted_processes = sorted(testtt, key=lambda process: process["Name"])
        for process in sorted_processes:
            print(process)
    elif int(choose) == 4:
        service.screenshot()
    elif int(choose) == 3:
        service.keylogger(5)
    elif int(choose) == 5:
        service.shutdown()
    elif int(choose) == 6:
        appName = input()
        service.openApplication(appName)
