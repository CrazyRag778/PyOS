import os
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("usage: man <app_name>")
        sys.exit(1)

    app_name = sys.argv[1]

    base_dir = Path(__file__).parent

    # First try: sbin/app_name/man.txt
    SBIN_MAN_FILE = base_dir / ".." / app_name / "man.txt"

    # Second try: bin/app_name/man.txt
    BIN_MAN_FILE = base_dir / ".." / ".." / "bin" / app_name / "man.txt"

    for man_file in [SBIN_MAN_FILE, BIN_MAN_FILE]:
        if man_file.exists():
            try:
                data = man_file.read_text()
                print(f"Manual page for {app_name}")
                print(data)
                return
            except Exception as e:
                print(f"Error reading manual page: {e}")
                sys.exit(1)

    print(f"man: no manual entry for {app_name}")

if __name__ == "__main__":
    main()
