import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. SIDE KONFIGURATION (Saxo-look)
st.set_page_config(page_title="App-Watcher Pro", page_icon="📈", layout="wide")

# PROFESSIONEL CSS (Høj læsbarhed & Nordnet layout)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    /* Baggrund og tekst */
    .stApp { background-color: #05070a; }
    h1, h2, h3, p, span { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    
    /* Top Status Bar */
    .status-line {
        background-color: #1a1e23;
        padding: 12px;
        border-radius: 4px;
        border-left: 5px solid #00c805;
        font-family: 'Roboto Mono', monospace;
        font-size: 16px;
        margin-bottom: 20px;
    }
    
    /* Store Info-kasser (Lige store og læsbare) */
    .metric-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .label { color: #8b949e; font-size: 13px; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; }
    .value { color: #ffffff; font-size: 28px; font-weight: 700; }
    
    /* Farver for profit/loss */
    .profit { color: #23d33a !important; }
    .loss { color: #f85149 !important; }
    
    /* Dataframe styling */
    .stDataFrame { border: 1px solid #30363d; border-radius: 8px; background-color: #0d1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA (Dine Nordnet-tal)
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN_KURS = TOTAL_INV / ANTAL

# 3. AI SCANNER LOGIK
def get_ai_opportunities():
    assets = {
        "SØLV (SI=F)": "SI=F", "GULD (GC=F)": "GC=F", "OLIE (CL=F)": "CL=F",
        "NASDAQ 100": "NQ=F", "S&P 500": "ES=F", "BITCOIN": "BTC-USD", "TESLA": "TSLA"
    }
    scan = []
    for navn, ticker in assets.items():
        try:
            d = yf.Ticker(ticker).history(period="2d")
            chg = ((d['Close'].iloc[-1] - d['Close'].iloc[0]) / d['Close'].iloc[0]) * 100
            trend = "🟢 STIGER" if chg > 0 else "🔴 FALDER"
            signal = "BULL" if chg > 1.5 else "BEAR" if chg < -1.5 else "VENT"
            scan.append({"INSTRUMENT": navn, "TREND": trend, "ÆNDRING": f"{chg:.2f}%", "SIGNAL": signal})
        except: pass
    return scan

# 4. LIVE BEREGNING
try:
    solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    # Estimeret certifikatkurs baseret på din 56,21 benchmark
    nu_cert_kurs = (solv_usd / 84.22) * 56.21
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
    
    # STATUS LINJE
    p_class = "profit" if netto_profit >= 0 else "loss"
    st.markdown(f"""<div class="status-line">
        [{dansk_tid}] <span class="{p_class}">● {netto_profit:.2f} DKK ({profit_pct:.2f}%)</span> | Spot: ${solv_usd:.2f}
    </div>""", unsafe_allow_html=True)

    # PORTEFØLJE OVERSIGT
    st.subheader(f"Portfolio: BULL XAG X4 VNT2")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-container"><div class="label">Markedsværdi</div><div class="value">{aktuel_vaerdi:.2f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-container"><div class="label">Netto Profit</div><div class="value {p_class}">{netto_profit:.2f} DKK</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-container"><div class="label">Aktuel Kurs</div><div class="value">{nu_cert_kurs:.2f}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-container"><div class="label">Breakeven</div><div class="value">{BREAKEVEN_KURS:.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # AI SCANNER
    st.subheader("🔍 Market Opportunities (AI Analysis)")
    df = pd.DataFrame(get_ai_opportunities())
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.toast("Opdaterer markedskurser...", icon="🔄")

# AUTO-REFRESH
time.sleep(30)
st.rerun()
