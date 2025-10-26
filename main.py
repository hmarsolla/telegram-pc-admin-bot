"""
Telegram Bot for Remote PC Administration.

This bot allows authorized users to monitor and control their PC remotely
through Telegram commands. Features include system information, control
commands, file operations, and monitoring capabilities.
"""

import logging
import socket
import os
import datetime
import tempfile
from pathlib import Path

import psutil
import platform
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from requests import get
from mss import mss

import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Conversation states for System Control commands
SHUTDOWN = 1
RESTART = 2
SLEEP = 3
LOCK = 4
LOGOUT = 5


# Basic Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initialize the bot and greet authorized users."""
    if update.message.chat_id in config.CHATIDLIST:
        await update.message.reply_text("I'm a bot, please talk to me!")


async def where(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display hostname, local IPs, and public IP address."""
    await update.message.reply_text(f'Chat_id: {update.message.chat_id}')
    if update.message.chat_id in config.CHATIDLIST:
        ip_list = socket.gethostbyname_ex(socket.gethostname())
        await update.message.reply_text(f'Hostname: {ip_list[0]}')
        for number, ip in enumerate(ip_list[2]):
            msg = f'IP #{number + 1} - {ip}'
            await update.message.reply_text(msg)

        public_ip = get('https://api.ipify.org').text
        await update.message.reply_text(f'Public IP: {public_ip}')


async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the Telegram chat ID of the requester."""
    await update.message.reply_text(str(update.message.chat_id))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all available commands and their descriptions."""
    help_text = """
🤖 Telegram PC Admin Bot - Commands

📋 Basic Commands:
/start - Initialize the bot
/help or /commands - Show this help message
/getid - Get your Telegram chat ID
/where - Get hostname, local IPs, and public IP

💻 System Information:
/uptime - Show system uptime and boot time
/disk - Display disk usage for all partitions
/memory - Show RAM and swap memory usage
/cpu - Display CPU usage and frequency info
/processes - List top 10 processes by CPU usage
/temp - Show system temperature sensors (Linux only)

🔧 System Control:
/shutdown - Shut down the system (requires confirmation)
/restart - Restart the system (requires confirmation)
/sleep - Put system to sleep/suspend (requires confirmation)
/lock - Lock the screen immediately
/logout - Log out current user (requires confirmation)

📁 File System:
/screenshot - Capture and send a screenshot
/ls [path] - List files in a directory
/download <file_path> - Download a file from PC
/upload - Upload a file to PC (send file with caption)

📊 Monitoring:
/status - Get comprehensive system status overview
/log [lines] - View system logs (default 50, max 200)

ℹ️ Notes:
• All commands (except /getid) require authorization
• System control commands may require admin/sudo privileges
• File size limit for downloads: 50 MB
• Use /cancel to exit any confirmation prompt

For detailed documentation, see commands.md
    """
    await update.message.reply_text(help_text)


# System Information Commands
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display system uptime and boot time."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime_duration = datetime.datetime.now() - boot_time
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await update.message.reply_text(
        f"System Uptime:\n{days}d {hours}h {minutes}m {seconds}s\n"
        f"Booted: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display disk usage for all available partitions."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    disk_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append(
                f"📁 {partition.device}\n"
                f"  Mount: {partition.mountpoint}\n"
                f"  Total: {usage.total / (1024**3):.2f} GB\n"
                f"  Used: {usage.used / (1024**3):.2f} GB "
                f"({usage.percent}%)\n"
                f"  Free: {usage.free / (1024**3):.2f} GB"
            )
        except PermissionError:
            continue

    response = "\n\n".join(disk_info) if disk_info else \
        "No disk information available"
    await update.message.reply_text(response)


async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display RAM and swap memory usage statistics."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    await update.message.reply_text(
        f"💾 RAM:\n"
        f"  Total: {mem.total / (1024**3):.2f} GB\n"
        f"  Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)\n"
        f"  Available: {mem.available / (1024**3):.2f} GB\n\n"
        f"💿 Swap:\n"
        f"  Total: {swap.total / (1024**3):.2f} GB\n"
        f"  Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)\n"
        f"  Free: {swap.free / (1024**3):.2f} GB"
    )


async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display CPU usage, core count, and frequency information."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()

    core_info = "\n".join([
        f"  Core {i}: {percent}%"
        for i, percent in enumerate(cpu_percent)
    ])

    # Handle cpu_freq which might be None on some systems
    if cpu_freq:
        freq_info = (
            f"Frequency:\n"
            f"  Current: {cpu_freq.current:.2f} MHz\n"
            f"  Min: {cpu_freq.min:.2f} MHz\n"
            f"  Max: {cpu_freq.max:.2f} MHz"
        )
    else:
        freq_info = "Frequency: Not available on this system"

    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    overall_usage = psutil.cpu_percent(interval=1)

    await update.message.reply_text(
        f"🖥️ CPU Info:\n"
        f"  Cores: {physical_cores} physical, {logical_cores} logical\n"
        f"  Overall Usage: {overall_usage}%\n\n"
        f"Per Core Usage:\n{core_info}\n\n"
        f"{freq_info}"
    )


async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List the top 10 processes by CPU usage."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    # Get top 10 processes by CPU usage
    procs = []
    attrs = ['pid', 'name', 'cpu_percent', 'memory_percent']
    for proc in psutil.process_iter(attrs):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    procs = sorted(
        procs,
        key=lambda x: x['cpu_percent'] or 0,
        reverse=True
    )[:10]

    proc_list = ["Top 10 Processes by CPU:\n"]
    for proc in procs:
        cpu_pct = proc['cpu_percent']
        mem_pct = proc['memory_percent']
        proc_list.append(
            f"PID {proc['pid']}: {proc['name']}\n"
            f"  CPU: {cpu_pct:.1f}% | RAM: {mem_pct:.1f}%"
        )

    await update.message.reply_text("\n\n".join(proc_list))


async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display system temperature sensor readings (Linux only)."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            msg = "🌡️ Temperature sensors not available on this system"
            await update.message.reply_text(msg)
            return

        temp_info = ["🌡️ System Temperatures:\n"]
        for name, entries in temps.items():
            for entry in entries:
                label = entry.label or 'N/A'
                temp_info.append(f"{name} - {label}: {entry.current}°C")

        await update.message.reply_text("\n".join(temp_info))
    except AttributeError:
        msg = "🌡️ Temperature monitoring not supported on this platform"
        await update.message.reply_text(msg)


# System Control Commands
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request confirmation to shut down the system."""
    if update.message.chat_id in config.CHATIDLIST:
        yes_no = [['Yes', 'No']]
        markup = ReplyKeyboardMarkup(yes_no, one_time_keyboard=True)
        await update.message.reply_text('Are you sure?', reply_markup=markup)
        return SHUTDOWN
    else:
        return ConversationHandler.END


async def shutdown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute system shutdown if confirmed."""
    if update.message.text == 'Yes':
        await update.message.reply_text(
            'Shutting system down',
            reply_markup=ReplyKeyboardRemove()
        )

        # Execute appropriate shutdown command based on OS
        if os.name == 'nt':  # Windows
            os.system('shutdown /s /t 1')
        else:  # Linux/Unix
            os.system('sudo shutdown -h now')

    elif update.message.text == 'No':
        await update.message.reply_text(
            'You can call me if you change your mind!',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request confirmation to restart the system."""
    if update.message.chat_id not in config.CHATIDLIST:
        return ConversationHandler.END

    yes_no = [['Yes', 'No']]
    markup = ReplyKeyboardMarkup(yes_no, one_time_keyboard=True)
    await update.message.reply_text('Restart the system?', reply_markup=markup)
    return RESTART


async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute system restart if confirmed."""
    if update.message.text == 'Yes':
        await update.message.reply_text(
            'Restarting system...',
            reply_markup=ReplyKeyboardRemove()
        )

        if os.name == 'nt':  # Windows
            os.system('shutdown /r /t 1')
        else:  # Linux/Unix
            os.system('sudo reboot')
    else:
        await update.message.reply_text(
            'Restart cancelled',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def sleep_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request confirmation to put system to sleep."""
    if update.message.chat_id not in config.CHATIDLIST:
        return ConversationHandler.END

    yes_no = [['Yes', 'No']]
    markup = ReplyKeyboardMarkup(yes_no, one_time_keyboard=True)
    await update.message.reply_text(
        'Put system to sleep?',
        reply_markup=markup
    )
    return SLEEP


async def sleep_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute system sleep if confirmed."""
    if update.message.text == 'Yes':
        await update.message.reply_text(
            'Putting system to sleep...',
            reply_markup=ReplyKeyboardRemove()
        )

        if os.name == 'nt':  # Windows
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        else:  # Linux/Unix
            os.system('systemctl suspend')
    else:
        await update.message.reply_text(
            'Sleep cancelled',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def lock_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request confirmation to lock the screen."""
    if update.message.chat_id not in config.CHATIDLIST:
        return ConversationHandler.END

    yes_no = [['Yes', 'No']]
    markup = ReplyKeyboardMarkup(yes_no, one_time_keyboard=True)
    await update.message.reply_text('Lock the screen?', reply_markup=markup)
    return LOCK


async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute screen lock if confirmed."""
    if update.message.text == 'Yes':
        await update.message.reply_text(
            'Locking screen...',
            reply_markup=ReplyKeyboardRemove()
        )

        if os.name == 'nt':  # Windows
            os.system('rundll32.exe user32.dll,LockWorkStation')
        else:  # Linux/Unix
            # Try multiple lock methods for better compatibility
            lock_commands = [
                'loginctl lock-session',  # systemd
                'gnome-screensaver-command -l',  # GNOME
                'xdg-screensaver lock',  # Generic X11
                'dm-tool lock',  # LightDM
                'xscreensaver-command -lock'  # XScreensaver
            ]
            # Try each command until one works
            for cmd in lock_commands:
                result = os.system(f'{cmd} 2>/dev/null')
                if result == 0:
                    break
    else:
        await update.message.reply_text(
            'Lock cancelled',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def logout_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request confirmation to log out current user."""
    if update.message.chat_id not in config.CHATIDLIST:
        return ConversationHandler.END

    yes_no = [['Yes', 'No']]
    markup = ReplyKeyboardMarkup(yes_no, one_time_keyboard=True)
    await update.message.reply_text(
        'Log out current user?',
        reply_markup=markup
    )
    return LOGOUT


async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute user logout if confirmed."""
    if update.message.text == 'Yes':
        await update.message.reply_text(
            'Logging out...',
            reply_markup=ReplyKeyboardRemove()
        )

        if os.name == 'nt':  # Windows
            os.system('shutdown /l')
        else:  # Linux/Unix
            # Try different logout methods for Linux
            os.system('pkill -KILL -u $USER')  # More universal approach
    else:
        await update.message.reply_text(
            'Logout cancelled',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


# File System Commands
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture and send a screenshot of the primary monitor."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    try:
        with mss() as sct:
            # Create a temporary file to save the screenshot
            with tempfile.NamedTemporaryFile(
                suffix='.png',
                delete=False
            ) as tmp_file:
                tmp_filename = tmp_file.name

            # Save screenshot
            sct.shot(mon=1, output=tmp_filename)

            # Send as photo
            with open(tmp_filename, 'rb') as photo_file:
                timestamp = datetime.datetime.now()
                caption = timestamp.strftime('Screenshot - %Y-%m-%d %H:%M:%S')
                await update.message.reply_photo(
                    photo=photo_file,
                    caption=caption
                )

            # Clean up temp file
            os.unlink(tmp_filename)
    except Exception as e:
        await update.message.reply_text(
            f"Error taking screenshot: {str(e)}"
        )


async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List files and directories in the specified or current path."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    # Get path from command args or use current directory
    path = ' '.join(context.args) if context.args else '.'

    try:
        p = Path(path).resolve()
        if not p.exists():
            await update.message.reply_text(f"Path not found: {path}")
            return

        if p.is_file():
            size = p.stat().st_size
            await update.message.reply_text(
                f"📄 {p.name}\nSize: {size / 1024:.2f} KB"
            )
            return

        items = []
        for item in sorted(p.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size / 1024:.2f} KB)")

        if items:
            # Split into chunks if too many items
            chunk_size = 30
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i+chunk_size]
                header = f"📂 {p}:\n\n" if i == 0 else ""
                await update.message.reply_text(header + "\n".join(chunk))
        else:
            await update.message.reply_text(f"📂 {p}: Empty directory")

    except PermissionError:
        await update.message.reply_text(f"Permission denied: {path}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download a file from the PC and send it to Telegram."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    if not context.args:
        await update.message.reply_text("Usage: /download <file_path>")
        return

    file_path = ' '.join(context.args)

    try:
        p = Path(file_path).resolve()
        if not p.exists():
            await update.message.reply_text(f"File not found: {file_path}")
            return

        if not p.is_file():
            await update.message.reply_text(f"Not a file: {file_path}")
            return

        # Check file size (Telegram has 50MB limit for bots)
        size = p.stat().st_size
        max_size = 50 * 1024 * 1024
        if size > max_size:
            size_mb = size / (1024**2)
            await update.message.reply_text(
                f"File too large: {size_mb:.2f} MB (max 50 MB)"
            )
            return

        # Open and send file, then close properly
        with open(p, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=p.name,
                caption=f"File: {p.name}\nSize: {size / 1024:.2f} KB"
            )
    except PermissionError:
        await update.message.reply_text(f"Permission denied: {file_path}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Upload a file from Telegram to the PC."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    if not update.message.document:
        msg = (
            "Please send a document to upload.\n"
            "Usage: Send file with caption: /upload <destination_path>"
        )
        await update.message.reply_text(msg)
        return

    # Get destination path from caption or use downloads folder
    caption = update.message.caption or ""
    if caption.startswith("/upload"):
        dest_path = caption.replace("/upload", "").strip()
    else:
        dest_path = ""

    if not dest_path:
        downloads = Path.home() / "Downloads"
        dest_path = str(downloads / update.message.document.file_name)

    try:
        file = await update.message.document.get_file()
        dest = Path(dest_path).resolve()

        # Create parent directories if needed
        dest.parent.mkdir(parents=True, exist_ok=True)

        await file.download_to_drive(str(dest))
        await update.message.reply_text(f"✅ File uploaded to: {dest}")
    except Exception as e:
        await update.message.reply_text(f"Error uploading file: {str(e)}")


# Monitoring Commands
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get comprehensive system status overview."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    # Get system information
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()

    # Get root disk usage (handle different root paths for Windows/Linux)
    if os.name == 'nt':
        # Windows - use C: drive
        disk = psutil.disk_usage('C:\\')
    else:
        # Linux/Unix - use root
        disk = psutil.disk_usage('/')

    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime_duration = datetime.datetime.now() - boot_time

    uptime_days = uptime_duration.days
    uptime_hours = uptime_duration.seconds // 3600
    uptime_minutes = (uptime_duration.seconds % 3600) // 60

    status_msg = (
        f"🖥️ System Status\n\n"
        f"💻 Host: {platform.node()}\n"
        f"🐧 OS: {platform.system()} {platform.release()}\n"
        f"⏱️ Uptime: {uptime_days}d {uptime_hours}h {uptime_minutes}m\n\n"
        f"🔥 CPU: {cpu_percent}%\n"
        f"💾 RAM: {mem.percent}% "
        f"({mem.used / (1024**3):.2f}/{mem.total / (1024**3):.2f} GB)\n"
        f"💿 Disk: {disk.percent}% "
        f"({disk.used / (1024**3):.2f}/{disk.total / (1024**3):.2f} GB)\n"
    )

    await update.message.reply_text(status_msg)


async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View system logs with configurable number of lines."""
    if update.message.chat_id not in config.CHATIDLIST:
        return

    # Get number of lines from args (default 50)
    lines = 50
    if context.args:
        try:
            lines = int(context.args[0])
            lines = min(lines, 200)  # Max 200 lines
        except ValueError:
            pass

    try:
        if os.name == 'nt':  # Windows
            # Get Windows Event Log using PowerShell
            cmd = (
                f'powershell -Command "Get-EventLog -LogName System '
                f'-Newest {lines} | Format-Table -AutoSize '
                f'TimeGenerated,EntryType,Source,Message | '
                f'Out-String -Width 4096"'
            )
            try:
                result = os.popen(cmd).read()
                if result.strip():
                    # Split into chunks if too long
                    max_length = 4000
                    if len(result) > max_length:
                        chunks = [
                            result[i:i+max_length]
                            for i in range(0, len(result), max_length)
                        ]
                        for i, chunk in enumerate(chunks[:3]):
                            msg = (
                                f"Event Log (part {i+1}):\n```\n"
                                f"{chunk}\n```"
                            )
                            await update.message.reply_text(
                                msg,
                                parse_mode='Markdown'
                            )
                    else:
                        msg = (
                            f"System Event Log (last {lines} entries):\n"
                            f"```\n{result}\n```"
                        )
                        await update.message.reply_text(
                            msg,
                            parse_mode='Markdown'
                        )
                else:
                    await update.message.reply_text(
                        "Could not retrieve event log"
                    )
            except Exception as e:
                error_msg = (
                    f"Error reading Windows Event Log: {str(e)}\n"
                    "Try running bot with administrator privileges."
                )
                await update.message.reply_text(error_msg)
        else:  # Linux/Unix
            # Read system log
            log_files = [
                '/var/log/syslog',
                '/var/log/messages',
                '/var/log/system.log'
            ]
            log_content = None

            for log_file in log_files:
                if Path(log_file).exists():
                    try:
                        with open(log_file, 'r') as f:
                            all_lines = f.readlines()
                            log_content = ''.join(all_lines[-lines:])
                        break
                    except PermissionError:
                        continue

            if log_content:
                # Split into chunks if too long
                max_length = 4000
                if len(log_content) > max_length:
                    chunks = [
                        log_content[i:i+max_length]
                        for i in range(0, len(log_content), max_length)
                    ]
                    for i, chunk in enumerate(chunks[:3]):
                        msg = f"Log (part {i+1}):\n```\n{chunk}\n```"
                        await update.message.reply_text(
                            msg,
                            parse_mode='Markdown'
                        )
                else:
                    msg = (
                        f"System Log (last {lines} lines):\n"
                        f"```\n{log_content}\n```"
                    )
                    await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                error_msg = (
                    "Could not access system logs. Make sure log files "
                    "exist and bot has read permissions."
                )
                await update.message.reply_text(error_msg)
    except PermissionError:
        error_msg = (
            "Permission denied. Run bot with appropriate privileges "
            "to read logs."
        )
        await update.message.reply_text(error_msg)
    except Exception as e:
        await update.message.reply_text(f"Error reading logs: {str(e)}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current conversation."""
    await update.message.reply_text(
        'Cancelled',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    """Initialize and run the bot."""
    import asyncio

    # Create and set event loop for Windows
    if os.name == 'nt':  # Windows
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Create the Application
    application = Application.builder().token(config.TOKEN).build()

    # Add basic command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('where', where))
    application.add_handler(CommandHandler('getid', getid))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('commands', help_command))

    # Add shutdown conversation handler
    shutdown_handler = ConversationHandler(
        entry_points=[CommandHandler('shutdown', shutdown)],
        states={
            SHUTDOWN: [
                MessageHandler(filters.Regex('^(Yes|No)$'), shutdown_cmd)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(shutdown_handler)

    # System Information handlers
    application.add_handler(CommandHandler('uptime', uptime))
    application.add_handler(CommandHandler('disk', disk))
    application.add_handler(CommandHandler('memory', memory))
    application.add_handler(CommandHandler('cpu', cpu))
    application.add_handler(CommandHandler('processes', processes))
    application.add_handler(CommandHandler('temp', temp))

    # System Control handlers
    restart_handler = ConversationHandler(
        entry_points=[CommandHandler('restart', restart)],
        states={
            RESTART: [
                MessageHandler(filters.Regex('^(Yes|No)$'), restart_cmd)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(restart_handler)

    sleep_handler = ConversationHandler(
        entry_points=[CommandHandler('sleep', sleep_system)],
        states={
            SLEEP: [
                MessageHandler(filters.Regex('^(Yes|No)$'), sleep_cmd)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(sleep_handler)

    lock_handler = ConversationHandler(
        entry_points=[CommandHandler('lock', lock_system)],
        states={
            LOCK: [
                MessageHandler(filters.Regex('^(Yes|No)$'), lock_cmd)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(lock_handler)

    logout_handler = ConversationHandler(
        entry_points=[CommandHandler('logout', logout_system)],
        states={
            LOGOUT: [
                MessageHandler(filters.Regex('^(Yes|No)$'), logout_cmd)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(logout_handler)

    # File System handlers
    application.add_handler(CommandHandler('screenshot', screenshot))
    application.add_handler(CommandHandler('ls', ls))
    application.add_handler(CommandHandler('download', download))
    application.add_handler(MessageHandler(filters.Document.ALL, upload))

    # Monitoring handlers
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('log', log))

    print('IP Bot Started')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
