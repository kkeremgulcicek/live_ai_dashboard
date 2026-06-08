import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz

st.set_page_config(page_title="Canlı Borsa Botu", layout="wide", page_icon="📊")

# --- Başlangıç Değerleri ---
if "cash" not in st.session_state:
    st.session_state.cash = 100.0
    st.session_state.pnl = 0.0
    st.session_state.trades = []

# --- Kullanıcıdan hisse seçimi ---
ticker = st.selectbox("Hisse Seç:", ["PLTR", "TSLA", "NVDA", "AAPL"])

# --- Veri Çek ---
df = yf.download(ticker, period="5d", interval="5m")
df["RSI"] = ta.rsi(df["Close"], length=14)
macd = ta.macd(df["Close"])
df = pd.concat([df, macd], axis=1)

# --- Sinyal Üret ---
last_rsi = df["RSI"].iloc[-1]
last_macd = df["MACDh_12_26_9"].iloc[-1]

signal = "BEKLE"
if last_rsi < 30 and last_macd > 0:
    signal = "AL"
elif last_rsi > 70 and last_macd < 0:
    signal = "SAT"

# --- İşlem Simülasyonu ---
price = df["Close"].iloc[-1]
if signal == "AL":
    st.session_state.trades.append({"time": datetime.now(), "ticker": ticker, "action": "AL", "price": price})
    st.session_state.cash -= price
elif signal == "SAT":
    st.session_state.trades.append({"time": datetime.now(), "ticker": ticker, "action": "SAT", "price": price})
    st.session_state.cash += price

# --- Dashboard ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Kasa", f"${st.session_state.cash:.2f}")
with col2:
    st.metric("Son Sinyal", signal)

st.dataframe(pd.DataFrame(st.session_state.trades))

# --- Grafik ---
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Mum"
))
fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", yaxis="y2"))

fig.update_layout(
    yaxis=dict(title="Fiyat"),
    yaxis2=dict(title="RSI", overlaying="y", side="right")
)

st.plotly_chart(fig, use_container_width=True)
