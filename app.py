import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="App Tài chính PRO MAX", layout="centered")

st.title("📱 AI Phân tích Vàng & Crypto")

# =========================
# 🟡 VÀNG
# =========================


def get_gold_history():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=3y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()
        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"])
        return df.dropna()
    except:
        return None

# =========================
# 🪙 BITCOIN (FIX FULL)
# =========================
# =========================
# 🪙 BITCOIN (FIX CHUẨN)
# =========================
def get_btc_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1d&interval=1m"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        return float(data['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return None

def get_btc_history():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=1y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"])
        return df.dropna()
    except:
        return None
# =========================
# 🛢️ OIL (DẦU)
# =========================
def get_oil_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=1d&interval=1m"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        return float(data['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return None

def get_oil_history():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=1y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"])
        return df.dropna()
    except:
        return None
# =========================
# 📊 RSI
# =========================
def calculate_rsi(df):
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# =========================
# 🧠 PHÂN TÍCH
# =========================
def analyze(df):
    df['MA7'] = df['price'].rolling(7).mean()
    df['MA30'] = df['price'].rolling(30).mean()
    df['MA100'] = df['price'].rolling(100).mean()
    df['RSI'] = calculate_rsi(df)

    latest = df.iloc[-1]

    score = 50
    notes = []

    if latest['MA7'] > latest['MA30']:
        score += 15
        notes.append("Xu hướng ngắn hạn tăng")
    else:
        score -= 15
        notes.append("Xu hướng ngắn hạn giảm")

    if latest['price'] > latest['MA100']:
        score += 10
        notes.append("Trend dài hạn tốt")
    else:
        score -= 10
        notes.append("Trend dài hạn yếu")

    if latest['RSI'] < 30:
        score += 15
        notes.append("Quá bán (có thể bật)")
    elif latest['RSI'] > 70:
        score -= 15
        notes.append("Quá mua (dễ giảm)")

    if score >= 70:
        decision = "📈 NÊN MUA"
    elif score <= 40:
        decision = "📉 NÊN TRÁNH"
    else:
        decision = "⏳ NÊN CHỜ"

    return df, latest, score, decision, notes

# =========================
# 🔘 VÀNG
# =========================
if st.button("🟡 Phân tích Vàng"):
    price = get_gold_price()
    df = get_gold_history()

    if price and df is not None:
        st.success(f"💰 Giá vàng: {price} USD")

        df, latest, score, decision, notes = analyze(df)

        st.subheader("📊 Kết quả Vàng")
        st.write(f"🎯 Điểm: {score}/100")
        st.write(f"📌 {decision}")
        st.write(f"RSI: {round(latest['RSI'],2)}")

        for n in notes:
            st.write(f"- {n}")

        st.line_chart(df[['price','MA7','MA30','MA100']])
    else:
        st.error("Lỗi dữ liệu vàng 😢")

# =========================
# 🔘 BTC
# =========================
if st.button("🪙 Phân tích Bitcoin"):
    price = get_btc_price()
    df = get_btc_history()

    if price and df is not None:
        st.success(f"💰 Bitcoin: {price} USD")

        df, latest, score, decision, notes = analyze(df)

        st.subheader("📊 Kết quả Bitcoin")
        st.write(f"🎯 Điểm: {score}/100")
        st.write(f"📌 {decision}")
        st.write(f"RSI: {round(latest['RSI'],2)}")

        for n in notes:
            st.write(f"- {n}")

        st.line_chart(df[['price','MA7','MA30','MA100']])
    else:
        st.error("Lỗi dữ liệu BTC 😢")
        # =========================
# 🔘 OIL
# =========================
if st.button("🛢️ Phân tích Dầu"):
    price = get_oil_price()
    df = get_oil_history()

    if price and df is not None:
        st.success(f"💰 Dầu WTI: {price} USD")

        df, latest, score, decision, notes = analyze(df)

        st.subheader("📊 Kết quả Dầu")
        st.write(f"🎯 Điểm: {score}/100")
        st.write(f"📌 {decision}")
        st.write(f"RSI: {round(latest['RSI'],2)}")

        # 🔔 Cảnh báo
        if latest['RSI'] < 30:
            st.warning("⚠️ QUÁ BÁN (có thể bật)")
        elif latest['RSI'] > 70:
            st.warning("⚠️ QUÁ MUA (dễ giảm)")

        for n in notes:
            st.write(f"- {n}")

        st.line_chart(df[['price','MA7','MA30','MA100']])

    else:
        st.error("Lỗi dữ liệu dầu 😢")
