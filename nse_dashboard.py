import time
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="NSE Trading Dashboard V3",
    layout="wide",
    page_icon="📈",
)

IST = ZoneInfo("Asia/Kolkata")

# ============================================================
# KEEP YOUR EXISTING PORTFOLIO AND NIFTY50 DICTIONARIES HERE.
# Paste both dictionaries from your current file in this section.
# ============================================================

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
