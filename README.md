# PyBOX 🖥️

> A fantasy virtual computer that simplifies packing software and blobs — with the feel of a complete configurable environment.

PyBOX is a Python-based virtual fantasy computer image that simulates a real computer environment. It features a custom shell, app registry, user management, encrypted storage, a `neofetch`-style system info module, and a `man` page system — all built from pure Python. This is the **Vanilla Image known as CrazyRag778's Image**.

---

## 📁 Project Structure

```
PyBOX/  # project root (repo folder remains by legacy name)
├── shell.py              # Main shell — entry point and command dispatcher
├── start.sh              # Shell script to launch PyOS
├── imp/
│   └── system.json       # System configuration (hostname, etc.)
├── ENV/
│   └── .system.json      # Runtime environment state
├── sbin/
│   ├── register.json     # System app registry (bob, passwd, man, etc.)
│   ├── bob/              # Package installer utility
│   ├── passwd/           # Password manager
│   ├── man/              # Manual page viewer
│   └── <appname>/
│       └── <appname>.py  # Each app lives in its own folder
├── bin/                  # User-installed applications
├── packs/                # Application packages (tarballs)
├── libs/                 # Shared libraries and reusable modules
├── README.md             # This file
└── .gitignore
```

---

## 🚀 Getting Started

### Launch PyBOX

```bash
python3 shell.py
```

You'll see the PyBOX prompt:
```
system@PyBOX$
```

---

## 🎮 Shell Commands

### Built-in Commands

#### System Information
```bash
status                 # Show system status (hostname, registered apps)
version                # Display PyBOX version info
help                   # Show all available commands
```

#### App Management
```bash
rebase                 # Reload app registries from register.json files
rebase system/bin      # Reload system and user app registries
```

#### Session Control
```bash
clear                  # Clear screen
killself               # Exit shell
shutdown               # Gracefully shutdown system
```

### System Commands (sbin/)

These are core commands registered in `sbin/register.json`:

#### **bob** — Package Manager
Installs and manages application packages.

```bash
bob install <package.tar.gz>    # Install package from packs/
bob remove <package_name>       # Remove installed package
bob list                        # List installed packages
bob help                        # Show bob usage
```

**Mechanism:**
- Extracts tarball from `packs/` to `bin/`
- Reads `manifest.json` from package to get NAME and type
- Registers app in `bin/register.json`
- Updates app registries after changes

Example:
```bash
bob install calculator.tar.gz
bob list
bob remove calculator
```

#### **passwd** — Password Manager
Changes system password stored in `imp/system.json`.

```bash
passwd <new_password>    # Set new password (no args for default prompt)
```

Default password is `root`. After first login, subsequent changes require current password verification.

#### **man** — Manual Page Viewer
Display manual pages for commands and applications.

```bash
man <command>           # Display man page for command
man bob                 # View bob package manager manual
man passwd              # View passwd utility manual
```

Each app in `sbin/<app>/` and `bin/<app>/` should include a `man.txt` file.

### User Commands (bin/)

User-installed applications are stored in `bin/` and loaded dynamically from `bin/register.json`.

Install applications using `bob`:
```bash
bob install myapp.tar.gz
myapp arg1 arg2         # Run installed app with arguments
```

---

## 🏗️ Architecture

### Command Dispatch Flow

```
User Input
    ↓
Parse command & arguments
    ↓
Match against:
  1. Built-in commands (help, status, clear, etc.)
  2. System apps (SYSTEM_APP_REGISTER_LIST from sbin/register.json)
  3. User apps (APP_REGISTER_LIST from bin/register.json)
    ↓
Execute or dispatch
    ↓
Return output to shell
```

### App Registry System

PyOS uses **two-tier app registry**:

1. **System Apps** (`sbin/register.json`)
   - Core system utilities
   - Pre-installed with PyOS
   - Example: bob, passwd, man

2. **User Apps** (`bin/register.json`)
   - Dynamically installed packages
   - Managed by `bob` installer
   - Hot-reloaded via `rebase` command

Registry JSON format:
```json
{
  "app_name": {
    "NAME": "app_name",
    "type": "utility|tool|system"
  }
}
```

### Error Handling

The shell gracefully handles:
- **Missing registry files** → Initialize empty registries
- **Corrupted JSON** → Warn user and continue
- **Missing app executables** → Display error message
- **Subprocess failures** → Catch and report to user
- **Invalid input** → Show command not found and suggest help
- **EOF/Interrupt** → Handle Ctrl+D and Ctrl+C gracefully

---

## 📦 Creating Application Packages

### Package Structure

Create a tarball with this structure:
```
myapp.tar.gz
└── myapp/
    ├── myapp.py          # Main executable
    ├── manifest.json     # Package metadata
    ├── man.txt           # Manual page (optional)
    └── <other files>
```

### manifest.json Example

```json
{
  "NAME": "myapp",
  "type": "utility",
  "version": "1.0",
  "description": "My awesome application"
}
```

Required fields: `NAME` and `type`

### myapp.py Example

```python
import sys

if len(sys.argv) > 1:
    name = sys.argv[1]
    print(f"Hello, {name}!")
else:
    print("Hello, World!")
```

### Install Package

```bash
# Copy tarball to packs/ directory
cp myapp.tar.gz packs/

# Use bob to install
bob install myapp.tar.gz

# Run from shell
myapp John
```

---

## 🔧 System Configuration

### imp/system.json

Contains image-level settings:
```json
{
  "HOSTNAME": "PyBOX",
  "password": "root"
}
```

Edit this to customize your PyBOX instance.

### ENV/.system.json

Runtime state (auto-managed):
```json
{
  "turned_on": true
}
```

---

## 🛠️ Development

### Adding New System Commands

1. Create directory: `sbin/<mycommand>/`
2. Add `<mycommand>/<mycommand>.py`
3. Add entry to `sbin/register.json`:
   ```json
   {
     "mycommand": {
       "NAME": "mycommand",
       "type": "system"
     }
   }
   ```
4. Invoke `rebase` in shell to reload registries

---

## 📝 Examples

### Example Session

```bash
# Start PyBOX
python3 shell.py

# Check status
status
# Output:
# Hostname: PyBOX
# System Apps: bob, man, passwd
# User Apps: (none)

# Install a package
bob install myapp.tar.gz

# Verify installation
bob list

# Run the app
myapp argument1

# Check available commands
help

# Exit
shutdown
```

### Example: Creating and Installing a Package

```bash
# Create package structure
mkdir -p myapp_pkg/myapp
cd myapp_pkg/myapp

# Create app code
cat > myapp.py << 'EOF'
import sys
print("MyApp v1.0")
print(f"Args: {sys.argv[1:]}")
EOF

# Create manifest
cat > manifest.json << 'EOF'
{
  "NAME": "myapp",
  "type": "utility",
  "version": "1.0"
}
EOF

# Create manual page
cat > man.txt << 'EOF'
myapp: Example application

USAGE
  myapp [args]

DESCRIPTION
  This is an example application.
EOF

# Create tarball
cd ..
tar czf myapp.tar.gz myapp/
cp myapp.tar.gz /path/to/PyOS/packs/

# Install in PyOS
# (in PyOS shell)
bob install myapp.tar.gz
myapp test
```

---

## 🐛 Troubleshooting

### Command Not Found

Check if the app is registered:
```bash
help          # Show all available commands
status        # Check system/user apps
bob list      # For installed apps
```

If app is installed but not showing:
```bash
rebase        # Reload registries
```

### Registry Errors

Check JSON files manually:
```bash
# Outside PyOS
cat sbin/register.json    # Should be valid JSON
cat bin/register.json
```

### Missing Dependencies

PyOS requires only Python 3.6+. All functionality is built with Python standard library:
- `json` — Configuration and registry
- `os` — File system operations
- `subprocess` — App execution
- `tarfile` — Package extraction
- `shutil` — Directory operations

---

## 📄 License

See [LICENSE](LICENSE) file.

---

## 🤝 Contributing

This is a fantasy OS project. Feel free to fork and extend with new features!

Suggestions for enhancements:
- File editor (`ed` or `vim`-style)
- User management system
- Process/job management
- Network simulation
- File permissions system
- Pipe support (|) for chaining commands

