import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sargs = sys.argv

if len(sargs) < 2:
    print("usage: man <app_name>")
    sys.exit(1)

app_name = sargs[1]

try:
    with open(os.path.join(BASE_DIR, "..", app_name, "man.txt")) as MAN_PAGE:
        data = MAN_PAGE.read()
    print(f"Manual page for {app_name}")
    print(data)
except FileNotFoundError:
    with open(os.path.join(BASE_DIR, "..", "..", "bin", app_name, "man.txt")) as MAN_PAGE:
        data = MAN_PAGE.read()
    print(f"Manual page for {app_name}")
    print(data)  
else:
    print(f"man: no manual entry for {app_name}")
