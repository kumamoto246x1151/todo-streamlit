import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date

# Supabase 初期化
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

supabase = init_supabase()

st.title("健康管理アプリ")

# ===== 入力欄 =====
st.subheader("今日の記録")

log_date = st.date_input(
    "日付",
    value=date.today()
)

sleep_hours = st.number_input(
    "睡眠時間（時間）", min_value=0.0, max_value=24.0, step=0.5
)

exercise_minutes = st.number_input(
    "運動時間（分）", min_value=0, step=5
)

condition = st.slider(
    "今日の体調（1：悪い 〜 5：良い）", 1, 5, 3
)

meal_type = st.selectbox(
    "食事内容",
    ["自炊", "外食", "脂質多め", "野菜中心"]
)

# ===== データ追加 =====
if st.button("記録する"):
    supabase.table("health_logs").insert({
        "log_date": str(log_date),
        "sleep_hours": sleep_hours,
        "exercise_minutes": exercise_minutes,
        "condition": condition,
        "meal_type": meal_type
    }).execute()
    st.rerun()

# ===== データ取得 =====
logs = (
    supabase.table("health_logs")
    .select("*")
    .order("log_date", desc=False)
    .execute()
).data

if not logs:
    st.info("まだ記録がありません。")
    st.stop()

df = pd.DataFrame(logs)
df["log_date"] = pd.to_datetime(df["log_date"])

# ===== グラフ表示 =====
st.subheader("グラフ")

st.write("睡眠時間の推移")
st.line_chart(
    df.set_index("log_date")["sleep_hours"]
)

st.write("運動時間の推移")
st.bar_chart(
    df.set_index("log_date")["exercise_minutes"]
)

st.write("体調スコアの推移")
st.line_chart(
    df.set_index("log_date")["condition"]
)

# ===== 一覧表示 =====
st.subheader("記録一覧")

for log in reversed(logs):
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])

    with col1:
        st.write(log["log_date"])

    with col2:
        st.write(f"睡眠 {log['sleep_hours']} h")

    with col3:
        st.write(f"運動 {log['exercise_minutes']} min")

    with col4:
        st.write(f"体調 {log['condition']}")

    with col5:
        st.write(log["meal_type"])

    with col6:
        if st.button("削除", key=f"del{log['id']}"):
            supabase.table("health_logs").delete().eq(
                "id", log["id"]
            ).execute()
            st.rerun()
