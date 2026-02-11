import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. SIDE KONFIGURATION (Saxo-look)
st.set_page_config(page_title="App-Watcher Pro", page_icon="📈", layout="wide")

# PROFESSIONEL CSS (Saxo/Nordnet inspireret)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0b0e11; }
    
    .status-bar {
        background: #161b22;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 25px;
        font-family: monospace;
    }
    
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 4px;
        border-bottom: 3px solid #005f5f; /* Nordnet blågrøn */
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-label { color: #848d97; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { color: #ffffff; font-size: 22px; font-weight: 700; }
    .metric-delta { font-size: 14px; margin-top: 5px; }
    
    .up { color: #2ea043; }
    .down { color: #f85149; }
    </style>
    """, unsafe_allow_html=True)

# 2. HANDELSDATA (Dine tal)
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. AI ANALYSE MOTOR
def get_market_data():
    items = {
        "SØLV (SI=F)": "SI=F", "GULD (GC=F)": "GC=F", "OLIE (CL=F)": "CL=F",
        "NASDAQ 100": "NQ=F", "S&P 500": "ES=F", "BITCOIN": "BTC-USD", "TESLA": "TSLA"
    }
    results = []
    for navn, ticker in items.items():
        try:
            d = yf.Ticker(ticker).history(period="2d", interval="15m")
            change = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
            color = "🟢" if change > 0 else "🔴"
            results.append({"AKTIV": f"**{navn}**", "TREND": f"{color} {change:.2f}%", "ANBEFALING": "KØB BULL" if change > 1 else "KØB BEAR" if change < -1 else "NEUTRAL"})
        except: pass
    return results

# 4. LIVE BEREGNING
try:
    solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    # Præcis beregning baseret på dit Nordnet-køb
    nu_cert_kurs = (solv_usd / 84.22) * 56.21
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
    
    # STATUS LINJE
    p_color = "up" if netto_profit >= 0 else "down"
    st.markdown(f"""<div class="status-bar">
        [{dansk_tid}] <span class="{p_color}">{'●' if netto_profit >= 0 else '●'} {netto_profit:.2f} DKK ({profit_pct:.2f}%)</span> | Spot: ${solv_usd:.2f}
    </div>""", unsafe_allow_html=True)

    # DASHBOARD
    st.subheader("BULL XAG X4 VNT2 Portfolio")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">Markedsværdi</div><div class="metric-value">{aktuel_vaerdi:.2f} DKK</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Netto Profit</div><div class="metric-value {p_color}">{netto_profit:.2f} DKK</div><div class="metric-delta {p_color}">{profit_pct:.2f}%</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">Seneste Kurs</div><div class="metric-value">{nu_cert_kurs:.2f} DKK</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-label">Breakeven</div><div class="metric-value">{BREAKEVEN:.2f} DKK</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # SCANNER
    st.subheader("🔍 Market Opportunities")
    st.dataframe(
        get_market_data(),
        use_container_width=True,
        hide_index=True,
        column_config={
            "AKTIV": st.column_config.TextColumn("Instrument"),
            "TREND": st.column_config.TextColumn("24H Trend"),
            "ANBEFALING": st.column_config.TextColumn("AI Signal")
        }
    )

except Exception as e:
    st.error("Forbinder til markeds-feed...")

# AUTO-REFRESH
time.sleep(30)
st.rerun()
