from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strategy import analyze, symbols
from datetime import datetime, timezone
import asyncio

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
origins = [
    "http://localhost:5173",
    "https://topaz-pwa.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# GLOBAL STATE
# -----------------------------
bot_running = False
signals_store = []   # 🔥 stores latest signals

# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def home():
    return {"message": "Trading Signal server running"}


@app.get("/signals")
def get_signals():
    return signals_store   # return stored signals


@app.post("/start")
def start_bot():
    global bot_running
    bot_running = True
    return {"message": "Bot started"}


@app.post("/stop")
def stop_bot():
    global bot_running
    bot_running = False
    return {"message": "Bot stopped"}


@app.get("/status")
def bot_status():
    return {"status": "running" if bot_running else "stopped"}


# -----------------------------
# TRADING SESSION CHECK
# -----------------------------
def in_trading_session():
    now = datetime.now(timezone.utc).hour

    return (7 <= now <= 16) or (12 <= now <= 21)


# -----------------------------
# BOT LOOP (BACKGROUND)
# -----------------------------
async def bot_loop():
    global bot_running, signals_store

    while True:
        if bot_running and in_trading_session():

            new_signals = []

            for pair, yf_symbol in symbols.items():
                result = analyze(pair, yf_symbol)
                new_signals.append(result)

            signals_store = new_signals  # 🔥 overwrite with latest batch
            print("✅ Signals updated")

        else:
            print("⏰ Waiting or stopped...")

        await asyncio.sleep(300)  # every 1 minute


# -----------------------------
# START BACKGROUND TASK
# -----------------------------
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(bot_loop())