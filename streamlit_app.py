import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. APP CONFIGURATION
st.set_page_config(page_title="StockWatch Pro", page_icon="📈", layout="wide")

# PROFESSIONEL HIGH-CONTRAST CSS (Saxo/Nordnet Style)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Roboto+Mono:wght@500&display=swap');
    
    .stApp { background-color: #05070a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Top Status Bar */
    .status-line {
        background-color: #111418;
        padding: 15px 25px;
        border-radius: 4px;
        border-left: 6px solid #00c805;
        font-family: 'Roboto Mono', monospace;
        font-size: 16px;
        margin-bottom: 25px;
        color: #ffffff !important;
        border: 1px solid #30363d;
    }
    
    /* Info-kasser */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 4px;
        text-align: center;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .m-label { color: #8b949e; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; }
    .m-value { color: #ffffff !important; font-size: 32px; font-weight: 700; }
    
    /* Custom Tabel for AI Scanner */
    .stock-table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #0d1117; }
    .stock-table th { text-align: left; padding: 15px; border-bottom: 2px solid #30363d; color: #8b949e; font-size: 12px; letter-spacing: 1px; }
    .stock-table td { padding: 18px 15px; border-bottom: 1px solid #21262d; font-size: 15px; color: #ffffff !important; }
    .stock-table tr:hover { background-color: #161b22; }
    
    .btn-nordnet {
        background-color: #005f5f;
        color: white !important;
        padding: 8px 16px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .trend-up { color: #23d33a !important; font-weight: bold; }
    .trend-down { color: #f85149 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA (Dine Nordnet-tal)
ANTAL = 36
GAK_STK = 56.21 #
GEBYRER = 98.0  # 49 kr ved køb + 49 kr ved salg
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER

# 3. AI SCANNER LOGIK
def get_stock_watch_data():
    assets = [
        {"n": "SILVER (SI=F)", "t": "SI=F", "l": "https://www.nordnet.dk/markedet/certifikater?searchTerm=S%C3%B8lv%20BULL"},
        {"n": "GOLD (GC=F)", "t": "GC=F", "l": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Guld%20BULL"},
        {"n": "NASDAQ 100", "t": "NQ=F", "l": "https://www.nordnet.dk/markedet/certifikater?searchTerm=NASDAQ%20BULL"},
        {"n": "BITCOIN", "t": "BTC-USD", "l": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Bitcoin%20BULL"},
        {"n": "OIL (CL=F)", "t": "CL=F", "l": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Olie%20BULL"}
    ]
    html_rows = ""
    for a in assets:
        try:
            d = yf.Ticker(a['t']).history(period="1d")
            chg = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
            color_class = "trend-up" if chg > 0 else "trend-down"
            signal = "🚀 BULL" if chg > 1.2 else "🧊 BEAR" if chg < -1.2 else "↔️ VENT"
            html_rows += f"""
            <tr>
                <td><b>{a['n']}</b></td>
                <td class="{color_class}">{'+' if chg > 0 else ''}{chg:.2f}%</td>
                <td>{signal}</td>
                <td><a href="{a['l']}" target="_blank" class="btn-nordnet">HANDEL PÅ NORDNET</a></td>
            </tr>
            """
        except: pass
    return html_rows

# 4. BEREGNING AF PROFIT
try:
    solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    # Estimat: (Nu_Spot / Købs_Spot) * Købs_Kurs
    nu_cert_kurs = (solv_usd / 84.09) * 50.96 
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
    
    # STATUS LINJE
    p_color = "#23d33a" if netto_profit >= 0 else "#f85149"
    st.markdown(f'<div class="status-line">[{dansk_tid}] <span style="color:{p_color}; font-weight:bold;">● {netto_profit:.2f} DKK ({profit_pct:.2f}%)</span> | Live Spot: ${solv_usd:.2f}</div>', unsafe_allow_html=True)

    # DASHBOARD
    st.title("📈 StockWatch Pro")
    st.markdown("<h3 style='color:#8b949e; font-size:16px;'>BULL XAG X4 VNT2 Portfolio</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-box"><div class="m-label">Egenkapital</div><div class="m-value">{aktuel_vaerdi:.2f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="m-label">Netto Afkast</div><div class="m-value" style="color:{p_color} !important;">{netto_profit:.2f} DKK</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-box"><div class="m-label">Nordnet Kurs</div><div class="m-value">{nu_cert_kurs:.2f}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-box"><div class="m-label">Breakeven</div><div class="m-value">{(TOTAL_INV/ANTAL):.2f}</div></div>', unsafe_allow_html=True)

    # MARKEDS SCANNER
    st.markdown("<br><h2 style='color:white; font-size:20px;'>🔍 AI Market Scanner</h2>", unsafe_allow_html=True)
    table_html = f"""
    <table class="stock-table">
        <thead>
            <tr><th>INSTRUMENT</th><th>DAGLIG TREND</th><th>SIGNAL</th><th>DIREKTE LINK</th></tr>
        </thead>
        <tbody>
            {get_stock_watch_data()}
        </tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

except:
    st.info("Markedet opdateres...")

time.sleep(30)
st.rerun()
