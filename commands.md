# Telegram PC Admin Bot - Commands Documentation

This bot allows you to remotely monitor and control your PC through Telegram. All commands are restricted to authorized chat IDs configured in `config.py`.

## 📋 Table of Contents
- [Basic Commands](#basic-commands)
- [System Information](#system-information)
- [System Control](#system-control)
- [File System](#file-system)
- [Monitoring](#monitoring)

---

## Basic Commands

### `/start`
**Description:** Initialize the bot and receive a welcome message.

**Usage:**
```
/start
```

**Response:** Confirmation message that the bot is active.

---

### `/getid`
**Description:** Get your Telegram chat ID. Useful for adding new authorized users to the bot.

**Usage:**
```
/getid
```

**Response:** Your numeric chat ID.

---

### `/where`
**Description:** Get network information including hostname, local IP addresses, and public IP address.

**Usage:**
```
/where
```

**Response:** 
- Hostname
- Local IP address(es)
- Public IP address

---

## System Information

### `/uptime`
**Description:** Display how long the system has been running since last boot.

**Usage:**
```
/uptime
```

**Response:**
- Uptime in days, hours, minutes, and seconds
- Boot timestamp

---

### `/disk`
**Description:** Show disk usage information for all mounted partitions.

**Usage:**
```
/disk
```

**Response:**
- For each partition:
  - Device name
  - Mount point
  - Total space
  - Used space (with percentage)
  - Free space

---

### `/memory`
**Description:** Display RAM and swap memory usage statistics.

**Usage:**
```
/memory
```

**Response:**
- **RAM:**
  - Total memory
  - Used memory (with percentage)
  - Available memory
- **Swap:**
  - Total swap
  - Used swap (with percentage)
  - Free swap

---

### `/cpu`
**Description:** Show detailed CPU information and usage statistics.

**Usage:**
```
/cpu
```

**Response:**
- Number of physical and logical cores
- Overall CPU usage percentage
- Per-core usage percentages
- CPU frequency (current, min, max)

---

### `/processes`
**Description:** List the top 10 processes by CPU usage.

**Usage:**
```
/processes
```

**Response:**
- For each process:
  - Process ID (PID)
  - Process name
  - CPU usage percentage
  - Memory usage percentage

---

### `/temp`
**Description:** Display system temperature readings from available sensors.

**Usage:**
```
/temp
```

**Response:**
- Temperature readings from various sensors (if available)
- Note: May not be available on all systems/platforms

---

## System Control

### `/shutdown`
**Description:** Shut down the system. Requires confirmation.

**Usage:**
```
/shutdown
```

**Interactive:** The bot will ask for confirmation (Yes/No) before executing.

**Behavior:**
- **Windows:** Executes `shutdown /s /t 1` (shutdown in 1 second)
- **Linux/Unix:** Executes `sudo shutdown -h now`

---

### `/restart`
**Description:** Restart the system. Requires confirmation.

**Usage:**
```
/restart
```

**Interactive:** The bot will ask for confirmation (Yes/No) before executing.

**Behavior:**
- **Windows:** Executes `shutdown /r /t 1`
- **Linux/Unix:** Executes `sudo reboot`

---

### `/sleep`
**Description:** Put the system into sleep/suspend mode. Requires confirmation.

**Usage:**
```
/sleep
```

**Interactive:** The bot will ask for confirmation (Yes/No) before executing.

**Behavior:**
- **Windows:** Executes suspend via PowerShell
- **Linux/Unix:** Executes `systemctl suspend`

---

### `/lock`
**Description:** Lock the screen immediately (no confirmation required).

**Usage:**
```
/lock
```

**Behavior:**
- **Windows:** Locks the workstation
- **Linux/Unix:** Executes `loginctl lock-session`

---

### `/logout`
**Description:** Log out the current user. Requires confirmation.

**Usage:**
```
/logout
```

**Interactive:** The bot will ask for confirmation (Yes/No) before executing.

**Behavior:**
- **Windows:** Executes `shutdown /l`
- **Linux/Unix:** Terminates user session via loginctl

---

## File System

### `/screenshot`
**Description:** Capture and send a screenshot of the primary monitor.

**Usage:**
```
/screenshot
```

**Response:** Image file with timestamp caption.

**Note:** Captures the primary/main display only.

---

### `/ls [path]`
**Description:** List files and directories in the specified path.

**Usage:**
```
/ls
/ls /home/user/documents
/ls C:\Users\Username\Desktop
```

**Parameters:**
- `path` (optional): Directory path to list. Defaults to current directory if not specified.

**Response:**
- For directories: 📁 Directory name/
- For files: 📄 Filename (size in KB)

**Note:** Long listings are split into multiple messages (30 items per message).

---

### `/download <file_path>`
**Description:** Download a file from the PC to your Telegram.

**Usage:**
```
/download /path/to/file.txt
/download C:\Users\Username\document.pdf
```

**Parameters:**
- `file_path` (required): Full path to the file to download.

**Limitations:**
- Maximum file size: 50 MB (Telegram bot API limit)
- File must exist and be readable

**Response:** The file is sent as a Telegram document with size information.

---

### `/upload` (via file)
**Description:** Upload a file from Telegram to the PC.

**Usage:**
1. Send a file to the bot
2. In the file caption, type: `/upload /destination/path/filename.ext`
3. If no path is specified, file is saved to ~/Downloads/

**Examples:**
```
Caption: /upload /home/user/documents/report.pdf
Caption: /upload C:\Users\Username\file.txt
Caption: /upload
```

**Note:** If destination path is not provided, file is saved to the user's Downloads folder.

---

## Monitoring

### `/status`
**Description:** Get a comprehensive overview of system status.

**Usage:**
```
/status
```

**Response:**
- Hostname
- Operating system and version
- System uptime
- CPU usage percentage
- RAM usage (percentage and GB)
- Disk usage (percentage and GB)

**Use Case:** Quick health check of the system.

---

### `/log [lines]`
**Description:** View recent system log entries.

**Usage:**
```
/log
/log 100
/log 200
```

**Parameters:**
- `lines` (optional): Number of log lines to display. Default: 50, Maximum: 200

**Behavior:**
- **Windows:** Windows event log viewing (not fully implemented)
- **Linux/Unix:** Reads from `/var/log/syslog` or `/var/log/messages`

**Note:** 
- Requires appropriate permissions to read system logs
- Long logs are split into multiple messages (max 4000 characters per message)
- Maximum 3 message chunks

---

### `/cancel`
**Description:** Cancel any ongoing operation that requires confirmation.

**Usage:**
```
/cancel
```

**Use Case:** Exit from `/shutdown`, `/restart`, `/sleep`, or `/logout` confirmation prompts.

---

## Security Notes

⚠️ **Important Security Considerations:**

1. **Authorized Users Only:** All commands (except `/getid`) are restricted to chat IDs listed in `config.CHATIDLIST`.

2. **Sudo Permissions:** On Linux/Unix systems, many system control commands require sudo privileges. Configure passwordless sudo or run the bot with appropriate permissions.

3. **File Access:** File system commands have access to all files the bot user can read/write. Be cautious with file paths.

4. **Network Security:** Keep your bot token secure and never share it publicly.

5. **System Control:** Commands like `/shutdown`, `/restart`, and `/logout` can disrupt system operation. Use with caution.

---

## Configuration

Edit `config.py` to set:
- `TOKEN`: Your Telegram bot token from @BotFather
- `CHATIDLIST`: List of authorized chat IDs (use `/getid` to get yours)

Example:
```python
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
CHATIDLIST = [123456789, 987654321]
```

---

## Platform Compatibility

| Command | Windows | Linux/Unix | Notes |
|---------|---------|------------|-------|
| Basic Commands | ✅ | ✅ | Fully compatible |
| `/uptime` | ✅ | ✅ | psutil cross-platform |
| `/disk` | ✅ | ✅ | psutil cross-platform |
| `/memory` | ✅ | ✅ | psutil cross-platform |
| `/cpu` | ✅ | ✅ | Handles missing frequency data |
| `/processes` | ✅ | ✅ | psutil cross-platform |
| `/temp` | ❌ | ✅ | Requires lm-sensors on Linux |
| `/shutdown` | ✅ | ✅ | Requires sudo on Linux |
| `/restart` | ✅ | ✅ | Requires sudo on Linux |
| `/sleep` | ✅ | ✅ | May require permissions on Linux |
| `/lock` | ✅ | ✅ | Multiple fallbacks for Linux |
| `/logout` | ✅ | ✅ | Uses pkill for better Linux compatibility |
| `/screenshot` | ✅ | ✅ | Requires graphical environment |
| `/ls` | ✅ | ✅ | pathlib handles paths |
| `/download` | ✅ | ✅ | pathlib handles paths |
| `/upload` | ✅ | ✅ | pathlib handles paths |
| `/status` | ✅ | ✅ | Handles different root paths |
| `/log` | ✅ | ✅ | PowerShell on Windows, syslog on Linux |

---

## Requirements

- Python 3.14+
- python-telegram-bot 21.7
- psutil 6.1.1
- mss 10.0.0
- requests 2.32.3

Install with:
```bash
pip install -r requirements.txt
```

---

## Running the Bot

```bash
python main.py
```

Or with Docker:
```bash
docker build -t telegram-pc-admin-bot .
docker run -v $(pwd)/config.py:/app/config.py telegram-pc-admin-bot
```

---

## Troubleshooting

### Command not working?
- Verify your chat ID is in `config.CHATIDLIST`
- Check bot logs for error messages
- Ensure required permissions (especially for system control commands)

### File operations failing?
- Verify file paths are correct
- Check file permissions
- Ensure file size is under 50 MB for downloads

### System control commands not working on Linux?
- Configure passwordless sudo for required commands
- Or run bot with appropriate privileges
- Check system logs with `journalctl -xe`

---

## Contributing

Feel free to add new commands or improve existing ones. Make sure to:
1. Add appropriate authorization checks
2. Handle both Windows and Linux/Unix platforms
3. Include proper error handling
4. Update this documentation

---

## License

[Add your license here]

---

**Last Updated:** October 26, 2025
