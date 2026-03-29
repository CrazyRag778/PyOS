# PyOS 🖥️

> A fantasy computer that simplifies packing of software and blobs — with the full feel of a complete OS.

PyOS is a Python-based operating system shell that simulates a real computer environment. It features a custom shell, app registry, user management, encrypted storage, a `neofetch`-style system info module, and a `man` page system — all built from pure Python.

---

## 📁 Project Structure

```
PyOS/
├── shell.py              # Main shell — entry point of the OS
├── start.sh              # Shell script to launch PyOS
├── imp/
│   └── system.json       # System configuration (hostname, etc.)
├── ENV/
│   └── .system.json      # Runtime environment state
├── sbin/
│   ├── register.json     # App registry
│   └── <appname>/
│       └── <appname>.py  # Each app lives in its own folder
├── bin/                  # Binary utilities
├── libs/                 # Shared libraries and reusable modules
└── .gitignore
```

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- Linux (recommended) or any Unix-like system

### Run

```bash
bash start.sh
```

Or directly:

```bash
python3 shell.py
```

---

## 🐚 Shell Usage

Once PyOS starts, you get an interactive shell prompt:

```
[home] system@myhostname$
```

### Built-in Commands

| Command | Description |
|---|---|
| `shutdown` | Gracefully shuts down PyOS |
| `killself` | Force-exits the shell |
| `clear` | Clears the terminal screen |
| `mkdir <name>` | Creates a directory |
| `<appname> [args]` | Runs a registered app from `sbin/` |

Any unrecognized command prints:
```
shell: command not found: <cmd>
```

---

## 📦 App System

Apps are registered in `sbin/register.json` and stored under `sbin/<appname>/<appname>.py`.

To add a new app:

1. Create a folder: `sbin/myapp/`
2. Add your script: `sbin/myapp/myapp.py`
3. Register it in `sbin/register.json`:

```json
{
  "myapp": {}
}
```

Apps are then callable directly from the shell:

```
[home] system@hostname$ myapp
```

---

## ⚙️ Configuration

**`imp/system.json`** — Static system config:
```json
{
  "HOSTNAME": "pyos-machine"
}
```

**`ENV/.system.json`** — Runtime state (auto-managed):
```json
{
  "turned_on": true
}
```

---

## 🔐 Security

PyOS includes **Fernet-based encryption** as a reusable module in `libs/` for securing sensitive data such as user passwords. The `passwd.py` utility handles user management with encrypted credentials.

---

## 🧩 Features

- **Custom Shell** — Interactive prompt with hostname display and working directory
- **App Registry** — Plug-and-play app system via `sbin/` and `register.json`
- **User Management** — `passwd`-style user creation and authentication
- **Fernet Encryption** — Encrypted storage for sensitive system data
- **`neofetch`-style Module** — System info display (OS, hostname, kernel, etc.)
- **`man` Page System** — Built-in manual pages for PyOS commands
- **Absolute Path Resolution** — All paths resolved relative to `shell.py` via `os.path.dirname(os.path.abspath(__file__))`

---

## 🛠️ Development Conventions

- All subprocess calls use list mode with `cwd=BASE_DIR`
- JSON read and write use **separate `with` blocks**
- Shared utilities live in `libs/` for reuse across apps
- Comments are present in all source files

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**CrazyRag778** — [github.com/CrazyRag778](https://github.com/CrazyRag778)
