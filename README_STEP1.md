# Stock Data Intelligence Dashboard — Step 1 (Data Collection)

This step fetches NSE stock data from **yfinance**, cleans it, adds metrics, and stores everything in **SQLite**.

### Setup
```bash
cd stock-dashboard
pip install -r requirements.txt
```

### Run (default symbols list in `src/config.py`)
```bash
python -m src.data_prep --days 450
```

### Run (custom symbols)
```bash
python -m src.data_prep --symbols INFY.NS TCS.NS RELIANCE.NS --days 420
```

### What gets saved
- SQLite DB: `data/stocks.db`
- Table: `prices` with columns:
  - date, symbol, open, high, low, close, volume
  - daily_return, ma_7, rolling_252_high, rolling_252_low
  - volatility_20d_ann (custom metric)
