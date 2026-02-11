import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. APP CONFIGURATION
st.set_page_config(page_title="StockWatch Pro", page_icon="📈", layout="wide")

# PROFESSIONEL CSS (Høj kontrast & læsbarhed)
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #848d97 !important; text-transform: uppercase; font-size: 12px !important; }
    .status-box { background-color: #111418; padding: 15px; border-radius: 5px; border: 1px solid #30363d; margin-bottom: 20px; font-family: monospace; }
    h1, h2, h3 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA (Dine Nordnet-tal)
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. NYHEDS-FUNKTION (20 seneste)
def hent_nyheder():
    try:
        search = yf.Search("Stock Market", max_results=20)
        return search.news
    except: return []

# 4. LIVE BEREGNING
try:
    solv_ticker = yf.Ticker("SI=F")
    hist_data = solv_ticker.history(period="1d", interval="5m")
    solv_usd = hist_data['Close'].iloc[-1]
    
    # Beregning baseret på dit Nordnet-køb
    nu_cert_kurs = (solv_usd / 84.09) * 50.96
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    dansk_tid = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")

    # STATUS BAR
    p_color = "🟢" if netto_profit >= 0 else "🔴"
    st.markdown(f"""<div class="status-box">[{dansk_tid}] {p_color} PROFIT: {netto_profit:.2f} DKK ({profit_pct:.2f}%) | SPOT SILVER: ${solv_usd:.2f}</div>""", unsafe_allow_html=True)

    st.title("📈 StockWatch Pro")
    
    # 5. METRICS (Portfolio)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Markedsværdi", f"{aktuel_vaerdi:.2f} DKK")
    c2.metric("Netto Afkast", f"{netto_profit:.2f} DKK", f"{profit_pct:.2f}%")
    c3.metric("Certifikat Kurs", f"{nu_cert_kurs:.2f} DKK")
    c4.metric("Breakeven", f"{BREAKEVEN:.2f} DKK")

    # 6. GRAF (Silver Spot Trend)
    st.subheader("🥈 Sølv Spot - 24T Udvikling")
    st.area_chart(hist_data['Close'], height=250, use_container_width=True)

    # 7. AI SCANNER & NYHEDER (To kolonner)
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🔍 Market Opportunities")
        assets = {"Sølv": "SI=F", "Guld": "GC=F", "Nasdaq": "NQ=F", "Bitcoin": "BTC-USD", "Olie": "CL=F"}
        scan_data = []
        for navn, tick in assets.items():
            d = yf.Ticker(tick).history(period="1d")
            chg = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
            scan_data.append({"Instrument": navn, "Trend": f"{chg:.2f}%", "Signal": "🚀 BULL" if chg > 1 else "🧊 BEAR" if chg < -1 else "⚖️ VENT"})
        st.table(pd.DataFrame(scan_data))

    with col_right:
        st.subheader("📰 Trading News (Top 20)")
        nyheder = hent_nyheder()
        if nyheder:
            for n in nyheder:
                st.markdown(f"**[{n['publisher']}]** [{n['title']}]({n['link']})")
                st.write("---")
        else:
            st.write("Henter nyheder...")

except Exception as e:
    st.error(f"Forbindelsesfejl: {e}")

# AUTO-REFRESH
time.sleep(60)
st.rerun()
