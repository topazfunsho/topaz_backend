from fastapi import FastAPI
from strategy import analyze, symbols
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173"
    "https://topaz-pwa.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    return {"message": "Trading Signal API Running"}

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