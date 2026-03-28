import json
import os
import subprocess

SYSTEM_INFO = json.load(open("imp/system.json"))
HOSTNAME = SYSTEM_INFO["HOSTNAME"]


APP_REGISTER = json.load(open("sbin/register.json"))
APP_REGISTER_LIST = list(APP_REGISTER.keys())

PROMPT = f"system@{HOSTNAME}$ "
PWD = "home/"
# DEBUG
# print(PWD)
# print(PROMPT)
print(APP_REGISTER_LIST)

open("ENV/.system.json", "a")


# SYSTEM STARTUP
def start_system():
    with open("ENV/.system.json", "r") as f:
        shell = json.load(f)
    shell["turned_on"] = True
    with open("ENV/.system.json", "w") as f:
        json.dump(shell, f, indent=4)


def stop_system():
    with open("ENV/.system.json", "r") as f:
        shell = json.load(f)
    shell["turned_on"] = False
    with open("ENV/.system.json", "w") as f:
        json.dump(shell, f, indent=4)
    exit(0)


# FILE MANAGEMENT
def make_dir(name):
    os.mkdir(f"{PWD}{name}")


start_system()

while True:
    cmd = input(f"[{PWD}] " + PROMPT)
    cmd = cmd.split(" ")
    if cmd[0] == "exit":
        break
    elif cmd[0] == "shutdown":
        stop_system()
    elif cmd[0] in APP_REGISTER_LIST:
        cmd[0] = f"sbin/{cmd[0]}/" + cmd[0] + ".py"
        cmd = " ".join(["python3", *cmd])
        result = subprocess.run(cmd, shell=True)
    elif cmd[0] == "mkdir":
        make_dir(cmd[1])
    else:
        cmd = " ".join(cmd)
        print(f"shell: command not found: {cmd}")
