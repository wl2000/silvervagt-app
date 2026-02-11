import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests

# 1. SIDE KONFIGURATION
st.set_page_config(page_title="SilverVagt Pro", page_icon="🥈", layout="wide")

# 2. DINE HANDELSDATA (Faste værdier)
ANTAL = 36
GAK_DKK = 56.21
GEBYRER_TOTAL = 98.0
TOTAL_INV = (ANTAL * GAK_DKK) + GEBYRER_TOTAL
BREAKEVEN = TOTAL_INV / ANTAL

# 3. FUNKTIONER
def hent_markedsdata():
    solv = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    return solv

def scan_markeder():
    forslag = []
    aktiver = {"Guld": "GC=F", "Olie": "CL=F", "Nasdaq": "NQ=F", "Bitcoin": "BTC-USD"}
    for navn, ticker in aktiver.items():
        data = yf.Ticker(ticker).history(period="1d", interval="15m")
        ændring = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        status = "🔥 BULL" if ændring > 1.2 else "📉 BEAR" if ændring < -1.2 else "⚖️ Neutral"
        forslag.append({"Aktiv": navn, "Status": status, "Ændring": f"{ændring:.2f}%"})
    return forslag

# 4. DASHBOARD LAYOUT
st.title("🥈 SilverVagt Pro - Live Dashboard")
dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
st.write(f"Sidst opdateret: {dansk_tid} (Dansk tid)")

col1, col2, col3 = st.columns(3)

# Hent live tal
nu_solv_usd = hent_markedsdata()
nu_certifikat_kurs = (nu_solv_usd / 84.22) * 56.21
aktuel_vaerdi = ANTAL * nu_certifikat_kurs
netto_profit = aktuel_vaerdi - TOTAL_INV
profit_pct = (netto_resultat / TOTAL_INV) * 100 if 'netto_resultat' in locals() else (netto_profit / TOTAL_INV) * 100

with col1:
    st.metric("Aktuel Værdi", f"{aktuel_vaerdi:.2f} DKK", f"{netto_profit:.2f} DKK")

with col2:
    st.metric("Sølv Spot (USD)", f"${nu_solv_usd:.2f}")

with col3:
    st.metric("Breakeven Kurs", f"{BREAKEVEN:.2f} DKK")

# 5. AI SCANNER SEKTION
st.subheader("🔍 AI Markeds-Scanner")
df_scan = pd.DataFrame(scan_markeder())
st.table(df_scan)

# 6. AUTOMATISK GENINDLÆSNING
st.empty()
time.sleep(30)
st.rerun()