import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Phân tích thị trường", layout="centered")

st.title("📊 Phân tích Vàng - Dầu - Bitcoin")

# =========================
# 📊 LẤY DỮ LIỆU CHUNG (3 NĂM)
# =========================
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).json()

        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"]).dropna()

        return df, df.iloc[-1]['price']
    except:
        return None, None

# =========================
# 📊 TÍNH MA
# =========================
def add_ma(df):
    df['MA7'] = df['price'].rolling(7).mean()
    df['MA30'] = df['price'].rolling(30).mean()
    df['MA100'] = df['price'].rolling(100).mean()
    return df

# =========================
# 🧠 HIỂN THỊ
# =========================
def show_result(name, symbol):
    df, price = get_data(symbol)

    if df is not None:
        df = add_ma(df)

        st.subheader(f"{name}")
        st.write(f"💰 Giá hiện tại: {round(price,2)}")

        latest = df.iloc[-1]

        st.write(f"MA7: {round(latest['MA7'],2)}")
        st.write(f"MA30: {round(latest['MA30'],2)}")
        st.write(f"MA100: {round(latest['MA100'],2)}")

        # Phân tích nhanh
        if latest['MA7'] > latest['MA30']:
            st.success("📈 Xu hướng ngắn hạn: TĂNG")
        else:
            st.warning("📉 Xu hướng ngắn hạn: GIẢM")

        st.line_chart(df[['price','MA7','MA30','MA100']])

    else:
        st.error("❌ Lỗi dữ liệu")

# =========================
# 🔘 NÚT
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🟡 Vàng"):
        show_result("VÀNG (GC=F)", "GC=F")

with col2:
    if st.button("🛢️ Dầu"):
        show_result("DẦU WTI (CL=F)", "CL=F")

with col3:
    if st.button("🪙 Bitcoin"):
        show_result("BITCOIN (BTC-USD)", "BTC-USD")
