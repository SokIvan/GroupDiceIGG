import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
MY_TG_ID = os.getenv("MY_TG_ID")

# Webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"