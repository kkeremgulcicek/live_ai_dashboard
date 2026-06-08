import pandas_ta as ta
import plotly.graph_objects as go

# --- Gerçek zamanlı veri çek ---
ticker = "PLTR"
df = yf.download(ticker, period="5d", interval="5m")

# --- RSI ve MACD hesapla ---
df["RSI"] = ta.rsi(df["Close"], length=14)
macd = ta.macd(df["Close"])
df = pd.concat([df, macd], axis=1)

# --- Mum grafiği + RSI ---
fig = go.Figure()

# Mum grafiği
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Mum Grafiği"
))

# RSI grafiği ayrı panelde
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
fig_rsi.add_hline(y=30, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=70, line_dash="dash", line_color="green")

# Streamlit'te göster
st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig_rsi, use_container_width=True)
