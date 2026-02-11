import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. SIDE KONFIGURATION
st.set_page_config(page_title="StockWatch Pro", page_icon="📈", layout="wide")

# PROFESSIONEL CSS (Lysere grå toner & Skarpere kontrast)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Baggrund skiftet fra sort til mørkegrå for bedre dybde */
    .stApp { background-color: #1a1c23; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Titler */
    h1 { margin-top: -50px; font-weight: 800; color: #ffffff !important; letter-spacing: -1px; }
    h2, h3 { color: #e1e4e8 !important; border-bottom: 1px solid #30363d; padding-bottom: 10px; }

    /* Top Status Bar (Lysere) */
    .status-line {
        background-color: #2d333b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #444c56;
        font-family: monospace;
        font-size: 15px;
        margin-bottom: 25px;
        color: #adbac7;
    }
    
    /* Info-kasser (Lysere baggrund) */
    .metric-card {
        background-color: #22272e;
        border: 1px solid #444c56;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    .m-label { color: #768390; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .m-value { color: #ffffff; font-size: 26px; font-weight: 700; margin-top: 5px; }
    
    /* Nyheds-sektion styling */
    .news-box {
        background-color: #22272e;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #444c56;
        margin-bottom: 15px;
    }
    .news-link { color: #539bf5 !important; text-decoration: none; font-weight: 600; font-size: 16px; }
    .news-meta { color: #768390; font-size: 12px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA (Dine tal)
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. AI SCANNER MED MERE INFO
def get_extended_market_data():
    assets = {"SØLV": "SI=F", "GULD": "GC=F", "NASDAQ": "NQ=F", "BITCOIN": "BTC-USD", "OLIE": "CL=F", "TESLA": "TSLA"}
    results = []
    for navn, tick in assets.items():
        try:
            t = yf.Ticker(tick)
            d = t.history(period="1d")
            info = t.fast_info
            chg = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
            results.append({
                "INSTRUMENT": navn,
                "PRIS": f"{d['Close'].iloc[-1]:.2f}",
                "TREND %": f"{chg:.2f}%",
                "DAGS HØJ": f"{d['High'].max():.2f}",
                "VOLUMEN": f"{d['Volume'].iloc[-1]:,}",
                "SIGNAL": "🚀 BULL" if chg > 1 else "🧊 BEAR" if chg < -1 else "⚖️ NEUTRAL"
            })
        except: pass
    return pd.DataFrame(results)

# 4. HOVED LAYOUT
st.title("📈 StockWatch Pro")

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

    # STATUS LINE
    p_color = "#2ea043" if netto_profit >= 0 else "#f85149"
    st.markdown(f"""<div class="status-line">
        [{dansk_tid}] <span style="color:{p_color}; font-weight:bold;">● {netto_profit:.2f} DKK ({profit_pct:.2f}%)</span> | Spot Silver: ${solv_usd:.2f}
    </div>""", unsafe_allow_html=True)

    # METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><div class="m-label">Egenkapital</div><div class="m-value">{aktuel_vaerdi:.2f} DKK</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="m-label">Netto Afkast</div><div class="m-value" style="color:{p_color};">{netto_profit:.2f} DKK</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="m-label">Kurs (Est.)</div><div class="m-value">{nu_cert_kurs:.2f} DKK</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="m-label">Breakeven</div><div class="m-value">{BREAKEVEN:.2f} DKK</div></div>', unsafe_allow_html=True)

    # 5. GRAF (KUN LINJE)
    st.markdown("### 🥈 Live Silver Spot (Line Chart)")
    st.line_chart(hist_data['Close'], height=300)

    # 6. AI MARKET OPPORTUNITIES (Fuld bredde)
    st.markdown("### 🔍 AI Market Opportunities (Expanded Data)")
    st.table(get_extended_market_data())

    # 7. TRADING NEWS (Fuld bredde nederst)
    st.markdown("### 📰 Global Trading News (Top 20)")
    news = yf.Search("Finance", max_results=20).news
    for n in news:
        st.markdown(f"""
        <div class="news-box">
            <a href="{n['link']}" target="_blank" class="news-link">{n['title']}</a>
            <div class="news-meta">{n['publisher']} • {datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Forbindelsesfejl: {e}")

time.sleep(60)
st.rerun()
