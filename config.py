"""
Configuration file for Telegram Bot.

Loads configuration from .env file using python-dotenv.
Contains authentication tokens and authorized chat IDs.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot API token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# List of authorized Telegram chat IDs
# Parse comma-separated string into list of integers
chat_ids_str = os.getenv('AUTHORIZED_CHAT_IDS', '')
CHATIDLIST = [int(id.strip()) for id in chat_ids_str.split(',') if id.strip()]

# Validate configuration
if not TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN not found in .env file. "
        "Please copy .env.example to .env and configure it."
    )

if not CHATIDLIST:
    raise ValueError(
        "AUTHORIZED_CHAT_IDS not found in .env file. "
        "Please add at least one authorized chat ID."
    )
