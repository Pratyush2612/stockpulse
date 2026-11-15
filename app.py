import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="StockPulse — Global Markets",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a24;
    --border: #2a2a3a;
    --accent: #00d4aa;
    --accent2: #7c3aed;
    --red: #ff4d6d;
    --green: #00d4aa;
    --text: #e8e8f0;
    --muted: #6b6b80;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

.main-header {
    background: linear-gradient(135deg, #0a0a0f 0%, #111130 50%, #0a0a0f 100%);
    border-bottom: 1px solid var(--border);
    padding: 2rem 0 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

.logo { font-size: 2.8rem; font-weight: 700; letter-spacing: -2px; }
.logo span { color: var(--accent); }
.tagline { color: var(--muted); font-size: 0.9rem; letter-spacing: 3px; text-transform: uppercase; }

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.metric-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
.metric-value { font-size: 1.8rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 0.2rem 0; }
.metric-change { font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; }
.up { color: var(--green); }
.down { color: var(--red); }

.section-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--muted);
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.info-item { background: var(--surface2); border-radius: 8px; padding: 0.7rem 1rem; }
.info-key { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; }
.info-val { font-size: 0.9rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }

.stock-pill {
    display: inline-block; background: var(--surface2); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.3rem 0.8rem; margin: 0.2rem;
    font-size: 0.75rem; cursor: pointer; transition: all 0.2s;
}
.stock-pill:hover { border-color: var(--accent); color: var(--accent); }

.stSelectbox > div > div { background: var(--surface) !important; border-color: var(--border) !important; }
.stSlider > div { color: var(--text) !important; }
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] p { color: var(--text) !important; }

.tab-header { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
TOP_200 = {
    "Apple Inc": "AAPL", "Microsoft Corp": "MSFT", "NVIDIA Corp": "NVDA",
    "Alphabet Inc (Google)": "GOOGL", "Amazon.com": "AMZN", "Meta Platforms": "META",
    "Berkshire Hathaway": "BRK-B", "Tesla Inc": "TSLA", "Broadcom Inc": "AVGO",
    "JPMorgan Chase": "JPM", "Eli Lilly": "LLY", "Visa Inc": "V",
    "UnitedHealth Group": "UNH", "Exxon Mobil": "XOM", "Johnson & Johnson": "JNJ",
    "Mastercard": "MA", "Procter & Gamble": "PG", "Home Depot": "HD",
    "Costco Wholesale": "COST", "Abbvie Inc": "ABBV", "Walmart": "WMT",
    "Chevron Corp": "CVX", "Oracle Corp": "ORCL", "Merck & Co": "MRK",
    "Bank of America": "BAC", "Netflix": "NFLX", "Salesforce": "CRM",
    "AMD": "AMD", "Cisco Systems": "CSCO", "ASML Holding": "ASML",
    "Novo Nordisk": "NVO", "Toyota Motor": "TM", "Samsung Electronics": "005930.KS",
    "Taiwan Semiconductor": "TSM", "LVMH": "MC.PA", "Nestlé": "NESN.SW",
    "Roche Holding": "ROG.SW", "Novartis": "NVS", "SAP SE": "SAP",
    "HSBC Holdings": "HSBC", "Shell plc": "SHEL", "Tencent Holdings": "0700.HK",
    "Alibaba Group": "BABA", "Reliance Industries": "RELIANCE.NS",
    "PepsiCo": "PEP", "Coca-Cola": "KO", "Intel Corp": "INTC",
    "IBM": "IBM", "Qualcomm": "QCOM", "Texas Instruments": "TXN",
    "Applied Materials": "AMAT", "Lam Research": "LRCX", "KLA Corp": "KLAC",
    "Micron Technology": "MU", "ServiceNow": "NOW", "Palo Alto Networks": "PANW",
    "Crowdstrike": "CRWD", "Snowflake": "SNOW", "Datadog": "DDOG",
    "MongoDB": "MDB", "Palantir Technologies": "PLTR", "Uber Technologies": "UBER",
    "Airbnb": "ABNB", "Block Inc": "SQ", "PayPal Holdings": "PYPL",
    "Shopify": "SHOP", "Spotify Technology": "SPOT", "Zoom Video": "ZM",
    "Workday": "WDAY", "HubSpot": "HUBS", "Twilio": "TWLO",
    "Unity Software": "U", "Roblox Corp": "RBLX", "Coinbase": "COIN",
    "Marathon Digital": "MARA", "MicroStrategy": "MSTR",
    "Goldman Sachs": "GS", "Morgan Stanley": "MS", "Wells Fargo": "WFC",
    "Citigroup": "C", "American Express": "AXP", "BlackRock": "BLK",
    "Charles Schwab": "SCHW", "CME Group": "CME",
    "Walt Disney": "DIS", "Comcast": "CMCSA", "Netflix": "NFLX",
    "Warner Bros Discovery": "WBD", "Paramount Global": "PARA",
    "Pfizer": "PFE", "Bristol-Myers Squibb": "BMY", "Gilead Sciences": "GILD",
    "Regeneron": "REGN", "Amgen": "AMGN", "Biogen": "BIIB",
    "Moderna": "MRNA", "Edwards Lifesciences": "EW", "Intuitive Surgical": "ISRG",
    "Medtronic": "MDT", "Stryker Corp": "SYK", "Boston Scientific": "BSX",
    "Abbott Laboratories": "ABT", "Thermo Fisher": "TMO", "Danaher": "DHR",
    "ExxonMobil": "XOM", "ConocoPhillips": "COP", "EOG Resources": "EOG",
    "Schlumberger": "SLB", "Marathon Petroleum": "MPC", "Valero Energy": "VLO",
    "NextEra Energy": "NEE", "Duke Energy": "DUK", "Southern Company": "SO",
    "American Tower": "AMT", "Crown Castle": "CCI", "Prologis": "PLD",
    "Simon Property": "SPG", "Equinix": "EQIX",
    "Caterpillar": "CAT", "Deere & Company": "DE", "Boeing": "BA",
    "Lockheed Martin": "LMT", "Raytheon Technologies": "RTX",
    "General Electric": "GE", "Honeywell": "HON", "3M Company": "MMM",
    "Emerson Electric": "EMR", "Parker Hannifin": "PH",
    "Amazon Web Services (Amazon)": "AMZN", "Alphabet Class C": "GOOG",
    "Arista Networks": "ANET", "Fortinet": "FTNT", "Zscaler": "ZS",
    "VeriSign": "VRSN", "Akamai Technologies": "AKAM",
    "Nike Inc": "NKE", "Starbucks": "SBUX", "McDonald's": "MCD",
    "Chipotle": "CMG", "Yum! Brands": "YUM", "Hilton Hotels": "HLT",
    "Marriott International": "MAR", "Booking Holdings": "BKNG", "Expedia": "EXPE",
    "Delta Air Lines": "DAL", "United Airlines": "UAL", "American Airlines": "AAL",
    "Southwest Airlines": "LUV", "FedEx": "FDX", "UPS": "UPS",
    "Union Pacific": "UNP", "CSX Corp": "CSX", "Norfolk Southern": "NSC",
    "Waste Management": "WM", "Republic Services": "RSG",
    "IQVIA Holdings": "IQV", "Verisk Analytics": "VRSK",
    "Moody's Corp": "MCO", "S&P Global": "SPGI", "FactSet Research": "FDS",
    "Fair Isaac (FICO)": "FICO", "Fiserv": "FI", "Fidelity National": "FIS",
    "Global Payments": "GPN", "Jack Henry": "JKHY",
    "Lowe's Companies": "LOW", "Best Buy": "BBY", "Target": "TGT",
    "Dollar General": "DG", "Dollar Tree": "DLTR", "TJX Companies": "TJX",
    "Ross Stores": "ROST", "Ulta Beauty": "ULTA", "O'Reilly Auto": "ORLY",
    "AutoZone": "AZO", "CarMax": "KMX",
    "Eaton Corp": "ETN", "Masco Corp": "MAS", "Trane Technologies": "TT",
    "Carrier Global": "CARR", "Otis Worldwide": "OTIS",
    "Colgate-Palmolive": "CL", "Kimberly-Clark": "KMB", "Church & Dwight": "CHD",
    "Estee Lauder": "EL", "Coty Inc": "COTY",
    "Constellation Brands": "STZ", "Brown-Forman": "BF-B",
    "Keurig Dr Pepper": "KDP", "Mondelez": "MDLZ", "General Mills": "GIS",
    "Hershey Company": "HSY", "Campbell Soup": "CPB",
}

SECTORS = {
    "Technology": ["AAPL","MSFT","NVDA","GOOGL","META","AVGO","AMD","CSCO","ORCL","IBM","QCOM","TXN","INTC","AMAT","LRCX","KLAC","MU","NOW","ANET"],
    "Finance": ["JPM","V","MA","BAC","GS","MS","WFC","C","AXP","BLK","SCHW","CME","SPGI","MCO","FDS","FICO","FI","FIS"],
    "Healthcare": ["LLY","UNH","JNJ","MRK","ABBV","PFE","BMY","GILD","REGN","AMGN","BIIB","MRNA","EW","ISRG","MDT","STK","BSX","ABT","TMO","DHR"],
    "Consumer": ["AMZN","TSLA","WMT","COST","HD","PG","PEP","KO","NKE","SBUX","MCD","CMG","DIS","LOW","TGT","TJX","ROST"],
    "Energy": ["XOM","CVX","COP","EOG","SLB","MPC","VLO"],
    "Industrial": ["CAT","DE","BA","LMT","RTX","GE","HON","MMM","EMR","PH","ETN","TT","CARR","OTIS","UNP","CSX","NSC","FDX","UPS","WM"],
}

PERIOD_MAP = {"1 Day":"1d","5 Days":"5d","1 Month":"1mo","3 Months":"3mo","6 Months":"6mo","1 Year":"1y","2 Years":"2y","5 Years":"5y","Max":"max"}
INTERVAL_MAP = {"1 Day":"5m","5 Days":"15m","1 Month":"1d","3 Months":"1d","6 Months":"1d","1 Year":"1wk","2 Years":"1wk","5 Years":"1mo","Max":"1mo"}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_info(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info
    except:
        return {}

@st.cache_data(ttl=600)
def fetch_financials(ticker):
    try:
        t = yf.Ticker(ticker)
        return {
            "income": t.income_stmt,
            "balance": t.balance_sheet,
            "cashflow": t.cashflow,
            "earnings": t.earnings_history,
            "recommendations": t.recommendations,
            "news": t.news[:8] if t.news else [],
        }
    except:
        return {}

def fmt(val, prefix="", suffix="", decimals=2):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    if abs(val) >= 1e12:
        return f"{prefix}{val/1e12:.{decimals}f}T{suffix}"
    if abs(val) >= 1e9:
        return f"{prefix}{val/1e9:.{decimals}f}B{suffix}"
    if abs(val) >= 1e6:
        return f"{prefix}{val/1e6:.{decimals}f}M{suffix}"
    return f"{prefix}{val:,.{decimals}f}{suffix}"

def safe(d, key, default="N/A"):
    v = d.get(key, default)
    return default if v is None else v

PLOT_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,17,24,0.8)",
    font=dict(color="#e8e8f0", family="Space Grotesk"),
    xaxis=dict(gridcolor="#2a2a3a", zeroline=False, showgrid=True),
    yaxis=dict(gridcolor="#2a2a3a", zeroline=False, showgrid=True),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2a2a3a"),
)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">⚡ Stock Selection</div>', unsafe_allow_html=True)
    company_name = st.selectbox("Select Company", list(TOP_200.keys()), index=0)
    ticker_sym = TOP_200[company_name]

    st.markdown('<div class="section-title">📅 Time Range</div>', unsafe_allow_html=True)
    period_label = st.select_slider("Period", list(PERIOD_MAP.keys()), value="1 Year")
    period = PERIOD_MAP[period_label]
    interval = INTERVAL_MAP[period_label]

    st.markdown('<div class="section-title">🔧 Indicators</div>', unsafe_allow_html=True)
    show_sma20 = st.checkbox("SMA 20", True)
    show_sma50 = st.checkbox("SMA 50", True)
    show_sma200 = st.checkbox("SMA 200", False)
    show_ema12 = st.checkbox("EMA 12", False)
    show_ema26 = st.checkbox("EMA 26", False)
    show_bb = st.checkbox("Bollinger Bands", False)
    show_volume = st.checkbox("Volume", True)

    st.markdown('<div class="section-title">📊 Compare</div>', unsafe_allow_html=True)
    compare_stocks = st.multiselect(
        "Compare with (max 4)",
        [f"{n} ({s})" for n, s in TOP_200.items() if s != ticker_sym],
        max_selections=4,
        default=[]
    )

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="logo">Stock<span>Pulse</span></div>
    <div class="tagline">Global Markets Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# ─── FETCH DATA ───────────────────────────────────────────────────────────────
with st.spinner(f"Fetching live data for {ticker_sym}..."):
    df = fetch_data(ticker_sym, period, interval)
    info = fetch_info(ticker_sym)
    financials = fetch_financials(ticker_sym)

if df.empty:
    st.error(f"⚠️ Could not fetch data for {ticker_sym}. Try another stock or check your connection.")
    st.stop()

# ─── COMPUTE INDICATORS ───────────────────────────────────────────────────────
close = df["Close"].squeeze()
volume = df["Volume"].squeeze() if "Volume" in df.columns else pd.Series(dtype=float)
high = df["High"].squeeze()
low = df["Low"].squeeze()
open_ = df["Open"].squeeze()

df["SMA20"] = close.rolling(20).mean()
df["SMA50"] = close.rolling(50).mean()
df["SMA200"] = close.rolling(200).mean()
df["EMA12"] = close.ewm(span=12).mean()
df["EMA26"] = close.ewm(span=26).mean()
df["BB_mid"] = close.rolling(20).mean()
df["BB_std"] = close.rolling(20).std()
df["BB_upper"] = df["BB_mid"] + 2*df["BB_std"]
df["BB_lower"] = df["BB_mid"] - 2*df["BB_std"]

delta = close.diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = (-delta.clip(upper=0)).rolling(14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
df["MACD"] = ema12 - ema26
df["MACD_signal"] = df["MACD"].ewm(span=9).mean()
df["MACD_hist"] = df["MACD"] - df["MACD_signal"]

df["ROC"] = close.pct_change(periods=10) * 100
df["ATR"] = pd.concat([
    high - low,
    (high - close.shift()).abs(),
    (low - close.shift()).abs()
], axis=1).max(axis=1).rolling(14).mean()

if not volume.empty and volume.sum() > 0:
    df["OBV"] = (np.sign(delta) * volume).fillna(0).cumsum()
    df["VWAP"] = (close * volume).cumsum() / volume.cumsum()

current_price = float(close.iloc[-1])
prev_price = float(close.iloc[-2]) if len(close) > 1 else current_price
day_change = current_price - prev_price
day_pct = (day_change / prev_price) * 100
first_price = float(close.iloc[0])
period_change = current_price - first_price
period_pct = (period_change / first_price) * 100

# ─── TOP METRICS ──────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, "Current Price", f"${current_price:,.2f}", day_change, day_pct, "Day"),
    (c2, "Market Cap", fmt(safe(info,"marketCap",0), "$"), period_change, period_pct, period_label),
    (c3, "52W High", f"${safe(info,'fiftyTwoWeekHigh','N/A'):,.2f}" if isinstance(safe(info,'fiftyTwoWeekHigh'), float) else "N/A", None, None, None),
    (c4, "52W Low", f"${safe(info,'fiftyTwoWeekLow','N/A'):,.2f}" if isinstance(safe(info,'fiftyTwoWeekLow'), float) else "N/A", None, None, None),
    (c5, "Volume", fmt(safe(info,"volume",0)), None, None, None),
]

for col, label, val, chg, pct, lbl in metrics:
    with col:
        change_html = ""
        if chg is not None:
            cls = "up" if chg >= 0 else "down"
            arrow = "▲" if chg >= 0 else "▼"
            change_html = f'<div class="metric-change {cls}">{arrow} {abs(pct):.2f}% ({lbl})</div>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            {change_html}
        </div>""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📈 Price & Indicators", "🕯️ Candlestick", "📊 Volume & MACD", "🔬 RSI & Oscillators", "💹 Returns Analysis", "🏢 Fundamentals", "⚖️ Compare Stocks", "📰 News & Sentiment"])

# ══════════════════════════════════════════════════════
# TAB 1: Price Chart + Indicators
# ══════════════════════════════════════════════════════
with tabs[0]:
    rows = 2 if show_volume else 1
    row_h = [0.75, 0.25] if show_volume else [1]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=row_h)

    fig.add_trace(go.Scatter(x=df.index, y=close, name="Price", line=dict(color="#00d4aa", width=2), fill="tozeroy", fillcolor="rgba(0,212,170,0.05)"), row=1, col=1)

    if show_bb:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="BB Upper", line=dict(color="#7c3aed", width=1, dash="dash")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="BB Lower", line=dict(color="#7c3aed", width=1, dash="dash"), fill="tonexty", fillcolor="rgba(124,58,237,0.05)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_mid"], name="BB Mid", line=dict(color="#7c3aed", width=1)), row=1, col=1)

    colors_ind = {"SMA20":"#f59e0b","SMA50":"#3b82f6","SMA200":"#ef4444","EMA12":"#f97316","EMA26":"#ec4899"}
    for key, label, show in [("SMA20","SMA 20",show_sma20),("SMA50","SMA 50",show_sma50),("SMA200","SMA 200",show_sma200),("EMA12","EMA 12",show_ema12),("EMA26","EMA 26",show_ema26)]:
        if show:
            fig.add_trace(go.Scatter(x=df.index, y=df[key], name=label, line=dict(color=colors_ind[key], width=1.5, dash="dot")), row=1, col=1)

    if show_volume and not volume.empty:
        clrs = ["#00d4aa" if c >= o else "#ff4d6d" for c, o in zip(close, open_)]
        fig.add_trace(go.Bar(x=df.index, y=volume, name="Volume", marker_color=clrs, opacity=0.7), row=2, col=1)

    fig.update_layout(**PLOT_THEME, height=600, title=dict(text=f"{company_name} ({ticker_sym}) — {period_label}", font=dict(size=16, color="#e8e8f0")))
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 2: Candlestick
# ══════════════════════════════════════════════════════
with tabs[1]:
    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25])
    fig2.add_trace(go.Candlestick(
        x=df.index, open=open_, high=high, low=low, close=close,
        name="OHLC",
        increasing=dict(line=dict(color="#00d4aa"), fillcolor="rgba(0,212,170,0.3)"),
        decreasing=dict(line=dict(color="#ff4d6d"), fillcolor="rgba(255,77,109,0.3)"),
    ), row=1, col=1)
    if show_sma50:
        fig2.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA 50", line=dict(color="#3b82f6", width=1.5)), row=1, col=1)
    if show_sma200:
        fig2.add_trace(go.Scatter(x=df.index, y=df["SMA200"], name="SMA 200", line=dict(color="#ef4444", width=1.5)), row=1, col=1)

    if not volume.empty:
        clrs = ["#00d4aa" if c >= o else "#ff4d6d" for c, o in zip(close, open_)]
        fig2.add_trace(go.Bar(x=df.index, y=volume, name="Volume", marker_color=clrs, opacity=0.6), row=2, col=1)

    fig2.update_layout(**PLOT_THEME, height=650, xaxis_rangeslider_visible=False, title=dict(text=f"Candlestick Chart — {ticker_sym}", font=dict(size=16, color="#e8e8f0")))
    st.plotly_chart(fig2, use_container_width=True)

    # OHLCV table
    st.markdown('<div class="section-title">Recent OHLCV Data</div>', unsafe_allow_html=True)
    recent = df[["Open","High","Low","Close","Volume"]].tail(20).iloc[::-1].copy()
    recent.index = recent.index.strftime("%Y-%m-%d %H:%M") if hasattr(recent.index, 'strftime') else recent.index
    st.dataframe(recent.style.format({"Open":"${:.2f}","High":"${:.2f}","Low":"${:.2f}","Close":"${:.2f}","Volume":"{:,.0f}"}), use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 3: Volume & MACD
# ══════════════════════════════════════════════════════
with tabs[2]:
    fig3 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.4, 0.3, 0.3],
                         subplot_titles=["Volume Analysis", "MACD", "ATR (Volatility)"])

    if not volume.empty:
        vol_ma = volume.rolling(20).mean()
        clrs = ["#00d4aa" if c >= o else "#ff4d6d" for c, o in zip(close, open_)]
        fig3.add_trace(go.Bar(x=df.index, y=volume, name="Volume", marker_color=clrs, opacity=0.7), row=1, col=1)
        fig3.add_trace(go.Scatter(x=df.index, y=vol_ma, name="Vol MA20", line=dict(color="#f59e0b", width=2)), row=1, col=1)

    fig3.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="#00d4aa", width=2)), row=2, col=1)
    fig3.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal", line=dict(color="#f59e0b", width=2)), row=2, col=1)
    hist_colors = ["#00d4aa" if v >= 0 else "#ff4d6d" for v in df["MACD_hist"].fillna(0)]
    fig3.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], name="Histogram", marker_color=hist_colors, opacity=0.7), row=2, col=1)

    fig3.add_trace(go.Scatter(x=df.index, y=df["ATR"], name="ATR", line=dict(color="#7c3aed", width=2), fill="tozeroy", fillcolor="rgba(124,58,237,0.1)"), row=3, col=1)

    fig3.update_layout(**PLOT_THEME, height=750, showlegend=True)
    st.plotly_chart(fig3, use_container_width=True)

    if not volume.empty and "OBV" in df.columns:
        fig_obv = go.Figure()
        fig_obv.add_trace(go.Scatter(x=df.index, y=df["OBV"], name="OBV", line=dict(color="#00d4aa", width=2), fill="tozeroy", fillcolor="rgba(0,212,170,0.05)"))
        fig_obv.update_layout(**PLOT_THEME, height=300, title="On-Balance Volume (OBV)")
        st.plotly_chart(fig_obv, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 4: RSI & Oscillators
# ══════════════════════════════════════════════════════
with tabs[3]:
    fig4 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.4, 0.3, 0.3],
                         subplot_titles=["Price", "RSI (14)", "Rate of Change (10)"])

    fig4.add_trace(go.Scatter(x=df.index, y=close, name="Price", line=dict(color="#00d4aa", width=2)), row=1, col=1)

    fig4.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="#f59e0b", width=2)), row=2, col=1)
    fig4.add_hline(y=70, line_color="#ff4d6d", line_dash="dash", line_width=1, row=2, col=1)
    fig4.add_hline(y=30, line_color="#00d4aa", line_dash="dash", line_width=1, row=2, col=1)
    fig4.add_hrect(y0=70, y1=100, fillcolor="rgba(255,77,109,0.05)", row=2, col=1)
    fig4.add_hrect(y0=0, y1=30, fillcolor="rgba(0,212,170,0.05)", row=2, col=1)

    roc_colors = ["#00d4aa" if v >= 0 else "#ff4d6d" for v in df["ROC"].fillna(0)]
    fig4.add_trace(go.Bar(x=df.index, y=df["ROC"], name="ROC", marker_color=roc_colors, opacity=0.8), row=3, col=1)
    fig4.add_hline(y=0, line_color="#6b6b80", line_width=1, row=3, col=1)

    fig4.update_layout(**PLOT_THEME, height=750)
    st.plotly_chart(fig4, use_container_width=True)

    # RSI Stats
    rsi_current = float(df["RSI"].dropna().iloc[-1]) if not df["RSI"].dropna().empty else 0
    col1, col2, col3 = st.columns(3)
    with col1:
        signal = "🔴 Overbought" if rsi_current > 70 else "🟢 Oversold" if rsi_current < 30 else "🟡 Neutral"
        st.metric("Current RSI", f"{rsi_current:.2f}", signal)
    with col2:
        st.metric("RSI (Avg 30d)", f"{df['RSI'].tail(30).mean():.2f}")
    with col3:
        st.metric("Price Volatility (ATR)", f"{float(df['ATR'].dropna().iloc[-1]):.2f}" if not df["ATR"].dropna().empty else "N/A")

# ══════════════════════════════════════════════════════
# TAB 5: Returns Analysis
# ══════════════════════════════════════════════════════
with tabs[4]:
    returns = close.pct_change().dropna()
    cum_returns = (1 + returns).cumprod() - 1

    col1, col2 = st.columns(2)

    with col1:
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(x=cum_returns.index, y=cum_returns * 100, name="Cumulative Return",
                                     line=dict(color="#00d4aa", width=2.5), fill="tozeroy",
                                     fillcolor="rgba(0,212,170,0.07)"))
        fig_cum.add_hline(y=0, line_color="#6b6b80", line_width=1)
        fig_cum.update_layout(**PLOT_THEME, height=350, title="Cumulative Returns (%)")
        st.plotly_chart(fig_cum, use_container_width=True)

    with col2:
        fig_ret = go.Figure()
        colors_ret = ["#00d4aa" if v >= 0 else "#ff4d6d" for v in returns]
        fig_ret.add_trace(go.Bar(x=returns.index, y=returns * 100, name="Daily Returns", marker_color=colors_ret, opacity=0.8))
        fig_ret.update_layout(**PLOT_THEME, height=350, title="Daily Returns (%)")
        st.plotly_chart(fig_ret, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=returns * 100, nbinsx=60, name="Return Distribution",
                                         marker_color="#7c3aed", opacity=0.8, marker_line=dict(color="#2a2a3a", width=0.5)))
        fig_hist.add_vline(x=float(returns.mean()*100), line_color="#00d4aa", line_dash="dash", annotation_text="Mean")
        fig_hist.update_layout(**PLOT_THEME, height=350, title="Return Distribution", xaxis_title="Return (%)", yaxis_title="Frequency")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col4:
        # Rolling volatility
        rolling_vol = returns.rolling(21).std() * np.sqrt(252) * 100
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol, name="Ann. Volatility",
                                      line=dict(color="#f59e0b", width=2), fill="tozeroy", fillcolor="rgba(245,158,11,0.08)"))
        fig_vol.update_layout(**PLOT_THEME, height=350, title="Rolling 21-Day Annualized Volatility (%)")
        st.plotly_chart(fig_vol, use_container_width=True)

    # Stats table
    st.markdown('<div class="section-title">📐 Statistical Summary</div>', unsafe_allow_html=True)
    ann_ret = float(returns.mean()) * 252 * 100
    ann_vol = float(returns.std()) * np.sqrt(252) * 100
    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0
    max_dd = float(((cum_returns + 1) / (cum_returns + 1).cummax() - 1).min()) * 100
    skew = float(returns.skew())
    kurt = float(returns.kurtosis())

    stats = {
        "Annualized Return": f"{ann_ret:.2f}%",
        "Annualized Volatility": f"{ann_vol:.2f}%",
        "Sharpe Ratio (approx)": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_dd:.2f}%",
        "Skewness": f"{skew:.3f}",
        "Kurtosis": f"{kurt:.3f}",
        "Best Day": f"{float(returns.max())*100:.2f}%",
        "Worst Day": f"{float(returns.min())*100:.2f}%",
        "Total Trading Days": str(len(returns)),
        "Positive Days": f"{(returns > 0).sum()} ({(returns>0).mean()*100:.1f}%)",
    }

    scols = st.columns(5)
    for i, (k, v) in enumerate(stats.items()):
        with scols[i % 5]:
            st.markdown(f'<div class="info-item"><div class="info-key">{k}</div><div class="info-val">{v}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 6: Fundamentals
# ══════════════════════════════════════════════════════
with tabs[5]:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="section-title">🏢 Company Overview</div>', unsafe_allow_html=True)
        overview = {
            "Symbol": safe(info, "symbol"),
            "Sector": safe(info, "sector"),
            "Industry": safe(info, "industry"),
            "Country": safe(info, "country"),
            "Employees": f"{safe(info,'fullTimeEmployees',0):,}" if isinstance(safe(info,'fullTimeEmployees'), int) else "N/A",
            "Exchange": safe(info, "exchange"),
            "Currency": safe(info, "currency"),
            "IPO Year": safe(info, "firstTradeDateEpochUtc", "N/A"),
        }
        for k, v in overview.items():
            st.markdown(f'<div class="info-item" style="margin-bottom:0.4rem"><div class="info-key">{k}</div><div class="info-val">{v}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">📋 About</div>', unsafe_allow_html=True)
        bio = safe(info, "longBusinessSummary", "No description available.")
        if bio != "N/A":
            st.markdown(f'<div style="font-size:0.82rem;color:#9999aa;line-height:1.6">{bio[:500]}...</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">💰 Valuation Metrics</div>', unsafe_allow_html=True)
        val_metrics = {
            "Market Cap": fmt(safe(info,"marketCap",0), "$"),
            "Enterprise Value": fmt(safe(info,"enterpriseValue",0), "$"),
            "P/E Ratio (TTM)": f"{safe(info,'trailingPE','N/A'):.2f}" if isinstance(safe(info,'trailingPE'), float) else "N/A",
            "Forward P/E": f"{safe(info,'forwardPE','N/A'):.2f}" if isinstance(safe(info,'forwardPE'), float) else "N/A",
            "PEG Ratio": f"{safe(info,'pegRatio','N/A'):.2f}" if isinstance(safe(info,'pegRatio'), float) else "N/A",
            "Price/Book": f"{safe(info,'priceToBook','N/A'):.2f}" if isinstance(safe(info,'priceToBook'), float) else "N/A",
            "EV/Revenue": f"{safe(info,'enterpriseToRevenue','N/A'):.2f}" if isinstance(safe(info,'enterpriseToRevenue'), float) else "N/A",
            "EV/EBITDA": f"{safe(info,'enterpriseToEbitda','N/A'):.2f}" if isinstance(safe(info,'enterpriseToEbitda'), float) else "N/A",
            "Revenue (TTM)": fmt(safe(info,"totalRevenue",0), "$"),
            "Gross Profit": fmt(safe(info,"grossProfits",0), "$"),
            "Net Income": fmt(safe(info,"netIncomeToCommon",0), "$"),
            "EPS (TTM)": f"${safe(info,'trailingEps','N/A'):.2f}" if isinstance(safe(info,'trailingEps'), float) else "N/A",
            "ROE": f"{safe(info,'returnOnEquity',0)*100:.1f}%" if isinstance(safe(info,'returnOnEquity'), float) else "N/A",
            "ROA": f"{safe(info,'returnOnAssets',0)*100:.1f}%" if isinstance(safe(info,'returnOnAssets'), float) else "N/A",
            "Profit Margin": f"{safe(info,'profitMargins',0)*100:.1f}%" if isinstance(safe(info,'profitMargins'), float) else "N/A",
            "Dividend Yield": f"{safe(info,'dividendYield',0)*100:.2f}%" if isinstance(safe(info,'dividendYield'), float) else "N/A",
            "Beta": f"{safe(info,'beta','N/A'):.2f}" if isinstance(safe(info,'beta'), float) else "N/A",
            "Short Ratio": f"{safe(info,'shortRatio','N/A'):.2f}" if isinstance(safe(info,'shortRatio'), float) else "N/A",
        }
        cols = st.columns(3)
        for i, (k, v) in enumerate(val_metrics.items()):
            with cols[i % 3]:
                st.markdown(f'<div class="info-item" style="margin-bottom:0.4rem"><div class="info-key">{k}</div><div class="info-val">{v}</div></div>', unsafe_allow_html=True)

    # Income Statement Chart
    if financials.get("income") is not None:
        inc = financials["income"]
        try:
            inc_t = inc.T if not inc.empty else None
            if inc_t is not None:
                st.markdown('<div class="section-title">📈 Revenue vs Net Income</div>', unsafe_allow_html=True)
                rev_row = [c for c in inc.index if "Total Revenue" in str(c) or "Revenue" in str(c)]
                net_row = [c for c in inc.index if "Net Income" in str(c)]
                if rev_row and net_row:
                    fig_inc = go.Figure()
                    years = [str(c)[:10] for c in inc.columns]
                    rev = [float(inc.loc[rev_row[0], c])/1e9 if pd.notna(inc.loc[rev_row[0], c]) else 0 for c in inc.columns]
                    net = [float(inc.loc[net_row[0], c])/1e9 if pd.notna(inc.loc[net_row[0], c]) else 0 for c in inc.columns]
                    fig_inc.add_trace(go.Bar(x=years, y=rev, name="Revenue (B)", marker_color="#00d4aa", opacity=0.85))
                    fig_inc.add_trace(go.Bar(x=years, y=net, name="Net Income (B)", marker_color="#7c3aed", opacity=0.85))
                    fig_inc.update_layout(**PLOT_THEME, height=350, barmode="group", yaxis_title="Billions USD")
                    st.plotly_chart(fig_inc, use_container_width=True)
        except Exception:
            pass

    # Analyst Recommendations
    recs = financials.get("recommendations")
    if recs is not None and not recs.empty:
        try:
            st.markdown('<div class="section-title">🎯 Analyst Recommendations</div>', unsafe_allow_html=True)
            st.dataframe(recs.head(10), use_container_width=True)
        except Exception:
            pass

# ══════════════════════════════════════════════════════
# TAB 7: Compare Stocks
# ══════════════════════════════════════════════════════
with tabs[6]:
    all_compare = [ticker_sym] + [s.split("(")[-1].rstrip(")") for s in compare_stocks]
    all_names = [company_name] + [s.split("(")[0].strip() for s in compare_stocks]

    compare_data = {}
    for sym in all_compare:
        d = fetch_data(sym, period, interval)
        if not d.empty:
            compare_data[sym] = d

    if len(compare_data) < 2:
        st.info("👆 Use the sidebar to select stocks to compare (max 4). The current stock is already included.")
    else:
        palette = ["#00d4aa","#f59e0b","#7c3aed","#ef4444","#3b82f6"]

        # Normalized Returns
        fig_comp = go.Figure()
        for i, (sym, d) in enumerate(compare_data.items()):
            c = d["Close"].squeeze()
            norm = (c / float(c.iloc[0])) * 100
            nm = all_names[list(compare_data.keys()).index(sym)] if sym in all_compare else sym
            fig_comp.add_trace(go.Scatter(x=d.index, y=norm, name=f"{sym} ({nm[:15]})", line=dict(color=palette[i], width=2.5)))
        fig_comp.add_hline(y=100, line_color="#6b6b80", line_dash="dash", line_width=1)
        fig_comp.update_layout(**PLOT_THEME, height=400, title="Normalized Price Performance (Base=100)", yaxis_title="Normalized Price")
        st.plotly_chart(fig_comp, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            # Correlation Heatmap
            price_df = pd.DataFrame({sym: d["Close"].squeeze() for sym, d in compare_data.items()}).ffill().dropna()
            corr = price_df.pct_change().dropna().corr()
            fig_corr = px.imshow(corr, color_continuous_scale=[[0,"#ff4d6d"],[0.5,"#1a1a24"],[1,"#00d4aa"]],
                                  text_auto=".2f", title="Return Correlation Heatmap", zmin=-1, zmax=1)
            fig_corr.update_layout(**PLOT_THEME, height=380)
            st.plotly_chart(fig_corr, use_container_width=True)

        with col2:
            # Volatility comparison
            vols = {}
            for sym, d in compare_data.items():
                r = d["Close"].squeeze().pct_change().dropna()
                vols[sym] = float(r.std()) * np.sqrt(252) * 100
            fig_bar = go.Figure(go.Bar(
                x=list(vols.keys()), y=list(vols.values()),
                marker_color=palette[:len(vols)], opacity=0.85,
                text=[f"{v:.1f}%" for v in vols.values()], textposition="outside"
            ))
            fig_bar.update_layout(**PLOT_THEME, height=380, title="Annualized Volatility (%)", yaxis_title="%")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Returns comparison table
        st.markdown('<div class="section-title">📊 Performance Summary</div>', unsafe_allow_html=True)
        summary = []
        for sym, d in compare_data.items():
            c = d["Close"].squeeze()
            r = c.pct_change().dropna()
            ret = (float(c.iloc[-1]) - float(c.iloc[0])) / float(c.iloc[0]) * 100
            ann_ret = float(r.mean()) * 252 * 100
            vol = float(r.std()) * np.sqrt(252) * 100
            sharpe = ann_ret / vol if vol else 0
            summary.append({"Symbol": sym, "Current Price": f"${float(c.iloc[-1]):.2f}", "Period Return": f"{ret:.1f}%",
                             "Ann. Return": f"{ann_ret:.1f}%", "Ann. Volatility": f"{vol:.1f}%", "Sharpe": f"{sharpe:.2f}"})
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

        # Volume comparison
        fig_vol_comp = go.Figure()
        for i, (sym, d) in enumerate(compare_data.items()):
            if "Volume" in d.columns:
                v = d["Volume"].squeeze()
                fig_vol_comp.add_trace(go.Scatter(x=d.index, y=v, name=sym, line=dict(color=palette[i], width=1.5), opacity=0.8))
        if fig_vol_comp.data:
            fig_vol_comp.update_layout(**PLOT_THEME, height=300, title="Volume Comparison")
            st.plotly_chart(fig_vol_comp, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 8: News
# ══════════════════════════════════════════════════════
with tabs[7]:
    news = financials.get("news", [])
    if news:
        st.markdown(f'<div class="section-title">📰 Latest News — {company_name}</div>', unsafe_allow_html=True)
        for item in news:
            try:
                title = item.get("title", "No title")
                link = item.get("link", "#")
                pub = item.get("publisher", "")
                st.markdown(f"""
                <div class="info-item" style="margin-bottom:0.8rem;padding:1rem 1.2rem;border-left:3px solid #00d4aa">
                    <div style="font-size:0.75rem;color:#6b6b80;margin-bottom:0.3rem">{pub}</div>
                    <a href="{link}" target="_blank" style="color:#e8e8f0;text-decoration:none;font-weight:600;font-size:0.95rem">{title}</a>
                </div>""", unsafe_allow_html=True)
            except Exception:
                continue
    else:
        st.info("No recent news available for this stock.")

    # Sector Pie
    st.markdown('<div class="section-title">🗂️ Sector Breakdown (Tracked Stocks)</div>', unsafe_allow_html=True)
    sector_counts = {s: len(t) for s, t in SECTORS.items()}
    fig_pie = go.Figure(go.Pie(
        labels=list(sector_counts.keys()), values=list(sector_counts.values()),
        hole=0.5, marker=dict(colors=["#00d4aa","#7c3aed","#f59e0b","#ef4444","#3b82f6","#ec4899","#10b981"]),
        textinfo="label+percent"
    ))
    fig_pie.update_layout(**PLOT_THEME, height=400, title="Stock Coverage by Sector", showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding:1rem;border-top:1px solid #2a2a3a;color:#6b6b80;font-size:0.75rem">
    StockPulse — Live data via Yahoo Finance · Built with Streamlit & Plotly · Not financial advice
</div>
""", unsafe_allow_html=True)
