import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import time

# 1. APP KONFIGURATION (Saxo/Apple Style)
st.set_page_config(page_title="SilverVagt Ultra", page_icon="📈", layout="wide")

# CUSTOM CSS FOR PROFESSIONELT LOOK
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1c1f26; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    code { background-color: #ff4b4b22 !important; color: #ff4b4b !important; border: 1px solid #ff4b4b44; }
    .stDataFrame { border: 1px solid #30363d; border-radius: 10px; }
    h1, h2, h3 { font-family: 'SF Pro Display', sans-serif; letter-spacing: -0.5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. HANDELSDATA (DKK & 56.21)
ANTAL = 36
GAK_STK = 56.21 # Din købspris i DKK
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. AI ANALYSE MODEL (Opdateret visning)
def scan_markeder():
    forslag = []
    aktiver = {
        "SILVER (SI=F)": "SI=F", "GOLD (GC=F)": "GC=F", "CRUDE OIL (CL=F)": "CL=F",
        "NASDAQ 100 (NQ=F)": "NQ=F", "S&P 500 (ES=F)": "ES=F", 
        "BITCOIN (BTC-USD)": "BTC-USD", "TESLA (TSLA)": "TSLA"
    }
    for navn, ticker in aktiver.items():
        try:
            data = yf.Ticker(ticker).history(period="2d", interval="15m")
            if not data.empty:
                nu_pris = data['Close'].iloc[-1]
                start_pris = data['Open'].iloc[0]
                ændring = ((nu_pris - start_pris) / start_pris) * 100
                if ændring > 1.2: status = "🚀 STRONG BULL"
                elif ændring < -1.2: status = "🧊 STRONG BEAR"
                else: status = "⚖️ NEUTRAL"
                # Bruger Markdown-venlig tekst til dataframe
                forslag.append({"AKTIV": f"**{navn}**", "STATUS": status, "ÆNDRING": f"{ændring:.2f}%"})
        except: pass
    return pd.DataFrame(forslag)

# 4. LIVE BEREGNING
try:
    solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    # Estimat baseret på din købs-benchmark
    nu_cert_kurs = (solv_usd / 84.22) * 56.21
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
    
    # 5. UI VISNING
    st.markdown(f"### `[{dansk_tid}]` **{'🟢' if netto_profit > 0 else '🔴'} {netto_profit:.2f} DKK ({profit_pct:.2f}%)** | Spot: ${solv_usd:.2f}")
    
    st.title("🥈 SilverVagt Ultra")
    st.caption("Professionel overvågning af BULL XAG X4 VNT2")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("PORTEFØLJE", f"{aktuel_vaerdi:.2f} DKK")
    m2.metric("PROFIT (NETTO)", f"{netto_profit:.2f} DKK", f"{profit_pct:.2f}%")
    m3.metric("CERTIFIKAT KURS", f"{nu_cert_kurs:.2f} DKK")
    m4.metric("BREAKEVEN", f"{BREAKEVEN:.2f} DKK")

    st.markdown("---")

    # 6. MARKEDS-SCANNER (Lækkert layout)
    st.subheader("🔍 AI Market Scanner")
    df_scan = scan_markeder()
    st.dataframe(
        df_scan,
        column_config={
            "AKTIV": st.column_config.TextColumn("Aktiv (Bold)", width="medium"),
            "STATUS": st.column_config.TextColumn("Anbefaling"),
            "ÆNDRING": st.column_config.ProgressColumn("Trend", format="%.2f%%", min_value=-5, max_value=5)
        },
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.toast("Opdaterer markedskurser...", icon="🔄")

# 7. AUTO-REFRESH
time.sleep(30)
st.rerun()
