"""
PyOS Shell: Main Interactive Command Dispatcher
================================================
shell.py is the entry point of PyOS. It implements a command-line shell that:
1. Loads system configuration (hostname, env state) from JSON files
2. Maintains two app registries: sbin/ (system commands) and bin/ (user apps)
3. Dispatches user input to registered apps or built-in commands
4. Manages system state (startup, shutdown)

Command Categories:
- Built-in: killself, shutdown, clear, rebase, help, status, version
- System Apps: Commands registered in sbin/register.json
- User Apps: Commands registered in bin/register.json

Architecture:
- Registry-based dispatch: SYSTEM_APP_REGISTER_LIST and APP_REGISTER_LIST control available commands
- Dynamic loading: Apps loaded from sbin/<name>/<name>.py or bin/<name>/<name>.py
- State management: Tracks system status via ENV/.system.json
"""

import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# System metadata and configuration
SYSTEM_INFO = None
HOSTNAME = "PyOS"
SYSTEM_APP_REGISTER = {}
SYSTEM_APP_REGISTER_LIST = []
APP_REGISTER = {}
APP_REGISTER_LIST = []


def load_system_info():
    """
    Load system configuration from imp/system.json.
    Sets HOSTNAME and other system metadata.
    
    Errors handled gracefully:
    - Missing file: use default hostname "PyOS"
    - Corrupt JSON: use defaults
    """
    global SYSTEM_INFO, HOSTNAME
    system_json_path = os.path.join(BASE_DIR, "imp", "system.json")
    
    try:
        with open(system_json_path) as f:
            SYSTEM_INFO = json.load(f)
            HOSTNAME = SYSTEM_INFO.get("HOSTNAME", "PyOS")
    except FileNotFoundError:
        print(f"WARNING: {system_json_path} not found, using defaults")
        SYSTEM_INFO = {"HOSTNAME": "PyOS"}
        HOSTNAME = "PyOS"
    except json.JSONDecodeError as e:
        print(f"WARNING: {system_json_path} corrupted ({e}), using defaults")
        SYSTEM_INFO = {"HOSTNAME": "PyOS"}
        HOSTNAME = "PyOS"
    except Exception as e:
        print(f"WARNING: Failed to load system info ({e}), using defaults")
        SYSTEM_INFO = {"HOSTNAME": "PyOS"}
        HOSTNAME = "PyOS"


def REBASE_SYSTEM_BIN():
    """
    Reload app registries from sbin/register.json and bin/register.json.
    
    Called at startup and when 'rebase' command is issued.
    Allows hot-reloading of installed apps without shell restart.
    
    Errors handled:
    - Missing register files: init to empty registries
    - Corrupt JSON: warn and init to empty
    """
    global SYSTEM_APP_REGISTER, SYSTEM_APP_REGISTER_LIST
    global APP_REGISTER, APP_REGISTER_LIST
    
    sbin_register_path = os.path.join(BASE_DIR, "sbin", "register.json")
    bin_register_path = os.path.join(BASE_DIR, "bin", "register.json")
    
    # Load system apps registry
    try:
        with open(sbin_register_path) as f:
            SYSTEM_APP_REGISTER = json.load(f)
    except FileNotFoundError:
        print(f"WARNING: {sbin_register_path} not found")
        SYSTEM_APP_REGISTER = {}
    except json.JSONDecodeError as e:
        print(f"WARNING: {sbin_register_path} corrupted ({e})")
        SYSTEM_APP_REGISTER = {}
    except Exception as e:
        print(f"WARNING: Cannot load system registry ({e})")
        SYSTEM_APP_REGISTER = {}
    
    # Load user apps registry
    try:
        with open(bin_register_path) as f:
            APP_REGISTER = json.load(f)
    except FileNotFoundError:
        print(f"WARNING: {bin_register_path} not found")
        APP_REGISTER = {}
    except json.JSONDecodeError as e:
        print(f"WARNING: {bin_register_path} corrupted ({e})")
        APP_REGISTER = {}
    except Exception as e:
        print(f"WARNING: Cannot load app registry ({e})")
        APP_REGISTER = {}
    
    SYSTEM_APP_REGISTER_LIST = list(SYSTEM_APP_REGISTER.keys())
    APP_REGISTER_LIST = list(APP_REGISTER.keys())


def start_system():
    """
    Initialize system startup state. Sets turned_on flag to True in ENV/.system.json.
    Called once when shell starts.
    """
    env_path = os.path.join(BASE_DIR, "ENV", ".system.json")
    try:
        with open(env_path, "r") as f:
            shell = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        shell = {}
    
    shell["turned_on"] = True
    try:
        with open(env_path, "w") as f:
            json.dump(shell, f, indent=4)
    except Exception as e:
        print(f"WARNING: Cannot write system state ({e})")


def stop_system():
    """
    Shutdown system: set turned_on flag to False and exit shell.
    Called by 'shutdown' command.
    """
    env_path = os.path.join(BASE_DIR, "ENV", ".system.json")
    try:
        with open(env_path, "r") as f:
            shell = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        shell = {}
    
    shell["turned_on"] = False
    try:
        with open(env_path, "w") as f:
            json.dump(shell, f, indent=4)
    except Exception as e:
        print(f"WARNING: Cannot write system state ({e})")
    
    print("System shutting down...")
    exit(0)


def print_status():
    """Display system status: hostname and registered apps."""
    print(f"Hostname: {HOSTNAME}")
    print(f"System Apps: {', '.join(sorted(SYSTEM_APP_REGISTER_LIST)) if SYSTEM_APP_REGISTER_LIST else 'none'}")
    print(f"User Apps: {', '.join(sorted(APP_REGISTER_LIST)) if APP_REGISTER_LIST else 'none'}")



def print_version():
    """Display PyOS version info."""
    print("PyOS v1.0 - Python-based Operating System")
    print("A fantasy computer with app registry and shell interface")


def print_help():
    """Display built-in command help."""
    print("PyOS Shell - Built-in Commands:")
    print("  status                 Show system status")
    print("  version                Show PyOS version")
    print("  rebase [system/bin]    Reload app registries")
    print("  clear                  Clear screen")
    print("  help                   Show this help")
    print("  killself               Exit shell")
    print("  shutdown               Shutdown system")
    print()
    print(f"System Apps: {', '.join(sorted(SYSTEM_APP_REGISTER_LIST)) if SYSTEM_APP_REGISTER_LIST else 'none'}")
    print(f"User Apps: {', '.join(sorted(APP_REGISTER_LIST)) if APP_REGISTER_LIST else 'none'}")



# Initialize system
load_system_info()
REBASE_SYSTEM_BIN()

# Ensure ENV directory and .system.json exist
env_dir = os.path.join(BASE_DIR, "ENV")
env_file = os.path.join(env_dir, ".system.json")
if not os.path.exists(env_dir):
    try:
        os.makedirs(env_dir, exist_ok=True)
    except OSError as e:
        print(f"WARNING: Cannot create ENV directory ({e})")

if not os.path.exists(env_file):
    try:
        with open(env_file, "w") as f:
            json.dump({"turned_on": False}, f, indent=4)
    except OSError as e:
        print(f"WARNING: Cannot create .system.json ({e})")

PROMPT = f"system@{HOSTNAME}$ "

# Start system and enter main loop
start_system()

while True:
    try:
        cmd = input(PROMPT)
    except EOFError:
        # Ctrl+D pressed
        print()
        stop_system()
    except KeyboardInterrupt:
        # Ctrl+C pressed
        print()
        continue
    except Exception as e:
        print(f"ERROR: Failed to read input ({e})")
        continue
    
    # Parse command and arguments
    cmd_parts = cmd.strip().split()
    if not cmd_parts or not cmd_parts[0]:
        continue
    
    cmd_name = cmd_parts[0]
    
    # BUILT-IN COMMANDS
    if cmd_name == "killself":
        exit(0)
    elif cmd_name == "shutdown":
        stop_system()
    elif cmd_name == "clear":
        try:
            subprocess.run("clear", shell=True)
        except Exception as e:
            print(f"ERROR: Cannot clear screen ({e})")
    
    # SYSTEM COMMANDS
    elif cmd_name == "status":
        print_status()
    elif cmd_name == "version":
        print_version()
    elif cmd_name == "help":
        print_help()
    
    # REGISTRY MANAGEMENT
    elif cmd_name == "rebase":
        target = cmd_parts[1] if len(cmd_parts) > 1 else "all"
        if target in ("system/bin", "all"):
            REBASE_SYSTEM_BIN()
            print("Registries reloaded.")
        else:
            print("ERROR: rebase [system/bin|all]")
    
    # REGISTERED APP EXECUTION (SYSTEM)
    elif cmd_name in SYSTEM_APP_REGISTER_LIST:
        app_path = os.path.join(BASE_DIR, "sbin", cmd_name, cmd_name + ".py")
        if not os.path.isfile(app_path):
            print(f"ERROR: System app '{cmd_name}' not found at {app_path}")
        else:
            # Pass remaining arguments to app
            full_cmd = ["python3", app_path] + cmd_parts[1:]
            try:
                subprocess.run(full_cmd, cwd=BASE_DIR)
            except Exception as e:
                print(f"ERROR: Failed to execute '{cmd_name}' ({e})")
    
    # REGISTERED APP EXECUTION (USER)
    elif cmd_name in APP_REGISTER_LIST:
        app_path = os.path.join(BASE_DIR, "bin", cmd_name, cmd_name + ".py")
        if not os.path.isfile(app_path):
            print(f"ERROR: User app '{cmd_name}' not found at {app_path}")
        else:
            # Pass remaining arguments to app
            full_cmd = ["python3", app_path] + cmd_parts[1:]
            try:
                subprocess.run(full_cmd, cwd=BASE_DIR)
            except Exception as e:
                print(f"ERROR: Failed to execute '{cmd_name}' ({e})")
    
    # UNKNOWN COMMAND
    else:
        print(f"shell: command not found: {cmd_name}")


