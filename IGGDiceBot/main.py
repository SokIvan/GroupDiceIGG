from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from bot import bot, dp, db
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, MY_TG_ID
import asyncio
import threading
import time
import requests

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        print(f"✅ Webhook set to: {webhook_url}")
    else:
        await bot.delete_webhook()
        print("✅ Webhook deleted - using polling")
    
    # Add yourself as admin and user if not exists
    my_tg_id = int(MY_TG_ID)
    if not await db.is_admin(my_tg_id):
        try:
            my_chat = await bot.get_chat(my_tg_id)
            username = my_chat.username or "Владелец"
            if await db.add_admin(my_tg_id, username):
                print("✅ Owner added as admin and user")
            else:
                print("❌ Failed to add owner as admin")
        except Exception as e:
            print(f"Error adding owner: {e}")
    
    # Start background task to keep Render awake
    if WEBHOOK_URL:
        threading.Thread(target=keep_awake, daemon=True).start()
        print("✅ Background keep-awake task started")
    
    print("✅ Bot started successfully")
    yield
    
    # Shutdown
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

def keep_awake():
    """Ping the app every 10 minutes to keep Render awake"""
    while True:
        try:
            if WEBHOOK_URL:
                response = requests.get(WEBHOOK_URL)
                print(f"🔄 Keep-alive ping: {response.status_code}")
            time.sleep(600)  # 10 minutes
        except Exception as e:
            print(f"❌ Keep-alive error: {e}")
            time.sleep(60)

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    try:
        update = await request.json()
        # Правильный способ обработки вебхука в aiogram 3.x
        await dp.feed_webhook_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"error": str(e)}, 400

@app.get("/")
async def root():
    return {
        "status": "Dice Alliance Bot is running!", 
        "ping": "pong",
        "webhook_url": f"{WEBHOOK_URL}{WEBHOOK_PATH}" if WEBHOOK_URL else "No webhook"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/set_webhook")
async def set_webhook():
    """Ручная установка вебхука"""
    if WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        result = await bot.set_webhook(webhook_url)
        return {"status": "webhook_set", "url": webhook_url, "result": result}
    return {"status": "no_webhook_url"}

@app.get("/delete_webhook")
async def delete_webhook():
    """Удаление вебхука"""
    result = await bot.delete_webhook()
    return {"status": "webhook_deleted", "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)