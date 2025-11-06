import pandas as pd, numpy as np, os
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
folder = os.path.join(ROOT, "data")

def gen(symbol, base_price):
    days = 200
    end = datetime(2025, 11, 6)
    dates = [end - timedelta(days=i) for i in range(days)]
    dates = sorted(dates)

    np.random.seed(abs(hash(symbol)) % 2**32)
    price = base_price + np.cumsum(np.random.normal(0, base_price*0.002, days))
    openp = price + np.random.normal(0, base_price*0.001, days)
    high  = price + np.abs(np.random.normal(0, base_price*0.003, days))
    low   = price - np.abs(np.random.normal(0, base_price*0.003, days))
    vol   = np.random.randint(800000,3000000,days)

    df = pd.DataFrame({
        "date":[d.strftime("%Y-%m-%d") for d in dates],
        "open":openp,
        "high":high,
        "low":low,
        "close":price,
        "volume":vol
    })
    df.to_csv(os.path.join(folder, f"{symbol}_mock.csv"), index=False)
    print(symbol, "done")


gen("TCS", 3500)
gen("HDFC", 1600)
gen("SBIN", 700)
