# Telegram PC Admin Bot

> **Note:** This repository was formerly known as "telegram-bot-get-ip" and has been expanded with comprehensive PC administration features.

A comprehensive Telegram bot for remotely monitoring and controlling your PC from anywhere. Get system information, manage files, take screenshots, and execute system commands - all through Telegram messages.

## 🌟 Features

### 📋 Basic Functions
- Get your system's IP addresses (local and public)
- Retrieve system hostname
- Authorization-based access control

### 💻 System Monitoring
- **Real-time Stats**: CPU usage, memory usage, disk space
- **System Info**: Uptime, boot time, OS details
- **Process Monitoring**: View top processes by CPU usage
- **Temperature Sensors**: Monitor system temperatures (Linux)
- **System Logs**: Read and view system event logs

### 🔧 System Control
- **Power Management**: Shutdown, restart, sleep
- **Session Control**: Lock screen, logout user
- All commands include confirmation prompts for safety

### 📁 File Management
- **Screenshot**: Capture and receive screenshots remotely
- **File Browser**: List directory contents
- **File Transfer**: Upload and download files (up to 50MB)
- Works with both Windows and Linux paths

### 🛡️ Security
- Chat ID whitelist - only authorized users can control the bot
- Confirmation prompts for destructive operations
- Secure file access within system permissions

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/hmarsolla/telegram-bot-get-ip.git
cd telegram-bot-get-ip
pip install -r requirements.txt
```

### Configuration

1. Create a Telegram bot via [@BotFather](https://t.me/botfather) and get your bot token
2. Get your Chat ID by messaging the bot and using `/getid`
3. Copy the example environment file and configure it:

```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:

```bash
# Telegram Bot API Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Authorized Chat IDs (comma-separated)
AUTHORIZED_CHAT_IDS=your_chat_id_here,additional_id_here
```

**Security Note:** The `.env` file is automatically ignored by git to protect your credentials.

### Run the Bot

```bash
python main.py
```

## 📱 Available Commands

### Basic Commands
- `/start` - Initialize the bot
- `/help` or `/commands` - Show all available commands
- `/getid` - Get your Telegram chat ID
- `/where` - Get hostname, local IPs, and public IP

### System Information
- `/uptime` - System uptime and boot time
- `/disk` - Disk usage for all partitions
- `/memory` - RAM and swap memory statistics
- `/cpu` - CPU usage and frequency information
- `/processes` - Top 10 processes by CPU usage
- `/temp` - System temperature sensors (Linux only)

### System Control
- `/shutdown` - Shut down the system
- `/restart` - Restart the system
- `/sleep` - Put system to sleep/suspend
- `/lock` - Lock the screen
- `/logout` - Log out current user

### File System
- `/screenshot` - Capture and send a screenshot
- `/ls [path]` - List files in a directory
- `/download <file_path>` - Download a file from PC
- Send a file with caption `/upload [path]` - Upload file to PC

### Monitoring
- `/status` - Comprehensive system status overview
- `/log [lines]` - View system logs (default 50, max 200)

**Note:** Use `/cancel` to exit any confirmation prompt.

## 🐳 Docker Usage

### Build the Image

```bash
docker build -t telegram-pc-admin-bot .
```

### Run the Container

```bash
docker run -v /path/to/your/config.py:/app/config.py telegram-pc-admin-bot
```

**Note:** Docker deployment has limitations with system control commands (shutdown, restart, etc.) as they affect the host system.

## 💻 Platform Compatibility

| Feature | Windows | Linux | Notes |
|---------|---------|-------|-------|
| Basic Commands | ✅ | ✅ | Fully compatible |
| System Information | ✅ | ✅ | All commands work |
| Temperature Monitoring | ❌ | ✅ | Requires lm-sensors on Linux |
| System Control | ✅ | ✅ | May require sudo on Linux |
| Screenshots | ✅ | ✅ | Requires graphical environment |
| File Operations | ✅ | ✅ | Cross-platform paths |
| Log Viewing | ✅ | ✅ | Event Log (Win) / syslog (Linux) |

## 🔧 Requirements

- Python 3.14+
- python-telegram-bot 21.7
- psutil 6.1.1
- mss 10.0.0
- requests 2.32.3

All dependencies are listed in `requirements.txt`

## 🔐 Linux Setup (Optional)

### For System Control Commands

Configure passwordless sudo for specific commands:

```bash
sudo visudo
```

Add these lines (replace `username` with your username):

```
username ALL=(ALL) NOPASSWD: /sbin/shutdown
username ALL=(ALL) NOPASSWD: /sbin/reboot
```

### For Temperature Monitoring

```bash
sudo apt-get install lm-sensors
sudo sensors-detect
```

### For Screenshot Support

Requires a graphical environment (X11 or Wayland with compatibility mode).

## 📖 Documentation

- **[commands.md](commands.md)** - Detailed command reference with examples
- **[PLATFORM_COMPATIBILITY.md](PLATFORM_COMPATIBILITY.md)** - Cross-platform compatibility guide

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new commands
- Improve existing functionality
- Fix bugs
- Improve documentation

## ⚠️ Security Considerations

- **Keep your bot token secret** - Never commit it to version control
- **Whitelist trusted users only** - Use the CHATIDLIST in config.py
- **Be cautious with system control** - Commands like shutdown can disrupt operations
- **File access permissions** - Bot has access to all files the user can read/write
- **Run with appropriate privileges** - Some commands require admin/sudo access

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with:
- [python-telegram-bot](https://python-telegram-bot.org/)
- [psutil](https://github.com/giampaolo/psutil)
- [mss](https://github.com/BoboTiG/python-mss)

---

**Last Updated:** October 26, 2025  
**Python Version:** 3.14+  
**Bot Version:** 2.0