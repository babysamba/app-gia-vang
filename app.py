import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import re

st.set_page_config(page_title="AI PRO MAX", layout="centered")

# =========================
# 🕒 GIỜ VN
# =========================
vn_time = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y %H:%M:%S")
st.caption(f"🕒 Giờ VN: {vn_time}")

st.title("📊 AI Săn kèo Vàng VN - Dầu - Bitcoin")

# =========================
# 📊 DATA THẾ GIỚI
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
# 🇻🇳 SJC
# =========================
def get_sjc_gold():
    try:
        url = "https://sjc.com.vn/giavang/textContent.php"
        data = requests.get(url, timeout=10).text

        for line in data.split("\n"):
            if "Nhẫn" in line:
                numbers = re.findall(r"\d+\.\d+", line)
                if len(numbers) >= 2:
                    return numbers[0], numbers[1]
        return None, None
    except:
        return None, None

# =========================
# 🇻🇳 DOJI
# =========================
def get_doji_gold():
    try:
        url = "https://giavang.doji.vn/"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).text

        numbers = re.findall(r"\d{2},\d{3}", data)
        if len(numbers) >= 2:
            return numbers[0].replace(",", ""), numbers[1].replace(",", "")
        return None, None
    except:
        return None, None

# =========================
# 🇻🇳 PNJ
# =========================
def get_pnj_gold():
    try:
        url = "https://giavang.pnj.com.vn/"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=10).text

        numbers = re.findall(r"\d{3},\d{3}", data)
        if len(numbers) >= 2:
            return numbers[0].replace(",", ""), numbers[1].replace(",", "")
        return None, None
    except:
        return None, None

# =========================
# 🇻🇳 GIÁ TRUNG BÌNH VN
# =========================
def get_vn_gold_price():
    sjc_buy, sjc_sell = get_sjc_gold()
    doji_buy, doji_sell = get_doji_gold()
    pnj_buy, pnj_sell = get_pnj_gold()

    prices = []

    for p in [sjc_sell, doji_sell, pnj_sell]:
        if p:
            prices.append(float(p))

    if len(prices) > 0:
        return sum(prices) / len(prices), prices
    else:
        return None, []

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
# 🧠 AI PHÂN TÍCH
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
        notes.append("MA7 > MA30 → xu hướng tăng")
    else:
        score -= 15
        notes.append("MA7 < MA30 → xu hướng giảm")

    if latest['price'] > latest['MA100']:
        score += 10
        notes.append("Giá trên MA100 → dài hạn tốt")
    else:
        score -= 10
        notes.append("Giá dưới MA100 → dài hạn yếu")

    if latest['RSI'] < 30:
        score += 15
        notes.append("RSI < 30 → quá bán")
    elif latest['RSI'] > 70:
        score -= 15
        notes.append("RSI > 70 → quá mua")

    if score >= 70:
        decision = "📈 MUA"
    elif score <= 40:
        decision = "📉 BÁN"
    else:
        decision = "⏳ CHỜ"

    if latest['RSI'] < 30 and latest['MA7'] < latest['MA30']:
        comment = "⚠️ Đang giảm nhưng quá bán → có thể hồi"
    elif latest['MA7'] > latest['MA30']:
        comment = "🚀 Xu hướng tăng rõ"
    else:
        comment = "📉 Xu hướng yếu → thận trọng"

    return df, latest, decision, notes, score, comment

# =========================
# 🇻🇳 HIỂN THỊ VÀNG VN
# =========================
def show_gold_vn():
    avg_price, prices = get_vn_gold_price()

    sjc_buy, sjc_sell = get_sjc_gold()
    doji_buy, doji_sell = get_doji_gold()
    pnj_buy, pnj_sell = get_pnj_gold()

    st.subheader("🇻🇳 Vàng nhẫn Việt Nam")

    if sjc_buy:
        st.write(f"SJC: {sjc_buy} - {sjc_sell}")
    if doji_buy:
        st.write(f"DOJI: {doji_buy} - {doji_sell}")
    if pnj_buy:
        st.write(f"PNJ: {pnj_buy} - {pnj_sell}")

    if avg_price:
        st.write(f"💰 Giá trung bình: {round(avg_price,2)} triệu")

        spread = max(prices) - min(prices)
        st.warning(f"⚠️ Chênh lệch: {round(spread,2)} triệu")

        # tạo data giả để phân tích
        df = pd.DataFrame([avg_price]*200, columns=["price"])

        df, latest, decision, notes, score, comment = analyze(df)

        st.write(f"📌 {decision}")
        st.write(f"🎯 Điểm: {score}/100")
        st.info(comment)

        for n in notes:
            st.write(f"- {n}")

        return decision
    else:
        st.error("❌ Không lấy được giá VN")
        return None

# =========================
# 📊 HIỂN THỊ KHÁC
# =========================
def show_result(name, symbol):
    df, price = get_data(symbol)

    if df is not None:
        df, latest, decision, notes, score, comment = analyze(df)

        st.subheader(name)
        st.write(f"💰 Giá: {round(price,2)}")
        st.write(f"📌 {decision}")
        st.write(f"🎯 Điểm: {score}/100")

        st.info(comment)

        for n in notes:
            st.write(f"- {n}")

        st.line_chart(df[['price','MA7','MA30','MA100']])

        return decision
    else:
        st.error("❌ Lỗi dữ liệu")
        return None

# =========================
# 🔘 NÚT
# =========================
col1, col2, col3 = st.columns(3)

gold_decision = oil_decision = btc_decision = None

with col1:
    if st.button("🟡 Vàng VN"):
        gold_decision = show_gold_vn()

with col2:
    if st.button("🛢️ Dầu"):
        oil_decision = show_result("DẦU (CL=F)", "CL=F")

with col3:
    if st.button("🪙 BTC"):
        btc_decision = show_result("BTC", "BTC-USD")

# =========================
# ⚖️ SO SÁNH
# =========================
if gold_decision or oil_decision or btc_decision:

    st.subheader("⚖️ So sánh")

    results = {
        "Vàng VN": gold_decision,
        "Dầu": oil_decision,
        "BTC": btc_decision
    }

    for k, v in results.items():
        if v:
            st.write(f"{k}: {v}")

    buy = [k for k, v in results.items() if v == "📈 MUA"]
    sell = [k for k, v in results.items() if v == "📉 BÁN"]

    if buy:
        st.success(f"🔥 NÊN MUA: {', '.join(buy)}")

    if sell:
        st.error(f"⚠️ NÊN TRÁNH: {', '.join(sell)}")
