import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import time  # <--- Dette fjerner din NameError!

# 1. SETUP & NOTIFIKATIONER
NTFY_TOPIC = "solv_vagt_99"

def send_ntfy_status(besked, title="SilverVagt Status"):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {"Title": title, "Priority": "high", "Tags": "rocket,moneybag"}
    try:
        requests.post(url, data=besked.encode('utf-8'), headers=headers)
    except: pass

# 2. DINE HANDELSDATA FRA NORDNET
ANTAL = 36
KOEBSPRIS_STK = 56.21
GEBYRER_I_ALT = 98.0
TOTAL_INV = (ANTAL * KOEBSPRIS_STK) + GEBYRER_I_ALT
# Din GAK inkl. gebyrer er 58,93 DKK
BREAKEVEN = TOTAL_INV / ANTAL 

# 3. DASHBOARD LAYOUT
st.set_page_config(page_title="BULL XAG X4 VNT2 Vagt", page_icon="🥈")
st.title("🥈 BULL XAG X4 VNT2 - Live Vagt")

# Dansk tidskorrektion (CET+1)
dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
st.caption(f"Sidst opdateret: {dansk_tid}")

# 4. DATA HENTNING & BEREGNING
try:
    # Hent Sølv Spot (USD)
    solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    
    # Beregn certifikatkursen præcis ud fra din observation
    # Ved sølv 84,22 var dit certifikat 56,21 DKK
    nu_cert_kurs = (solv_usd / 84.22) * 56.21
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100

    # VISNING AF TAL
    col1, col2 = st.columns(2)
    
    with col1:
        farve = "normal" if netto_profit >= 0 else "inverse"
        st.metric("Netto Profit (efter gebyr)", f"{netto_profit:.2f} DKK", f"{profit_pct:.2f}%", delta_color=farve)
        st.write(f"**Aktuel Værdi:** {aktuel_vaerdi:.2f} DKK")

    with col2:
        st.metric("Sølv Spot (USD)", f"${solv_usd:.2f}")
        st.write(f"**BULL XAG X4 Pris (Estimeret):** {nu_cert_kurs:.2f} DKK")

    st.divider()
    st.info(f"🎯 Breakeven: Du skal over {BREAKEVEN:.2f} DKK på Nordnet for reel profit.")

    # Send alarm ved overskud
    if netto_profit > 0:
        send_ntfy_status(f"Profit! Værdi: {aktuel_vaerdi:.0f} DKK", "💰 BULL XAG X4 GEVINST")

except Exception as e:
    st.warning("Venter på live data fra markedet...")

# 5. AUTOMATISK REFRESH
time.sleep(30)
st.rerun()
