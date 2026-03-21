import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="App Vàng PRO MAX", layout="centered")

st.title("📱 AI Dự đoán giá vàng (PRO MAX)")

# --- LẤY GIÁ ---
def get_gold_price():
    url = "https://api.gold-api.com/price/XAU"
    try:
        return requests.get(url).json()['price']
    except:
        return None

# --- LỊCH SỬ 3 NĂM ---
def get_gold_history():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=3y&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        data = requests.get(url, headers=headers).json()
        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"])
        df = df.dropna()
        return df
    except:
        return None

# --- TÍNH RSI ---
def calculate_rsi(df):
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- PHÂN TÍCH ---
if st.button("📊 Phân tích ngay"):
    price = get_gold_price()

    if price:
        st.success(f"💰 Giá hiện tại: {price} USD/oz")

        df = get_gold_history()

        if df is not None:

            # MA
            df['MA7'] = df['price'].rolling(7).mean()
            df['MA30'] = df['price'].rolling(30).mean()
            df['MA100'] = df['price'].rolling(100).mean()

            # RSI
            df['RSI'] = calculate_rsi(df)

            latest = df.iloc[-1]

            score = 50
            notes = []

            # --- CHẤM ĐIỂM ---
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
                notes.append("Quá bán (có thể bật lên)")
            elif latest['RSI'] > 70:
                score -= 15
                notes.append("Quá mua (dễ giảm)")

            # --- KẾT LUẬN ---
            if score >= 70:
                decision = "📈 NÊN MUA"
            elif score <= 40:
                decision = "📉 NÊN TRÁNH"
            else:
                decision = "⏳ NÊN CHỜ"

            # --- HIỂN THỊ ---
            st.subheader("📊 Kết quả")

            st.write(f"🎯 Điểm cơ hội: {score}/100")
            st.write(f"📌 Kết luận: {decision}")
            st.write(f"📉 RSI: {round(latest['RSI'],2)}")

            st.write("🧠 Nhận định:")
            for n in notes:
                st.write(f"- {n}")

            st.line_chart(df[['price','MA7','MA30','MA100']])

        else:
            st.error("Không lấy được dữ liệu 😢")

    else:
        st.error("Không lấy được giá 😢")
