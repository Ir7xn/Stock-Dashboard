# 📈 Stock Price Dashboard (FastAPI + JS + Chart.js)

This project is a mini end-to-end Stock Analytics dashboard built using **FastAPI (Backend)** and **HTML + JS + Chart.js (Frontend)**.

It fetches recent stock prices from the stored SQLite DB, visualizes them, and also predicts the next day close using **Linear Regression**.

---

## 🔗 Live Deployment (Render)

**Live URL:** https://stock-dashboard-snn1.onrender.com

---

## ✅ Features

| Feature | Status |
|--------|--------|
| View stock closing price chart | ✅ |
| 30 days / 90 days filter | ✅ |
| Predict next closing price | ✅ |
| 52-week summary (high / low / avg) | ✅ |
| Fully deployed on Render | ✅ |

---

## 📦 Tech Stack

| Layer | Tools Used |
|-------|------------|
| Backend | FastAPI, Uvicorn, SQLAlchemy |
| DB | SQLite |
| ML Model | scikit-learn (Linear Regression) |
| Frontend | HTML, CSS, JS, Chart.js |
| Deployment | Render |

---

## 📁 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/companies` | GET | Returns list of companies |
| `/data/{symbol}` | GET | Returns latest 200 rows for a company |
| `/summary/{symbol}` | GET | 52-week high, low, avg |
| `/predict/{symbol}` | GET | Predict next close price |

---
