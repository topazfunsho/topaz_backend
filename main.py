from fastapi import FastAPI
from strategy import analyze, symbols
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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