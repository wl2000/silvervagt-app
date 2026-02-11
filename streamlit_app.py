import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go

# 1. APP CONFIGURATION (Clean & Light)
st.set_page_config(page_title="StockWatch Pro", page_icon="📈", layout="wide")

# PROFESSIONEL CSS (eToro/Saxo Light Style)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
    
    .stApp { background-color: #f4f7f9; color: #1e222d; font-family: 'Inter', sans-serif; }
    
    /* Overskrift helt øverst */
    .main-title { font-size: 32px; font-weight: 700; color: #1e222d; margin-top: -60px; margin-bottom: 20px; }
    
    /* Info-kasser (Hvid baggrund, skygge) */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e3eb;
        text-align: left;
    }
    .m-label { color: #707a8a; font-size: 13px; font-weight: 500; text-transform: uppercase; }
    .m-value { color: #1e222d; font-size: 24px; font-weight: 700; margin-top: 5px; }
    
    /* Profit/Loss farver */
    .up { color: #00b15d !important; }
    .down { color: #ff3b30 !important; }

    /* Nyheds-kort (Rubiks-stil) */
    .news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
    .news-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e3eb;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .news-title { font-size: 14px; font-weight: 600; color: #1e222d; text-decoration: none; line-height: 1.4; }
    .news-title:hover { color: #0056b3; }
    .news-meta { font-size: 11px; color: #909399; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA (Dine Nordnet-tal)
ANTAL = 36
GAK_STK = 56.21
GEBYRER = 98.0
TOTAL_INV = (ANTAL * GAK_STK) + GEBYRER
BREAKEVEN = TOTAL_INV / ANTAL

# 3. HOVED LAYOUT
st.markdown('<h1 class="main-title">📈 StockWatch Pro</h1>', unsafe_allow_html=True)

try:
    # Hent data
    solv_ticker = yf.Ticker("SI=F")
    hist_data = solv_ticker.history(period="1d", interval="5m")
    solv_usd = hist_data['Close'].iloc[-1]
    
    # Beregning
    nu_cert_kurs = (solv_usd / 84.09) * 50.96
    aktuel_vaerdi = ANTAL * nu_cert_kurs
    netto_profit = aktuel_vaerdi - TOTAL_INV
    profit_pct = (netto_profit / TOTAL_INV) * 100
    p_class = "up" if netto_profit >= 0 else "down"

    # PORTFOLIO METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><div class="m-label">Værdi i DKK</div><div class="m-value">{aktuel_vaerdi:.2f}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="m-label">Netto Profit</div><div class="m-value {p_class}">{netto_profit:.2f} DKK ({profit_pct:.2f}%)</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="m-label">Seneste Kurs</div><div class="m-value">{nu_cert_kurs:.2f}</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="m-label">Breakeven</div><div class="m-value">{BREAKEVEN:.2f}</div></div>', unsafe_allow_html=True)

    # 4. FOKUSERET GRAF (Plotly for zoom-kontrol)
    st.markdown("<br>### 🥈 Silver Spot (Daily Range: 80 - 88)", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], mode='lines', line=dict(color='#007aff', width=2)))
    fig.update_layout(
        height=250, margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white', paper_bgcolor='#f4f7f9',
        yaxis=dict(range=[80, 88], gridcolor='#e0e3eb', zeroline=False),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. AI MARKET SCANNER
    st.markdown("### 🔍 Market Opportunities")
    assets = {"Sølv": "SI=F", "Guld": "GC=F", "Nasdaq": "NQ=F", "Bitcoin": "BTC-USD", "Tesla": "TSLA"}
    scan_list = []
    for navn, tick in assets.items():
        d = yf.Ticker(tick).history(period="1d")
        chg = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
        scan_list.append({
            "Instrument": navn, "Trend": f"{chg:.2f}%", 
            "Status": "🟢 BULL" if chg > 1 else "🔴 BEAR" if chg < -1 else "⚖️ VENT",
            "Handel": f"https://www.nordnet.dk/markedet/certifikater?searchTerm={navn}"
        })
    st.table(pd.DataFrame(scan_list))

    # 6. NEWS RUBIKS (Grid layout nederst)
    st.markdown("### 📰 Global Trading News Feed")
    news = yf.Search("Stock Market", max_results=20).news
    
    # HTML Grid construct
    news_html = '<div class="news-grid">'
    for n in news:
        time_str = datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')
        news_html += f"""
        <div class="news-card">
            <a href="{n['link']}" target="_blank" class="news-title">{n['title']}</a>
            <div class="news-meta">{n['publisher']} • Kl. {time_str}</div>
        </div>
        """
    news_html += '</div>'
    st.markdown(news_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Opdaterer markedet... {e}")

time.sleep(60)
st.rerun()
