from fastapi import FastAPI
from strategy import analyze, symbols
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime, timezone

app = FastAPI()

origins = [
    "http://localhost:5173"
    "https://topaz-pwa.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_running = False


@app.post("/stop")
def stop_bot():
    global bot_running
    bot_running = False
    return {"message": "Bot stopped", "status": "program stopped"}


@app.get("/status")
def bot_status():
    if stop_bot():
        return {"status": "program not running"}
    else:
        return {"status": "program running"}

@app.get("/")
def home():
    return {"message": "Trading Signal server Running"}

@app.get("/signals")
def all_signals():
    
    return [
        {
            "price": "1234.433",
            "pair": "EURUSD",
            "signal": "CALL",
            "strength": "Medium"
        },
        {
            "price": "14534.433",
            "pair": "GBPUSD",
            "signal": "PUT",
            "strength": "Medium"
        }
    ]

    # results = []

    # for pair, yf_symbol in symbols.items():
    #     results.append(analyze(pair, yf_symbol))

    # return results


@app.get("/signal/{pair}")
def single_signal(pair: str):

    pair = pair.upper()

    if pair not in symbols:
        return {"error": "Pair not supported"}

    return analyze(pair, symbols[pair])

def in_trading_session():
    now = datetime.now(timezone.utc).hour

    london_open = 7
    london_close = 16
    ny_open = 12
    ny_close = 21

    if (london_open <= now <= london_close) or (ny_open <= now <= ny_close):
        return True
    return False

while True:

    if bot_running:
        if in_trading_session():
            for pair, yf_symbol in symbols.items():
                analyze(pair, yf_symbol)
        else:
            print("⏰ Outside trading session. Bot waiting...")

    time.sleep(60)