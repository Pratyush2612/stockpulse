# 📈 StockPulse — Global Stock Analysis Dashboard

A professional, real-time stock analysis dashboard for 200+ global companies.
Built with Streamlit, Plotly, and Yahoo Finance.

---

## 🚀 Features

- **Live Data** — Real-time prices & historical data via Yahoo Finance (free, no API key)
- **200+ Stocks** — Top global companies across 7 sectors
- **8 Analysis Tabs**: Price & Indicators, Candlestick, Volume & MACD, RSI & Oscillators, Returns Analysis, Fundamentals, Stock Comparison, News
- **Technical Indicators**: SMA, EMA, Bollinger Bands, RSI, MACD, ATR, OBV, VWAP, ROC
- **Fundamental Data**: P/E, EV/EBITDA, Revenue, Net Income, Analyst Recommendations
- **Multi-Stock Comparison**: Normalized performance, correlation heatmap, volatility comparison

---

## 🛠️ Local Setup (Run on your machine)

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone / download the project files
mkdir stockpulse && cd stockpulse
# Copy app.py and requirements.txt here

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run app.py
```

The app opens at: **http://localhost:8501**

---

## 🌐 Deploy for FREE — Public Access

### Option 1: Streamlit Community Cloud (Recommended — Easiest)

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "StockPulse dashboard"
   git remote add origin https://github.com/YOUR_USERNAME/stockpulse.git
   git push -u origin main
   ```

2. Go to **https://share.streamlit.io**
3. Sign in with GitHub
4. Click **New App** → Select your repo → branch: `main` → file: `app.py`
5. Click **Deploy**

✅ Your app will be live at: `https://YOUR_USERNAME-stockpulse.streamlit.app`
✅ Free, public URL, auto-restarts, no server needed

---

### Option 2: Railway.app (Always-On Free Tier)

1. Create `Procfile` in your project:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Go to **https://railway.app** → New Project → Deploy from GitHub
3. Connect your repo → it auto-detects Python
4. Add environment variable: `PORT = 8501`
5. Deploy → Get your public URL

---

### Option 3: Render.com (Free Web Service)

1. Go to **https://render.com** → New → Web Service
2. Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`
5. Deploy

---

### Option 4: Google Cloud Run (Scalable)

```bash
# Build Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT/stockpulse

# Deploy
gcloud run deploy stockpulse \
  --image gcr.io/YOUR_PROJECT/stockpulse \
  --platform managed \
  --allow-unauthenticated \
  --port 8501
```

Use this `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

---

## 📊 Data Source

All data is fetched **live** from Yahoo Finance via the `yfinance` library.
- Stock prices: Real-time (15-min delay for free tier)
- Financial statements: Quarterly/Annual
- News: Latest articles

**No API key required!**

---

## 🔧 Customization

### Add more stocks
Edit the `TOP_200` dictionary in `app.py`:
```python
TOP_200 = {
    "Company Name": "TICKER",
    ...
}
```

### Change cache duration
```python
@st.cache_data(ttl=300)  # 300 seconds = 5 minutes
```

---

## ⚠️ Disclaimer

This dashboard is for **educational purposes only**. Not financial advice.
Always do your own research before investing.
