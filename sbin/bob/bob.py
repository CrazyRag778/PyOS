import json
import os
import tarfile
import sys
s_args = sys.argv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(BASE_DIR, "bin", "register.json")) as f:
    USER_APP_REGISTER = json.load(f) 

USER_APP_REGISTER_LIST = list(USER_APP_REGISTER.keys())

# UNPACK - LOAD TO BIN - REGISTER

BIN_TAR = sys.argv[1]

def get_name(tarball):
    tarball = tarball.split(".")
    return tarball[0]
def SETUP_BIN():
    # UNPACK
    os.mkdir(os.path.join(BASE_DIR, "bin", get_name(BIN_TAR)))
    with tarfile.open(os.path.join(BASE_DIR, "packs", BIN_TAR), "r:*") as tar:
        tar.extractall(path=os.path.join(BASE_DIR, "bin/"))
    # REGISTER
    with open(os.path.join(BASE_DIR, "bin", get_name(BIN_TAR), "manifest.json")) as f:
        MANIFEST = json.loads(f.read())
        BIN_TYPE = MANIFEST['type']
        BIN_NAME = MANIFEST['NAME']
        USER_APP_REGISTER[BIN_NAME] = {
            "NAME": BIN_NAME,
            "type": BIN_TYPE
        }
        with open(os.path.join(BASE_DIR, 'bin', 'register.json'), 'w') as REGISTER:
            json.dump(USER_APP_REGISTER, REGISTER, indent=4) 

SETUP_BIN()