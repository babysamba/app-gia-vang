import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="App Giá Vàng PRO", layout="centered")

st.title("📱 Dự đoán giá vàng (PRO)")

# --- LẤY GIÁ VÀNG HIỆN TẠI ---
def get_gold_price():
    url = "https://api.gold-api.com/price/XAU"
    try:
        return requests.get(url).json()['price']
    except:
        return None

# --- LẤY DỮ LIỆU THẬT (Yahoo Finance) ---
def get_gold_history():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=3y&interval=1d"
    try:
        data = requests.get(url).json()
        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"])
        df = df.dropna()
        return df
    except:
        return None

# --- GIAO DIỆN ---
if st.button("📥 Phân tích giá vàng"):
    price = get_gold_price()

    if price:
        st.success(f"💰 Giá hiện tại: {price} USD/oz")

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
                note = "Xu hướng tăng, chưa quá mua"
            elif latest['MA7'] < latest['MA30'] and rsi > 30:
                signal = "📉 BÁN"
                note = "Xu hướng giảm"
            else:
                signal = "⏳ CHỜ"
                note = "Thị trường chưa rõ xu hướng"

            # HIỂN THỊ
            st.subheader("📊 Kết quả")
            st.write(f"Tín hiệu: {signal}")
            st.write(f"RSI: {round(rsi,2)}")
            st.write(f"Nhận định: {note}")

            st.line_chart(df[['price', 'MA7', 'MA30']])

        else:
            st.error("Không lấy được dữ liệu lịch sử 😢")

    else:
        st.error("Không lấy được giá vàng 😢")
