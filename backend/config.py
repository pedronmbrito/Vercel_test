import os
from dotenv import load_dotenv

load_dotenv()

# Slack credentials
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL")

# Server
PORT = int(os.environ.get("PORT", 3000))

# App settings
CHECKIN_TIME = "09:00"  # Default check-in time
REPORT_TIME = "17:00"   # Default report time
