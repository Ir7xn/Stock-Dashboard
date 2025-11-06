"""
Data Collection & Preparation (Part 1)
- Fetches stock data from yfinance
- Cleans and adds metrics:
  * daily_return = (Close - Open) / Open
  * ma_7 = 7-day moving average of Close
  * rolling_252_high / rolling_252_low = approx 52-week high/low on rolling window
  * volatility_20d_ann = annualized volatility using 20-day rolling std of daily_return
- Stores into SQLite (data/stocks.db), table name: "prices"
"""
from __future__ import annotations
import argparse
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DB_PATH = os.path.join(ROOT, "data", "stocks.db")
ENGINE = create_engine(f"sqlite:///{DB_PATH}", future=True)

def fetch_history(symbol: str, start: str = None, end: str = None):
    from config import USE_CSV, CSV_FILES
    if USE_CSV:
        file = CSV_FILES[symbol]
        df = pd.read_csv(os.path.join(ROOT, file))
        df["symbol"] = symbol
        df["date"] = pd.to_datetime(df["date"])
        return df



def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values(["symbol", "date"]).copy()
    # Daily return
    df["daily_return"] = (df["close"] - df["open"]) / df["open"]
    # 7-day MA
    df["ma_7"] = df.groupby("symbol")["close"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    # 52-week high/low (approx 252 trading days)
    window = 252
    df["rolling_252_high"] = df.groupby("symbol")["close"].transform(lambda s: s.rolling(window, min_periods=1).max())
    df["rolling_252_low"]  = df.groupby("symbol")["close"].transform(lambda s: s.rolling(window, min_periods=1).min())
    # Volatility score (custom metric): annualized 20-day volatility of daily returns
    vol_window = 20
    df["volatility_20d_ann"] = df.groupby("symbol")["daily_return"].transform(lambda s: s.rolling(vol_window, min_periods=2).std() * np.sqrt(252))
    return df

def ensure_schema():
    with ENGINE.begin() as conn:
        conn.execute(text("""        CREATE TABLE IF NOT EXISTS prices (
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            daily_return REAL,
            ma_7 REAL,
            rolling_252_high REAL,
            rolling_252_low REAL,
            volatility_20d_ann REAL,
            PRIMARY KEY (date, symbol)
        );
        """))

def upsert_prices(df: pd.DataFrame):
    # simple insert replace existing table
    ensure_schema()
    with ENGINE.begin() as conn:
        df.to_sql("prices", conn, if_exists="replace", index=False)
    print(f"Inserted {len(df)} rows.")


def fetch_and_store(symbols: list[str], days: int = 450):
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    frames = []
    for sym in symbols:
        print(f"Downloading {sym} from {start} to {end}...")
        hist = fetch_history(sym, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        if hist.empty:
            print(f"Warning: no data for {sym}")
            continue
        frames.append(hist)
    if not frames:
        print("No data downloaded.")
        return
    df = pd.concat(frames, ignore_index=True)
    df = add_metrics(df)
    upsert_prices(df)
    print(f"Stored {len(df)} rows into {DB_PATH}")

def preview_last_rows(limit: int = 5):
    with ENGINE.begin() as conn:
        res = conn.execute(text("SELECT * FROM prices ORDER BY date DESC, symbol LIMIT :lim"), {"lim": limit}).fetchall()
        for row in res:
            print(dict(row._mapping))

def main():
    parser = argparse.ArgumentParser(description="Fetch NSE stocks via yfinance and store with metrics into SQLite.")
    parser.add_argument("--symbols", nargs="*", default=None, help="Symbols like INFY.NS TCS.NS RELIANCE.NS ... If omitted uses defaults.")
    parser.add_argument("--days", type=int, default=450, help="How many calendar days back to fetch (default 450)." )
    args = parser.parse_args()

    # Lazy import to avoid circular import for DEFAULT_SYMBOLS
    from config import DEFAULT_SYMBOLS
    symbols = args.symbols if args.symbols else DEFAULT_SYMBOLS
    fetch_and_store(symbols, days=args.days)
    preview_last_rows()

if __name__ == "__main__":
    main()
