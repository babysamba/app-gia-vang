import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AI PRO MAX", layout="wide")

st.title("📱 AI Săn kèo Vàng - Crypto - Dầu - Cổ phiếu")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("🔎 Nhập mã")

symbol = st.sidebar.text_input("Mã chính", "BTC-USD")
symbol2 = st.sidebar.text_input("So sánh", "ETH-USD")

scan_list = st.sidebar.text_input(
    "Danh sách quét",
    "BTC-USD,ETH-USD,SOL-USD,GC=F,CL=F"
)

analyze_btn = st.sidebar.button("📊 Phân tích")

# =========================
# DATA (Yahoo)
# =========================
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"]).dropna()

        return df, df.iloc[-1]['price']
    except:
        return None, None

# =========================
# RSI
# =========================
def rsi(df):
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# =========================
# ANALYZE
# =========================
def analyze(df):
    df['MA7'] = df['price'].rolling(7).mean()
    df['MA30'] = df['price'].rolling(30).mean()
    df['MA100'] = df['price'].rolling(100).mean()
    df['RSI'] = rsi(df)

    latest = df.iloc[-1]

    score = 50
    if latest['MA7'] > latest['MA30']:
        score += 15
    else:
        score -= 15

    if latest['price'] > latest['MA100']:
        score += 10
    else:
        score -= 10

    if latest['RSI'] < 30:
        score += 15
    elif latest['RSI'] > 70:
        score -= 15

    if score >= 70:
        decision = "📈 MUA"
    elif score <= 40:
        decision = "📉 TRÁNH"
    else:
        decision = "⏳ CHỜ"

    return df, latest, score, decision

# =========================
# MAIN
# =========================
if analyze_btn:

    # --- PHÂN TÍCH CHÍNH ---
    df, price = get_data(symbol)

    if df is not None:
        df, latest, score, decision = analyze(df)

        st.subheader(f"📊 {symbol}")
        st.write(f"💰 Giá: {round(price,2)}")
        st.write(f"🎯 Điểm: {score}")
        st.write(f"📌 {decision}")

        # 🔔 RSI ALERT
        if latest['RSI'] < 30:
            st.warning("⚠️ QUÁ BÁN (có thể bật)")
        elif latest['RSI'] > 70:
            st.warning("⚠️ QUÁ MUA (dễ giảm)")

        st.line_chart(df[['price','MA7','MA30','MA100']])

    else:
        st.error("❌ Không lấy được dữ liệu")

    # =========================
    # ⚖️ SO SÁNH
    # =========================
    if symbol2:
        df2, _ = get_data(symbol2)

        if df2 is not None:
            _, latest2, score2, _ = analyze(df2)

            st.subheader("⚖️ So sánh")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"{symbol}: {score}")

            with col2:
                st.write(f"{symbol2}: {score2}")

            if score > score2:
                st.success(f"👉 {symbol} mạnh hơn")
            else:
                st.success(f"👉 {symbol2} mạnh hơn")

    # =========================
    # 🪙 SCAN
    # =========================
    st.subheader("🪙 Săn kèo")

    symbols = [s.strip().upper() for s in scan_list.split(",")]

    results = []

    for s in symbols:
        df_s, _ = get_data(s)
        if df_s is not None:
            _, latest_s, score_s, _ = analyze(df_s)
            results.append((s, score_s, latest_s['RSI']))

    if results:
        best = sorted(results, key=lambda x: x[1], reverse=True)

        st.write("🔥 Top cơ hội:")
        for r in best:
            st.write(f"{r[0]} | Điểm: {r[1]} | RSI: {round(r[2],2)}")
