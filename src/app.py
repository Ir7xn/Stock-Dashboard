from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from typing import List, Dict
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

# 1) /companies
@app.get("/companies")
def get_companies():
    return ["RELIANCE"]

# 2) /data/{symbol}
@app.get("/data/{symbol}")
def get_data(symbol: str):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT date, open, high, low, close, volume
            FROM prices
            WHERE symbol = :s
            ORDER BY date DESC
            LIMIT 30
        """), {"s": symbol}).fetchall()
    return [dict(r._mapping) for r in rows]

# 3) /summary/{symbol}
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
            WHERE symbol = :s
            AND close IS NOT NULL
            ORDER BY date DESC
            LIMIT 30
        """), {"s": symbol}).fetchall()

    closes = [float(r[0]) for r in rows]  # make sure they are floats

    if len(closes) < 2:
        return {"error": "Not enough data to predict"}

    closes = closes[::-1]    # oldest → newest

    X = np.arange(len(closes)).reshape(-1,1)
    y = np.array(closes)

    model = LinearRegression()
    model.fit(X, y)

    next_price = model.predict([[len(closes)]])[0]

    return {"predicted_next_close": round(float(next_price), 2)}