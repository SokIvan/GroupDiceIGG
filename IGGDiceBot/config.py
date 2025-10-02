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
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}" if BOT_TOKEN else "/webhook"

# Проверка обязательных переменных
if not all([SUPABASE_URL, SUPABASE_KEY, BOT_TOKEN, ADMIN_CHAT_ID, MY_TG_ID]):
    missing = []
    if not SUPABASE_URL: missing.append("SUPABASE_URL")
    if not SUPABASE_KEY: missing.append("SUPABASE_KEY") 
    if not BOT_TOKEN: missing.append("BOT_TOKEN")
    if not ADMIN_CHAT_ID: missing.append("ADMIN_CHAT_ID")
    if not MY_TG_ID: missing.append("MY_TG_ID")
    raise Exception(f"Missing required environment variables: {', '.join(missing)}")