"""
BOB: Package Installer Utility for PyOS
========================================
bob.py handles installation and removal of application packages in PyOS.
Packages are stored as tarballs in `packs/` and extracted to `bin/`.
Each installed package is registered in `bin/register.json` for shell dispatch.

Mechanism:
----------
1. INSTALL: Extracts tarball → reads manifest.json → registers in bin/register.json
2. REMOVE: Looks up package in register.json → deletes directory → updates register
3. LIST: Displays all registered packages from register.json
4. LEGACY: Single tarball argument triggers install (backward compatible)

Dependencies: shell.py uses bob to manage installed applications and maintains
the registry that controls which commands are available at shell prompt.
"""

import json
import os
import tarfile
import sys
import shutil

# Command-line arguments passed to this script
s_args = sys.argv

# BASE_DIR points to PyOS root: sbin/bob/bob.py → go up 3 levels
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# USER_APP_REGISTER holds all registered apps from bin/register.json
# Populated at startup via safe_load_register()
USER_APP_REGISTER = {}


def safe_load_register():
    """
    Load package registry from bin/register.json.
    
    Handles gracefully:
    - Missing file (init to empty {})
    - JSON corruption (warn and init to empty {})
    - Permission errors (warn and init to empty {})
    
    This ensures bob can always operate even if registry is corrupt.
    """
    global USER_APP_REGISTER
    register_path = os.path.join(BASE_DIR, "bin", "register.json")

    if not os.path.isfile(register_path):
        USER_APP_REGISTER = {}
        return

    try:
        with open(register_path) as f:
            USER_APP_REGISTER = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: register.json is corrupted ({e}).")
        USER_APP_REGISTER = {}
    except Exception as e:
        print(f"ERROR: cannot read register.json ({e}).")
        USER_APP_REGISTER = {}


def safe_save_register():
    """
    Persist updated USER_APP_REGISTER back to bin/register.json.
    
    Called after install/remove operations to ensure registry stays in sync.
    Raises exception if write fails (caller handles retry/cleanup).
    """
    register_path = os.path.join(BASE_DIR, "bin", "register.json")
    try:
        with open(register_path, 'w') as REGISTER:
            json.dump(USER_APP_REGISTER, REGISTER, indent=4)
    except Exception as e:
        raise RuntimeError(f"Failed to write register.json: {e}")


def get_name(tarball):
    """
    Extract package name from tarball filename.
    Example: "myapp.tar.gz" → "myapp"
    
    Validates format: filename must contain a dot.
    Raises ValueError if invalid.
    """
    if not tarball or '.' not in tarball:
        raise ValueError(f"Invalid tarball name '{tarball}'")
    return tarball.split('.')[0]


def install_package(tarball):
    """
    Install a package from packs/<tarball> into bin/<package_name>.
    
    Process:
    1. Extract tarball from packs/ to bin/
    2. Read manifest.json from extracted package
    3. Register package by manifest NAME and type in register.json
    
    Errors raised if:
    - Archive doesn't exist
    - Package dir already exists (prevent overwrites)
    - manifest.json missing or invalid
    - Required fields (type, NAME) missing from manifest
    """
    package_dir = os.path.join(BASE_DIR, "bin", get_name(tarball))
    archive_path = os.path.join(BASE_DIR, "packs", tarball)

    if not os.path.isfile(archive_path):
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    if os.path.exists(package_dir):
        raise FileExistsError(f"Package directory already exists: {package_dir}")

    os.makedirs(package_dir, exist_ok=False)

    try:
        with tarfile.open(archive_path, "r:*") as tar:
            tar.extractall(path=os.path.join(BASE_DIR, "bin"))
    except (tarfile.TarError, OSError) as e:
        raise RuntimeError(f"Failed to extract tarball '{tarball}': {e}")

    manifest_path = os.path.join(package_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(f"manifest.json not found in package '{package_dir}'")

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to read manifest: {e}")

    bin_type = manifest.get('type')
    bin_name = manifest.get('NAME')
    if not bin_type or not bin_name:
        raise ValueError("manifest.json must include 'type' and 'NAME'")

    USER_APP_REGISTER[bin_name] = {
        "NAME": bin_name,
        "type": bin_type
    }

    safe_save_register()
    print(f"Package '{bin_name}' installed successfully.")



def remove_package(package_name):
    """
    Remove a package by name from register.json.
    
    Process:
    1. Verify package_name exists in register.json
    2. Delete bin/<package_name> directory tree
    3. Remove entry from register.json
    
    Errors raised if:
    - Package not in registry
    - Directory doesn't exist
    - Directory deletion fails
    """
    if package_name not in USER_APP_REGISTER:
        raise ValueError(f"Package '{package_name}' not found in registry")

    package_info = USER_APP_REGISTER[package_name]
    package_dir = os.path.join(BASE_DIR, "bin", package_name)

    if not os.path.isdir(package_dir):
        raise FileNotFoundError(f"Package directory '{package_dir}' not found")

    try:
        shutil.rmtree(package_dir)
    except Exception as e:
        raise RuntimeError(f"Failed to remove package directory '{package_dir}': {e}")

    USER_APP_REGISTER.pop(package_name)
    safe_save_register()

    print(f"Package '{package_name}' removed successfully.")




def list_packages():
    """
    Display all installed packages from register.json.
    Shows package NAME and type.
    """
    if not USER_APP_REGISTER:
        print("No packages installed.")
        return

    print("Installed packages:")
    for name, info in sorted(USER_APP_REGISTER.items()):
        print(f" - {name} ({info.get('type', 'unknown')})")


def print_help():
    """Display command usage and syntax."""
    print("Usage: bob.py <command> [package]")
    print("Commands:")
    print("  install <package.tar.gz>   Install package from packs/")
    print("  remove  <package>          Remove installed package by name")
    print("  list                      List installed packages")
    print("  help                      Show this message")
    print("Legacy: bob.py <package.tar.gz> installs package")




# MAIN CLI DISPATCH
# ==================
# Entry point: parse command-line arguments and dispatch to appropriate handler.
# Supports both modern CLI modes (install/remove/list) and legacy tarball-only mode.

if __name__ == '__main__':
    safe_load_register()

    if len(s_args) < 2:
        print_help()
        sys.exit(1)

    cmd = s_args[1].lower()

    try:
        if cmd in ('install', 'add'):
            # Install mode: requires tarball filename as arg 2
            if len(s_args) < 3:
                raise ValueError("install requires a tarball argument")
            install_package(s_args[2])
        elif cmd in ('remove', 'uninstall', 'rm'):
            # Remove mode: requires registered package name as arg 2
            if len(s_args) < 3:
                raise ValueError("remove requires a tarball argument")
            remove_package(s_args[2])
        elif cmd in ('list', 'ls'):
            # List mode: no additional args needed
            list_packages()
        elif cmd in ('help', '-h', '--help', '?'):
            # Help mode: show usage
            print_help()
        else:
            # Legacy mode: treat arg 1 as tarball and install
            # This preserves backward compatibility with old shell.py calls
            install_package(s_args[1])
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

