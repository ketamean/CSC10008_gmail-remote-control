listdemo = []
# with open("usermail.txt", "r") as f:
#     for x in f:
#         listdemo.append(x.rstrip())
with open("usermail.txt", "w") as f:
    for mail in ["asdf", "asdf"]:
        f.write(mail + "\n")
print(listdemo)
