import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import re

st.set_page_config(page_title="AI MARKET PRO", layout="centered")

# =========================
# TIME
# =========================
vn_time = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y %H:%M:%S")
st.caption(f"🕒 {vn_time}")

st.title("📊 AI Phân tích Vàng - Dầu - BTC (FULL)")

# =========================
# GOLD VN (VIEW ONLY)
# =========================
def get_sjc():
    try:
        data = requests.get("https://sjc.com.vn/giavang/textContent.php", timeout=10).text
        for line in data.split("\n"):
            if "Nhẫn" in line:
                nums = re.findall(r"\d+\.\d+", line)
                if len(nums) >= 2:
                    return nums[0], nums[1]
    except:
        pass
    return None, None

def get_doji():
    try:
        data = requests.get("https://giavang.doji.vn/", timeout=10).text
        nums = re.findall(r"\d{2},\d{3}", data)
        if len(nums) >= 2:
            return nums[0].replace(",", ""), nums[1].replace(",", "")
    except:
        pass
    return None, None

def get_pnj():
    try:
        data = requests.get("https://giavang.pnj.com.vn/", timeout=10).text
        nums = re.findall(r"\d{3},\d{3}", data)
        if len(nums) >= 2:
            return nums[0].replace(",", ""), nums[1].replace(",", "")
    except:
        pass
    return None, None

st.subheader("🇻🇳 Giá vàng nhẫn VN")

sjc_b, sjc_s = get_sjc()
doji_b, doji_s = get_doji()
pnj_b, pnj_s = get_pnj()

if sjc_s: st.write(f"SJC: {sjc_b} - {sjc_s}")
if doji_s: st.write(f"DOJI: {doji_b} - {doji_s}")
if pnj_s: st.write(f"PNJ: {pnj_b} - {pnj_s}")

# =========================
# DATA SAFE
# =========================
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3y&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            return None, None

        data = res.json()

        if not data.get('chart') or not data['chart'].get('result'):
            return None, None

        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=["price"]).dropna()

        return df, df.iloc[-1]['price']

    except:
        return None, None

# =========================
# RSI
# =========================
def calc_rsi(df):
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
    df['RSI'] = calc_rsi(df)

    latest = df.iloc[-1]

    notes = []

    if latest['MA7'] > latest['MA30']:
        notes.append("MA7 > MA30 → xu hướng ngắn hạn TĂNG")
    else:
        notes.append("MA7 < MA30 → xu hướng ngắn hạn GIẢM")

    if latest['price'] > latest['MA100']:
        notes.append("Giá > MA100 → xu hướng dài hạn TỐT")
    else:
        notes.append("Giá < MA100 → xu hướng dài hạn YẾU")

    if latest['RSI'] < 30:
        notes.append("RSI < 30 → quá bán (có thể bật)")
    elif latest['RSI'] > 70:
        notes.append("RSI > 70 → quá mua (dễ giảm)")

    # DECISION
    if latest['MA7'] > latest['MA30'] and latest['price'] > latest['MA100'] and latest['RSI'] < 70:
        decision = "📈 MUA"
    elif latest['MA7'] < latest['MA30'] and latest['price'] < latest['MA100'] and latest['RSI'] > 30:
        decision = "📉 BÁN"
    else:
        decision = "⏳ CHỜ"

    # COMMENT
    if latest['RSI'] < 30:
        comment = "⚠️ Đang giảm nhưng quá bán → có thể hồi kỹ thuật"
    elif latest['MA7'] > latest['MA30']:
        comment = "🚀 Xu hướng tăng rõ"
    else:
        comment = "📉 Xu hướng yếu → nên chờ"

    return df, latest, decision, notes, comment

# =========================
# SHOW
# =========================
def show(name, symbol):
    df, price = get_data(symbol)

    if df is None:
        st.error("❌ Không lấy được dữ liệu")
        return None

    df, latest, decision, notes, comment = analyze(df)

    st.subheader(name)
    st.write(f"💰 Giá: {round(price,2)}")
    st.write(f"📌 {decision}")
    st.write(f"📊 RSI: {round(latest['RSI'],2)}")
    st.info(comment)

    for n in notes:
        st.write(f"- {n}")

    st.line_chart(df[['price','MA7','MA30','MA100']])

    return decision

# =========================
# BUTTON
# =========================
col1, col2, col3 = st.columns(3)

gold = oil = btc = None

with col1:
    if st.button("🟡 Vàng"):
        gold = show("Vàng (GC=F)", "GC=F")

with col2:
    if st.button("🛢️ Dầu"):
        oil = show("Dầu (CL=F)", "CL=F")

with col3:
    if st.button("🪙 BTC"):
        btc = show("Bitcoin", "BTC-USD")

# =========================
# COMPARE
# =========================
if gold or oil or btc:
    st.subheader("⚖️ So sánh")

    results = {"Vàng": gold, "Dầu": oil, "BTC": btc}

    for k, v in results.items():
        if v:
            st.write(f"{k}: {v}")

    buy = [k for k, v in results.items() if v == "📈 MUA"]
    sell = [k for k, v in results.items() if v == "📉 BÁN"]

    if buy:
        st.success(f"🔥 NÊN MUA: {', '.join(buy)}")

    if sell:
        st.error(f"⚠️ NÊN TRÁNH: {', '.join(sell)}")
