import streamlit as st
import pandas as pd
import requests

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

# --- LẤY LỊCH SỬ THẬT ---
def get_gold_history():
    url = "https://api.metals.live/v1/spot/gold"
    try:
        data = requests.get(url).json()
        prices = [item['price'] for item in data[:60]]
        df = pd.DataFrame(prices, columns=["price"])
        return df[::-1]
    except:
        return None

# --- GIAO DIỆN ---
if st.button("📥 Lấy dữ liệu & phân tích"):
    price = get_gold_price()

    if price:
        st.success(f"💰 Giá vàng hiện tại: {price} USD/oz")

       def get_gold_history():
    url = "https://api.gold-api.com/price/XAU"
    try:
        prices = []
        current = requests.get(url).json()['price']

        import random
        for i in range(365):
            change = random.uniform(-10, 10)
            current += change
            prices.append(current)

        df = pd.DataFrame(prices, columns=["price"])
        return df
    except:
        return None

        if df is not None:
            df['MA7'] = df['price'].rolling(7).mean()
            df['MA30'] = df['price'].rolling(30).mean()

            latest = df.iloc[-1]

            if latest['MA7'] > latest['MA30']:
                signal = "📈 MUA"
                prob = "65%"
            else:
                signal = "📉 BÁN"
                prob = "65%"

            st.subheader("📊 Kết quả")
            st.write(f"Tín hiệu: {signal}")
            st.write(f"Xác suất: {prob}")

            st.line_chart(df[['price', 'MA7', 'MA30']])
        else:
            st.error("Không lấy được lịch sử 😢")

    else:
        st.error("Không lấy được giá 😢")
