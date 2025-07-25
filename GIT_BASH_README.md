# Stock Scanner - Git Bash Setup Guide

This guide is specifically for Windows users who prefer using Git Bash for development. Git Bash provides a Unix-like command line experience on Windows.

## 🚀 Quick Start with Git Bash

### Prerequisites
1. **Git for Windows** - Download from [git-scm.com](https://git-scm.com/download/win)
   - This includes Git Bash automatically
2. **Python 3.8+** - Download from [python.org](https://python.org)
   - ✅ Make sure to check "Add Python to PATH" during installation
3. **MySQL Server** - Download from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Run the automated setup
bash setup_git_bash.sh
```

That's it! The script will handle everything automatically.

## 🛠️ Manual Setup (Step by Step)

### Step 1: Open Git Bash
- Right-click in your project folder
- Select "Git Bash Here"
- Or open Git Bash and navigate to your project: `cd /c/path/to/your/project`

### Step 2: Load Helper Commands
```bash
# Load helpful commands and aliases
source git_bash_commands.sh

# This gives you access to shortcuts like:
# - setup (run full setup)
# - start (start Django server)
# - migrate (run migrations)
# - And many more!
```

### Step 3: Run Setup
```bash
# Option 1: Full automated setup
setup

# Option 2: Quick setup (if you know what you're doing)
quick_setup

# Option 3: Manual step by step
install_deps
create_db
migrate
```

### Step 4: Start the Application
```bash
# Start Django development server
start

# Or start on a different port
start_port 8080
```

## 📋 Available Git Bash Commands

After running `source git_bash_commands.sh`, you get access to these commands:

### Setup Commands
- `setup` - Run the full automated setup script
- `quick_setup` - Quick setup for experienced users
- `install_deps` - Install Python dependencies only

### Database Commands
- `create_db` - Create MySQL database and user
- `test_db` - Test database connection
- `reset_db` - Reset database (⚠️ WARNING: deletes all data)

### Django Commands
- `start` - Start Django development server
- `start_port <port>` - Start server on specific port
- `migrate` - Run Django migrations
- `create_admin` - Create Django superuser
- `shell` - Open Django shell
- `check_django` - Run Django system check
- `show_migrations` - Show migration status

### Utility Commands
- `cleanup` - Clean cache and temporary files
- `status` - Show project status
- `load_stocks` - Load NASDAQ stock data
- `logs [lines]` - Show application logs

### Git Shortcuts
- `gs` - git status
- `ga` - git add
- `gc` - git commit
- `gp` - git push
- `gl` - git pull
- `quick_commit [message]` - Quick commit and push
- `update` - Pull changes and update project

### Help
- `help_commands` - Show all available commands

## 🔍 Common Git Bash Usage Patterns

### Daily Development Workflow
```bash
# Load commands (do this once per session)
source git_bash_commands.sh

# Check project status
status

# Start development server
start

# In another Git Bash window:
# Make changes to code...

# Quick commit and push
quick_commit "Fixed bug in stock filtering"

# Update from remote
update
```

### First Time Setup
```bash
# Clone and setup
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Load helper commands
source git_bash_commands.sh

# Run full setup
setup

# Create admin user
create_admin

# Start server
start
```

### Troubleshooting Workflow
```bash
# Load commands
source git_bash_commands.sh

# Check status
status

# Test database
test_db

# Clean up files
cleanup

# Reset migrations if needed
reset_db
migrate

# Check Django
check_django
```

## 🐛 Troubleshooting Git Bash Issues

### 1. Python Not Found
**Error**: `python: command not found`

**Solution**:
```bash
# Check if Python is installed
python --version
python3 --version

# If not found, add to PATH or reinstall Python
# Make sure to check "Add Python to PATH" during installation
```

### 2. MySQL Not Found
**Error**: `mysql: command not found`

**Solutions**:
```bash
# Check common MySQL locations
ls "/c/Program Files/MySQL"
ls "/c/xampp/mysql/bin"

# Add MySQL to PATH temporarily
export PATH="/c/Program Files/MySQL/MySQL Server 8.0/bin:$PATH"

# Or use full path
"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe" --version
```

### 3. Permission Denied
**Error**: `Permission denied` when running scripts

**Solution**:
```bash
# Make script executable
chmod +x setup_git_bash.sh

# Or run with bash explicitly
bash setup_git_bash.sh
```

### 4. Windows Path Issues
**Error**: Path not found or weird path errors

**Solutions**:
```bash
# Use forward slashes in Git Bash
cd /c/Users/YourName/Documents/project

# Convert Windows path to Git Bash path
# Windows: C:\Users\Name\project
# Git Bash: /c/Users/Name/project
```

### 5. Unicode/Encoding Issues
**Error**: Character encoding problems

**Solution**:
```bash
# Set UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Use the Windows-compatible scripts
bash setup_git_bash.sh  # Instead of the Python scripts
```

## 🔧 Advanced Git Bash Configuration

### Auto-load Commands
Add this to your `~/.bashrc` file to automatically load commands:

```bash
# Add to ~/.bashrc
if [[ -f "/path/to/stock-scanner-complete/git_bash_commands.sh" ]]; then
    source "/path/to/stock-scanner-complete/git_bash_commands.sh"
fi
```

### Custom Aliases
Add your own aliases to `~/.bashrc`:

```bash
# Custom aliases for Stock Scanner
alias scanner='cd /c/path/to/stock-scanner-complete && source git_bash_commands.sh'
alias dev_start='cd /c/path/to/stock-scanner-complete && start'
alias dev_status='cd /c/path/to/stock-scanner-complete && status'
```

### Git Configuration
Set up Git for the project:

```bash
# Configure Git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Project-specific configuration
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## 📁 Git Bash File Paths

Understanding file paths in Git Bash:

```bash
# Windows paths vs Git Bash paths
Windows: C:\Users\Name\Documents\project
Git Bash: /c/Users/Name/Documents/project

Windows: D:\Development\stock-scanner
Git Bash: /d/Development/stock-scanner

# Current directory shortcuts
.       # Current directory  
..      # Parent directory
~       # Home directory (/c/Users/YourName)
```

## 🎯 Best Practices for Git Bash

1. **Always use forward slashes** for paths
2. **Use tab completion** - type first few letters and press Tab
3. **Use `source git_bash_commands.sh`** to load helper functions
4. **Keep Git Bash windows organized** - one for server, one for commands
5. **Use `status` command** to check project health regularly
6. **Commit frequently** with `quick_commit`

## 🚀 Performance Tips

1. **Close unnecessary programs** when running the server
2. **Use `cleanup` command** regularly to remove cache files
3. **Monitor database size** - reset if it gets too large during development
4. **Use `start_port` command** if port 8000 is busy

## 📝 Development Workflow Example

```bash
# Morning routine
cd /c/path/to/stock-scanner-complete
source git_bash_commands.sh
gl  # git pull
status
start

# Development work...
# (server running in background)

# End of day
quick_commit "Daily development progress"
cleanup
```

---

**Need help?** 
- Type `help_commands` in Git Bash
- Check the main `WINDOWS_SETUP_README.md`
- Create an issue on GitHub