import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. SIDE KONFIGURATION
st.set_page_config(page_title="App-Watcher Pro", page_icon="📈", layout="wide")

# PROFESSIONEL NORDNET/SAXO CSS (Høj kontrast & læsbarhed)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Mono:wght@500&display=swap');
    
    .stApp { background-color: #0b0e11; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Top Status Bar */
    .status-line {
        background-color: #161b22;
        padding: 15px 25px;
        border-radius: 6px;
        border: 1px solid #30363d;
        font-family: 'Roboto Mono', monospace;
        font-size: 16px;
        margin-bottom: 25px;
    }
    
    /* Info-kasser (Ens størrelse og høj kontrast) */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-bottom: 4px solid #005f5f; /* Nordnet Teal */
        padding: 25px;
        border-radius: 4px;
        text-align: center;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .m-label { color: #848d97; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
    .m-value { color: #ffffff !important; font-size: 30px; font-weight: 700; }
    
    /* Farver */
    .profit { color: #2ea043 !important; }
    .loss { color: #f85149 !important; }
    
    /* Knapper & Links */
    .trade-link {
        background-color: #005f5f;
        color: white !important;
        padding: 4px 10px;
        border-radius: 4px;
        text-decoration: none;
        font-size: 12px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA (Dine Nordnet-tal)
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. AI SCANNER MED DIREKTE LINKS
def get_market_opportunities():
    # Liste over populære certifikater og deres Nordnet-links
    assets = [
        {"Navn": "SØLV (SI=F)", "Ticker": "SI=F", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=S%C3%B8lv%20BULL"},
        {"Navn": "GULD (GC=F)", "Ticker": "GC=F", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Guld%20BULL"},
        {"Navn": "OLIE (CL=F)", "Ticker": "CL=F", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Olie%20BULL"},
        {"Navn": "NASDAQ 100", "Ticker": "NQ=F", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=NASDAQ%20BULL"},
        {"Navn": "S&P 500", "Ticker": "ES=F", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=S%26P%20BULL"},
        {"Navn": "BITCOIN", "Ticker": "BTC-USD", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Bitcoin%20BULL"},
        {"Navn": "TESLA", "Ticker": "TSLA", "Link": "https://www.nordnet.dk/markedet/certifikater?searchTerm=Tesla%20BULL"}
    ]
    scan = []
    for a in assets:
        try:
            d = yf.Ticker(a['Ticker']).history(period="2d")
            chg = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
            trend = "🟢 STIGER" if chg > 0 else "🔴 FALDER"
            signal = "BULL" if chg > 1.2 else "BEAR" if chg < -1.2 else "VENT"
            scan.append({
                "INSTRUMENT": a['Navn'],
                "TREND": trend,
                "ÆNDRING": f"{chg:.2f}%",
                "AI SIGNAL": signal,
                "HANDEL": a['Link']
            })
        except: pass
    return scan

# 4. LIVE BEREGNING OG VISNING
try:
    solv_usd = yf.Ticker("SI=F").history(period="1d", interval="1m")['Close'].iloc[-1]
    # Præcis estimering af certifikatkurs
    nu_cert_kurs = (solv_usd / 84.09) * 50.96 
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
    
    # STATUS LINJE
    p_class = "profit" if netto_profit >= 0 else "loss"
    st.markdown(f"""<div class="status-line">
        [{dansk_tid}] <span class="{p_class}">● {netto_profit:.2f} DKK ({profit_pct:.2f}%)</span> | Spot: ${solv_usd:.2f}
    </div>""", unsafe_allow_html=True)

    # PORTFOLIO SEKTION
    st.subheader("Portfolio: BULL XAG X4 VNT2")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-box"><div class="m-label">Markedsværdi</div><div class="m-value">{aktuel_vaerdi:.2f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="m-label">Netto Profit</div><div class="m-value {p_class}">{netto_profit:.2f} DKK</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-box"><div class="m-label">Aktuel Kurs</div><div class="m-value">{nu_cert_kurs:.2f}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-box"><div class="m-label">Breakeven</div><div class="m-value">{BREAKEVEN:.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # SCANNER MED LINKS
    st.subheader("🔍 Market Opportunities (AI Analysis)")
    df = pd.DataFrame(get_market_opportunities())
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "HANDEL": st.column_config.LinkColumn("Handel nu", display_text="ÅBN NORDNET")
        }
    )

except Exception as e:
    st.warning("Opdaterer markedskurser...")

# AUTO-REFRESH
time.sleep(30)
st.rerun()
