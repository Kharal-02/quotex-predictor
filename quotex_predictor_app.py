import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Page settings
st.set_page_config(page_title="Quotex 1-Minute Candle Predictor", layout="centered")
st.title("🔮 Quotex 1-Minute Candle Predictor")
st.markdown("**Predict next candle using RSI, EMA, and pattern detection**")

# Asset dropdown
symbol_map = {
    "EUR/USD": "EURUSD=X",
    "BTC/USD": "BTC-USD",
    "XAU/USD (Gold)": "XAUUSD=X"
}
asset = st.selectbox("Select Asset", list(symbol_map.keys()))
symbol = symbol_map[asset]

# Fetch market data
df = yf.download(tickers=symbol, period="2h", interval="1m")
df.dropna(inplace=True)

# Check if enough data is available
if df.empty or len(df) < 3:
    st.error("⚠️ Failed to fetch enough data. Please try again later or change asset.")
    st.stop()

# Add technical indicators
df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
df["ema20"] = ta.trend.EMAIndicator(df["Close"], window=20).ema_indicator()
df["ema50"] = ta.trend.EMAIndicator(df["Close"], window=50).ema_indicator()

# Pattern detection
def detect_pattern(row, prev_row):
    if prev_row["Close"] < prev_row["Open"] and row["Close"] > row["Open"] and row["Close"] > prev_row["Open"] and row["Open"] < prev_row["Close"]:
        return "Bullish Engulfing"
    elif prev_row["Close"] > prev_row["Open"] and row["Close"] < row["Open"] and row["Open"] > prev_row["Close"] and row["Close"] < prev_row["Open"]:
        return "Bearish Engulfing"
    return "No Clear Pattern"

# Latest candles
latest = df.iloc[-1]
previous = df.iloc[-2]
pattern = detect_pattern(latest, previous)

rsi = latest["rsi"]
ema_trend = "UP" if latest["ema20"] > latest["ema50"] else "DOWN"

# Prediction logic
if pattern == "Bullish Engulfing" and rsi < 70 and ema_trend == "UP":
    prediction = "🔼 NEXT Candle = UP"
elif pattern == "Bearish Engulfing" and rsi > 30 and ema_trend == "DOWN":
    prediction = "🔽 NEXT Candle = DOWN"
else:
    prediction = "❔ NEXT Candle = NEUTRAL / UNCLEAR"

# Display results
st.subheader("📊 Analysis Result")
st.write("**Asset:**", asset)
st.write("**Last Candle Close:**", round(latest["Close"], 5))
st.write("**RSI:**", round(rsi, 2))
st.write("**EMA Trend:**", ema_trend)
st.write("**Pattern Detected:**", pattern)
st.success(f"**{prediction}**")

# Footer
st.markdown("---")
st.caption("Made with ❤️ for Quotex traders")
