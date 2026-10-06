import os
from dotenv import load_dotenv

# Automatically load the .env file if it exists
load_dotenv()

# ==========================================
# EMEC BOT CONFIGURATION
# ==========================================

BOT_NAME = "EmecTech Bot"
CHANNEL_NAME = "CampusZone"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# Schedule settings (06:00 AM WAT)
POST_TIME = "06:00"

# Target filters / preferences
TARGET_DEGREE_LEVELS = ["Undergraduate", "Masters", "PhD", "Fellowship"]

# Telegram Credentials (Now safely loaded from .env or GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
