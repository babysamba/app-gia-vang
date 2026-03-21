import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AI Phân tích thị trường", layout="centered")

st.title("📊 AI Phân tích Vàng - Dầu - Bitcoin")

# =========================
# 📊 LẤY DỮ LIỆU (3 NĂM)
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

    # --- QUYẾT ĐỊNH ---
    if latest['MA7'] > latest['MA30'] and latest['RSI'] < 70:
        decision = "📈 MUA"
    elif latest['MA7'] < latest['MA30'] and latest['RSI'] > 30:
        decision = "📉 BÁN"
    else:
        decision = "⏳ CHỜ"

    return df, latest, decision

# =========================
# 📊 HIỂN THỊ
# =========================
def show_result(name, symbol):
    df, price = get_data(symbol)

    if df is not None:
        df, latest, decision = analyze(df)

        st.subheader(name)
        st.write(f"💰 Giá: {round(price,2)}")

        st.write(f"MA7: {round(latest['MA7'],2)}")
        st.write(f"MA30: {round(latest['MA30'],2)}")
        st.write(f"MA100: {round(latest['MA100'],2)}")
        st.write(f"RSI: {round(latest['RSI'],2)}")

        st.write(f"📌 Kết luận: {decision}")

        # 🔔 CẢNH BÁO
        if latest['RSI'] < 30:
            st.warning("⚠️ QUÁ BÁN → chuẩn bị bật")
        elif latest['RSI'] > 70:
            st.warning("⚠️ QUÁ MUA → dễ giảm")

        st.line_chart(df[['price','MA7','MA30','MA100']])

        return decision, latest['RSI']

    else:
        st.error("❌ Lỗi dữ liệu")
        return None, None

# =========================
# 🔘 NÚT
# =========================
col1, col2, col3 = st.columns(3)

gold_decision = oil_decision = btc_decision = None

with col1:
    if st.button("🟡 Vàng"):
        gold_decision, gold_rsi = show_result("VÀNG (GC=F)", "GC=F")

with col2:
    if st.button("🛢️ Dầu"):
        oil_decision, oil_rsi = show_result("DẦU (CL=F)", "CL=F")

with col3:
    if st.button("🪙 Bitcoin"):
        btc_decision, btc_rsi = show_result("BITCOIN (BTC-USD)", "BTC-USD")

# =========================
# ⚖️ SO SÁNH
# =========================
if gold_decision or oil_decision or btc_decision:

    st.subheader("⚖️ So sánh thị trường")

    results = {
        "Vàng": gold_decision,
        "Dầu": oil_decision,
        "Bitcoin": btc_decision
    }

    for k, v in results.items():
        if v:
            st.write(f"{k}: {v}")

    # 🔥 tìm cơ hội
    buy_candidates = [k for k, v in results.items() if v == "📈 MUA"]
    sell_candidates = [k for k, v in results.items() if v == "📉 BÁN"]

    if buy_candidates:
        st.success(f"🔥 NÊN CHÚ Ý MUA: {', '.join(buy_candidates)}")

    if sell_candidates:
        st.error(f"⚠️ ĐANG YẾU (CÓ THỂ BÁN): {', '.join(sell_candidates)}")
