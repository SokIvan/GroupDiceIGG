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
        print(f"Webhook set to: {webhook_url}")
    else:
        await bot.delete_webhook()
        print("Webhook deleted - using polling")
    
    # Add yourself as admin and user if not exists
    my_tg_id = int(MY_TG_ID)
    if not await db.is_admin(my_tg_id):
        # Получаем информацию о себе из Telegram
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
    if WEBHOOK_URL:  # Only on Render
        threading.Thread(target=keep_awake, daemon=True).start()
        print("✅ Background keep-awake task started")
    
    print("✅ Bot started successfully")
    yield
    
    # Shutdown
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

def keep_awake():
    """Ping the app every 10 minutes to keep Render awake"""
    import requests
    while True:
        try:
            if WEBHOOK_URL:
                # Ping the root endpoint
                response = requests.get(WEBHOOK_URL.replace(WEBHOOK_PATH, ''))
                print(f"🔄 Keep-alive ping: {response.status_code}")
            time.sleep(600)  # 10 minutes
        except Exception as e:
            print(f"❌ Keep-alive error: {e}")
            time.sleep(60)  # Wait 1 minute on error

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    try:
        update = await request.json()
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {
        "status": "Dice Alliance Bot is running!", 
        "ping": "pong",
        "docs": "Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/test-db")
async def test_db():
    """Тестовый endpoint для проверки подключения к базе"""
    try:
        users = await db.get_all_users()
        admins = await db.is_admin(int(MY_TG_ID))
        return {
            "database": "connected",
            "total_users": len(users),
            "is_admin": admins
        }
    except Exception as e:
        return {"database": "error", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)