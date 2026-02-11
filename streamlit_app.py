import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import time

# 1. SETUP & APP KONFIGURATION
st.set_page_config(page_title="SilverVagt: App-Watcher", page_icon="📈", layout="wide")

# 2. HANDELSDATA: BULL XAG X4 VNT2
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. AI ANALYSE MODEL
def scan_markeder():
    forslag = []
    # Liste over interessante aktiver til BULL/BEAR certifikater
    aktiver = {
        "Sølv (SI=F)": "SI=F",
        "Guld (GC=F)": "GC=F",
        "Olie (CL=F)": "CL=F",
        "Nasdaq 100 (NQ=F)": "NQ=F",
        "S&P 500 (ES=F)": "ES=F",
        "Bitcoin (BTC-USD)": "BTC-USD",
        "Naturgas (NG=F)": "NG=F",
        "Tesla (TSLA)": "TSLA"
    }
    
    for navn, ticker in aktiver.items():
        try:
            data = yf.Ticker(ticker).history(period="2d", interval="15m")
            if len(data) > 1:
                nu_pris = data['Close'].iloc[-1]
                start_pris = data['Open'].iloc[0]
                ændring = ((nu_pris - start_pris) / start_pris) * 100
                
                # Simpel momentum-logik: Over 1.5% bevægelse signalerer trend
                if ændring > 1.5: signal = "🚀 KØB BULL (Stærk Trend)"
                elif ændring < -1.5: signal = "🧊 KØB BEAR (Stærk Trend)"
                elif ændring > 0.5: signal = "📈 Mild Bull"
                elif ændring < -0.5: signal = "📉 Mild Bear"
                else: signal = "⚖️ Neutral / Konsolidering"
                
                forslag.append({"Aktiv": navn, "Status": signal, "Ændring i dag": f"{ændring:.2f}%"})
        except: pass
    return pd.DataFrame(forslag)

# 4. HOVED DASHBOARD
st.title("🥈 SilverVagt: App-Watcher Pro")
dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Din Position: BULL XAG X4 VNT2")
    try:
        # Hent live data
        solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
        nu_cert_kurs = (solv_usd / 84.22) * 56.21
        aktuel_vaerdi = ANTAL * nu_cert_kurs
        netto_profit = aktuel_vaerdi - TOTAL_INV
        profit_pct = (netto_profit / TOTAL_INV) * 100
        
        # Visuel feedback
        m1, m2, m3 = st.columns(3)
        m1.metric("Netto Profit", f"{netto_profit:.2f} DKK", f"{profit_pct:.2f}%")
        m2.metric("Aktuel Værdi", f"{aktuel_vaerdi:.2f} DKK")
        m3.metric("Sølv Spot", f"${solv_usd:.2f}")
        
        st.progress(min(max((nu_cert_kurs / BREAKEVEN) / 2, 0.0), 1.0), text=f"Distance til Breakeven ({BREAKEVEN:.2f} DKK)")
    except:
        st.error("Kunne ikke hente markedskurser lige nu.")

with col2:
    st.subheader("🕒 Tidsstempel")
    st.write(f"Dansk tid: **{dansk_tid}**")
    st.info(f"Total investeret: {TOTAL_INV:.2f} DKK (Inkl. 98 kr gebyr)")

st.divider()

# 5. MARKEDS-SCANNER SEKTION
st.subheader("🔍 AI Markeds-Scanner & Handelsforslag")
st.write("Scanner for volumendrevne trends i realtid:")
st.dataframe(scan_markeder(), use_container_width=True)

# 6. REFRESH LOGIK
time.sleep(30)
st.rerun()
