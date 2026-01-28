import streamlit as st
from supabase import create_client
import pandas as pd

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

sleep_hours = st.number_input(
    "睡眠時間（時間）", min_value=0.0, max_value=24.0, step=0.5
)

exercise_minutes = st.number_input(
    "運動時間（分）", min_value=0, step=5
)

condition = st.slider(
    "今日の体調（1：悪い 〜 5：良い）", 1, 5, 3
)

# ===== データ追加 =====
if st.button("記録する"):
    supabase.table("health_logs").insert({
        "sleep_hours": sleep_hours,
        "exercise_minutes": exercise_minutes,
        "condition": condition
    }).execute()
    st.rerun()

# ===== データ取得 =====
logs = (
    supabase.table("health_logs")
    .select("*")
    .order("created_at", desc=False)
    .execute()
).data

if not logs:
    st.info("まだ記録がありません。")
    st.stop()

# DataFrame に変換
df = pd.DataFrame(logs)
df["created_at"] = pd.to_datetime(df["created_at"])

# ===== グラフ表示 =====
st.subheader("グラフ")

st.write("睡眠時間の推移")
st.line_chart(
    df.set_index("created_at")["sleep_hours"]
)

st.write("運動時間の推移")
st.bar_chart(
    df.set_index("created_at")["exercise_minutes"]
)

st.write("体調スコアの推移")
st.line_chart(
    df.set_index("created_at")["condition"]
)

# ===== 一覧表示 =====
st.subheader("記録一覧")

for log in reversed(logs):
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

    with col1:
        st.write(log["created_at"][:16])

    with col2:
        st.write(f"睡眠 {log['sleep_hours']} h")

    with col3:
        st.write(f"運動 {log['exercise_minutes']} min")

    with col4:
        st.write(f"体調 {log['condition']}")

    with col5:
        if st.button("削除", key=f"del{log['id']}"):
            supabase.table("health_logs").delete().eq(
                "id", log["id"]
            ).execute()
            st.rerun()
