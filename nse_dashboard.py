import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

st.set_page_config(
    page_title="NSE Live Dashboard · 1h HA",
    layout="wide",
    page_icon=""
)

# ====================== YOUR PORTFOLIO ======================
PORTFOLIO = {
    "Reliance": "RELIANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "L&T": "LT.NS",
    "Coforge": "COFORGE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HCLTech": "HCLTECH.NS",
    "SBI": "SBIN.NS",
    "IndusInd": "INDUSINDBK.NS",
    "ICICI": "ICICIBANK.NS",
    "Axis": "AXISBANK.NS",
    "Bandhan": "BANDHANBNK.NS",
    "ZEE": "ZEEL.NS",
    "ITC": "ITC.NS",
    "GAIL": "GAIL.NS",
    "HindPetro": "HINDPETRO.NS",
    "BPCL": "BPCL.NS",
    "LIC": "LICI.NS",
    "Nestle": "NESTLEIND.NS",
    "Maruti": "MARUTI.NS",
    "M&M": "M&M.NS",
    "PFC": "PFC.NS",
    "REC": "RECLTD.NS",
    "AsianPaints": "ASIANPAINT.NS",
    "Airtel": "BHARTIARTL.NS",
}

# ====================== FULL NIFTY 50 ======================
NIFTY50 = {
    "Adani Enterprises": "ADANIENT.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Bajaj Finserv": "BAJAJFINSV.NS",
    "Bharat Electronics": "BEL.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "BSE": "BSE.NS",
    "Cipla": "CIPLA.NS",
    "Coal India": "COALINDIA.NS",
    "Dr Reddy's": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Eternal": "ETERNAL.NS",
    "Grasim": "GRASIM.NS",
    "HCL Tech": "HCLTECH.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "Hindalco": "HINDALCO.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "IndiGo": "INDIGO.NS",
    "Infosys": "INFY.NS",
    "ITC": "ITC.NS",
    "Jio Financial": "JIOFIN.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Kotak Bank": "KOTAKBANK.NS",
    "L&T": "LT.NS",
    "M&M": "M&M.NS",
    "Maruti": "MARUTI.NS",
    "Max Healthcare": "MAXHEALTH.NS",
    "Nestle India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "Power Grid": "POWERGRID.NS",
    "Reliance": "RELIANCE.NS",
    "SBI": "SBIN.NS",
    "SBI Life": "SBILIFE.NS",
    "Shriram Finance": "SHRIRAMFIN.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Tata Consumer": "TATACONSUM.NS",
    "Tata Motors PV": "TMPV.NS",
    "Tata Steel": "TATASTEEL.NS",
    "TCS": "TCS.NS",
    "Tech Mahindra": "TECHM.NS",
    "Titan": "TITAN.NS",
    "Trent": "TRENT.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "Wipro": "WIPRO.NS",
}

# ====================== INDICATORS ======================
def heiken_ashi(df):
    ha = df.copy()
    ha["HA_Close"] = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4
    ha["HA_Open"] = 0.0
    ha.iloc[0, ha.columns.get_loc("HA_Open")] = (df["Open"].iloc[0] + df["Close"].iloc[0]) / 2
    for i in range(1, len(ha)):
        ha.iloc[i, ha.columns.get_loc("HA_Open")] = (
            ha["HA_Open"].iloc[i - 1] + ha["HA_Close"].iloc[i - 1]
        ) / 2
    ha["HA_High"] = ha[["High", "HA_Open", "HA_Close"]].max(axis=1)
    ha["HA_Low"] = ha[["Low", "HA_Open", "HA_Close"]].min(axis=1)
    return ha


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def supertrend(df, period=10, multiplier=3):
    high = df["HA_High"]
    low = df["HA_Low"]
    close = df["HA_Close"]

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    hl2 = (high + low) / 2

    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)

    final_upper = upper.copy()
    final_lower = lower.copy()
    st_dir = pd.Series(1, index=df.index)

    for i in range(1, len(df)):
        if upper.iloc[i] < final_upper.iloc[i - 1] or close.iloc[i - 1] > final_upper.iloc[i - 1]:
            final_upper.iloc[i] = upper.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        if lower.iloc[i] > final_lower.iloc[i - 1] or close.iloc[i - 1] < final_lower.iloc[i - 1]:
            final_lower.iloc[i] = lower.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i - 1]

        if st_dir.iloc[i - 1] == 1:
            st_dir.iloc[i] = -1 if close.iloc[i] < final_lower.iloc[i] else 1
        else:
            st_dir.iloc[i] = 1 if close.iloc[i] > final_upper.iloc[i] else -1

    return st_dir


def calculate_signals(ticker):
    try:
        data = yf.download(
            ticker,
            period="15d",
            interval="1h",
            progress=False,
            auto_adjust=True
        )

        if data.empty or len(data) < 60:
            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required = ["Open", "High", "Low", "Close", "Volume"]
        for col in required:
            if col not in data.columns:
                return None

        ha = heiken_ashi(data)
        ha["EMA50"] = ha["HA_Close"].ewm(span=50, adjust=False).mean()
        ha["RSI"] = calculate_rsi(ha["HA_Close"], 14)
        ha["RSI_SMA"] = ha["RSI"].rolling(14).mean()
        ha["ST"] = supertrend(ha)

        last = ha.iloc[-1]
        prev = ha.iloc[-2]

        price_cross_up = prev["HA_Close"] < prev["EMA50"] and last["HA_Close"] > last["EMA50"]
        price_cross_down = prev["HA_Close"] > prev["EMA50"] and last["HA_Close"] < last["EMA50"]

        rsi_cross_up = prev["RSI"] < prev["RSI_SMA"] and last["RSI"] > last["RSI_SMA"]
        rsi_cross_down = prev["RSI"] > prev["RSI_SMA"] and last["RSI"] < last["RSI_SMA"]

        st_green = last["ST"] == 1
        st_red = last["ST"] == -1

        signal = "—"
        if price_cross_up and st_green and rsi_cross_up:
            signal = "BUY"
        elif price_cross_down and st_red and rsi_cross_down:
            signal = "SELL"

        avg_vol = data["Volume"].tail(20).mean()

        return {
            "Price": round(float(last["HA_Close"]), 2),
            "Open": round(float(last["HA_Open"]), 2),
            "High": round(float(last["HA_High"]), 2),
            "Low": round(float(last["HA_Low"]), 2),
            "Volume": int(last["Volume"]) if not pd.isna(last["Volume"]) else 0,
            "AvgVol": int(avg_vol) if not pd.isna(avg_vol) else 0,
            "ST": "Green" if st_green else "Red",
            "RSI": round(float(last["RSI"]), 1) if not pd.isna(last["RSI"]) else None,
            "RSI_SMA": round(float(last["RSI_SMA"]), 1) if not pd.isna(last["RSI_SMA"]) else None,
            "Signal": signal,
        }
    except Exception:
        return None


def create_table(stock_dict, title):
    st.subheader(title)
    rows = []
    progress = st.progress(0)
    total = len(stock_dict)

    for i, (name, ticker) in enumerate(stock_dict.items()):
        res = calculate_signals(ticker)
        if res:
            rows.append({"Stock": name, "Symbol": ticker, **res})
        else:
            rows.append({
                "Stock": name, "Symbol": ticker,
                "Price": None, "Open": None, "High": None, "Low": None,
                "Volume": None, "AvgVol": None, "ST": "—",
                "RSI": None, "RSI_SMA": None, "Signal": "Error"
            })
        progress.progress((i + 1) / total)

    progress.empty()
    df = pd.DataFrame(rows)

    def color_signal(val):
        if val == "BUY":
            return "background-color: #0d3b1e; color: #3fb950; font-weight: bold"
        if val == "SELL":
            return "background-color: #3b0d0d; color: #f85149; font-weight: bold"
        return ""

    def color_st(val):
        if val == "Green":
            return "color: #3fb950; font-weight: bold"
        if val == "Red":
            return "color: #f85149; font-weight: bold"
        return ""

    styled = (
        df.style
        .map(color_signal, subset=["Signal"])
        .map(color_st, subset=["ST"])
        .format({
            "Price": "{:.2f}",
            "Open": "{:.2f}",
            "High": "{:.2f}",
            "Low": "{:.2f}",
            "RSI": "{:.1f}",
            "RSI_SMA": "{:.1f}",
            "Volume": "{:,.0f}",
            "AvgVol": "{:,.0f}"
        }, na_rep="—")
    )

    st.dataframe(styled, use_container_width=True, height=min(780, 40 + len(rows) * 35))
    return df


# ====================== UI ======================
st.title("NSE Live Dashboard · 1h Heiken Ashi")
st.caption("50-EMA + SuperTrend(10,3) + RSI(14)/SMA(14)  |  Auto-refresh every 60 seconds")

col1, col2 = st.columns([4, 1])
with col2:
    auto = st.checkbox("Auto-refresh every 60s", value=True)

placeholder = st.empty()

with placeholder.container():
    # ----- Section 1: Your Portfolio -----
    create_table(PORTFOLIO, "Your Portfolio Stocks")

    st.markdown("---")

    # ----- Section 2: Full Nifty 50 -----
    create_table(NIFTY50, "All Nifty 50 Stocks")

    st.caption(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}  |  "
        "Data source: Yahoo Finance  |  Crossovers are rare → Signal is often —"
    )

# Auto-refresh
if auto:
    time.sleep(60)
    st.rerun()
