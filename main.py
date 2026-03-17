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
    print("📡 Sending signals:", signals_store)
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
        if bot_running:

            print("🚀 Bot running...")

            new_signals = []

            for pair, yf_symbol in symbols.items():
                result = analyze(pair, yf_symbol)

                if result:  # ✅ prevent None
                    new_signals.append(result)

            if new_signals:  # ✅ only update if not empty
                signals_store = new_signals
                print("✅ Signals updated:", signals_store)
            else:
                print("⚠️ No signals generated")

        else:
            print("⏹️ Bot stopped")

        await asyncio.sleep(10)  # 🔥 reduce to 10s for testing


# -----------------------------
# START BACKGROUND TASK
# -----------------------------
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(bot_loop())