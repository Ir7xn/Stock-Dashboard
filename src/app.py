from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
import os
import numpy as np

from sklearn.linear_model import LinearRegression

app = FastAPI(title="Stock Data API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT, "data", "stocks.db")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

@app.get("/companies")
def get_companies():
    return ["RELIANCE", "TCS", "HDFC", "SBIN"]

@app.get("/data/{symbol}")
def get_data(symbol: str):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT date, open, high, low, close, volume
            FROM prices
            WHERE symbol = :s
            ORDER BY date DESC
            LIMIT 200
        """), {"s": symbol}).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/summary/{symbol}")
def summary(symbol: str):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT 
              MAX(close) AS high_52,
              MIN(close) AS low_52,
              AVG(close) AS avg_close
            FROM prices
            WHERE symbol = :s
        """), {"s": symbol}).fetchone()
    return dict(row._mapping)

@app.get("/predict/{symbol}")
def predict_next(symbol: str):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT close FROM prices
            WHERE symbol = :s AND close IS NOT NULL
            ORDER BY date DESC
            LIMIT 30
        """), {"s": symbol}).fetchall()

    closes = [float(r[0]) for r in rows]
    if len(closes) < 2: return {"error": "Not enough data"}

    closes = closes[::-1]
    X = np.arange(len(closes)).reshape(-1,1)
    y = np.array(closes)
    model = LinearRegression().fit(X, y)
    return {"predicted_next_close": round(float(model.predict([[len(closes)]])[0]), 2)}

# ---- VERY IMPORTANT ----
# mount static LAST not first
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
