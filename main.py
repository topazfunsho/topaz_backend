from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strategy import analyze, symbols
from datetime import datetime, timezone
import asyncio

app = FastAPI()

# CORS
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

bot_running = False


@app.get("/")
def home():
    return {"message": "Trading Signal server running"}


@app.get("/signals")
def all_signals():
    results = []

    for pair, yf_symbol in symbols.items():
        results.append(analyze(pair, yf_symbol))

    return results


@app.get("/signal/{pair}")
def single_signal(pair: str):
    pair = pair.upper()

    if pair not in symbols:
        return {"error": "Pair not supported"}

    return analyze(pair, symbols[pair])


@app.post("/stop")
def stop_bot():
    global bot_running
    bot_running = False
    return {"message": "Bot stopped", "status": "program stopped"}


@app.post("/start")
def start_bot():
    global bot_running
    bot_running = True
    return {"message": "Bot started", "status": "program running"}


@app.get("/status")
def bot_status():
    return {"status": "running" if bot_running else "stopped"}


def in_trading_session():
    now = datetime.now(timezone.utc).hour

    london_open = 7
    london_close = 16
    ny_open = 12
    ny_close = 21

    return (london_open <= now <= london_close) or (ny_open <= now <= ny_close)


async def bot_loop():
    global bot_running

    while True:
        if bot_running:
            if in_trading_session():
                for pair, yf_symbol in symbols.items():
                    analyze(pair, yf_symbol)
            else:
                print("⏰ Outside trading session. Bot waiting...")

        await asyncio.sleep(60)


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(bot_loop())