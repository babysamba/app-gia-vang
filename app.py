import streamlit as st
import pandas as pd
import requests
import random

st.set_page_config(page_title="App Giá Vàng", layout="centered")

st.title("📱 App dự đoán giá vàng")

# --- LẤY GIÁ VÀNG THẬT ---
def get_gold_price():
    url = "https://api.gold-api.com/price/XAU"
    try:
        data = requests.get(url).json()
        return data['price']
    except:
        return None

# --- LỊCH SỬ (giả lập thông minh hơn) ---
def get_gold_history():
    try:
        current = get_gold_price()
        prices = []

        for i in range(365):
            change = random.uniform(-10, 10)
            current += change
            prices.append(current)

        df = pd.DataFrame(prices, columns=["price"])
        return df
    except:
        return None

# --- GIAO DIỆN ---
if st.button("📥 Lấy dữ liệu & phân tích"):
    price = get_gold_price()

    if price:
        st.success(f"💰 Giá vàng hiện tại: {price} USD/oz")

        df = get_gold_history()

        if df is not None:

            # MA
            df['MA7'] = df['price'].rolling(7).mean()
            df['MA30'] = df['price'].rolling(30).mean()

            # RSI
            delta = df['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            rsi = latest['RSI']

            # TÍN HIỆU
            if latest['MA7'] > latest['MA30'] and rsi < 70:
                signal = "📈 MUA"
            elif latest['MA7'] < latest['MA30'] and rsi > 30:
                signal = "📉 BÁN"
            else:
                signal = "⏳ CHỜ"

            # HIỂN THỊ
            st.subheader("📊 Kết quả")
            st.write(f"Tín hiệu: {signal}")
            st.write(f"RSI: {round(rsi,2)}")

            st.line_chart(df[['price', 'MA7', 'MA30']])

        else:
            st.error("Không lấy được dữ liệu lịch sử 😢")

    else:
        st.error("Không lấy được giá vàng 😢")
