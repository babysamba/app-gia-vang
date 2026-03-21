import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AI Phân tích tài sản", layout="centered")

st.title("📱 Phân tích Vàng - Crypto - Kim loại")

# =========================
# 📥 INPUT
# =========================
symbol = st.text_input(
    "Nhập mã tài sản (ví dụ: BTC-USD, ETH-USD, GC=F)",
    value="BTC-USD",
    key="input_symbol"
)

# =========================
# 📊 LẤY DỮ LIỆU (Yahoo)
# =========================
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"])
        df = df.dropna()

        price_now = df.iloc[-1]['price']

        return df, price_now
    except:
        return None, None

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
# 🔘 NÚT PHÂN TÍCH
# =========================
if analyze_btn:, key="analyze_btn"):
    df, price = get_data(symbol)

    if df is not None:
        st.success(f"💰 Giá hiện tại: {round(price,2)}")

        df, latest, score, decision, notes = analyze(df)

        st.subheader("📊 Kết quả")

        st.write(f"🎯 Điểm: {score}/100")
        st.write(f"📌 {decision}")
        st.write(f"RSI: {round(latest['RSI'],2)}")

        st.write("🧠 Nhận định:")
        for n in notes:
            st.write(f"- {n}")

        st.line_chart(df[['price','MA7','MA30','MA100']])

    else:
        st.error("❌ Không lấy được dữ liệu (kiểm tra lại mã)")
        # =========================
# 📥 INPUT (BÊN PHẢI)
# =========================
st.sidebar.header("🔎 Nhập mã tài sản")

symbol = st.sidebar.text_input(
    "Ví dụ: BTC-USD, ETH-USD, GC=F",
    value="BTC-USD",
    key="symbol_input"
)

analyze_btn = st.sidebar.button("📊 Phân tích")
