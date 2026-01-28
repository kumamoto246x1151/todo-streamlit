import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date

# ===============================
# Supabase 初期化
# ===============================
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

supabase = init_supabase()

# ===============================
# タイトル
# ===============================
st.title("Health Log")
st.caption("Daily sleep, exercise and condition tracking")

st.divider()

# ===============================
# 入力フォーム
# ===============================
st.subheader("New Record")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        log_date = st.date_input("Date", value=date.today())
        sleep_hours = st.number_input(
            "Sleep (hours)", min_value=0.0, max_value=24.0, step=0.5
        )
        exercise_minutes = st.number_input(
            "Exercise (minutes)", min_value=0, step=5
        )

    with col2:
        condition = st.slider(
            "Condition", 1, 5, 3
        )
        meal_type = st.selectbox(
            "Meal type",
            ["自炊", "外食", "脂質多め", "野菜中心"]
        )

    if st.button("Save"):
        supabase.table("health_logs").insert({
            "log_date": str(log_date),
            "sleep_hours": sleep_hours,
            "exercise_minutes": exercise_minutes,
            "condition": condition,
            "meal_type": meal_type
        }).execute()
        st.rerun()

# ===============================
# データ取得
# ===============================
logs = (
    supabase.table("health_logs")
    .select("*")
    .order("log_date", desc=False)
    .execute()
).data

if not logs:
    st.info("No data yet.")
    st.stop()

df = pd.DataFrame(logs)
df["log_date"] = pd.to_datetime(df["log_date"])
df = df.set_index("log_date")

# ===============================
# サマリー
# ===============================
st.divider()
st.subheader("Overview")

avg_sleep = df["sleep_hours"].mean()
avg_exercise = df["exercise_minutes"].mean()
avg_condition = df["condition"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Avg Sleep", f"{avg_sleep:.1f} h")
col2.metric("Avg Exercise", f"{avg_exercise:.0f} min")
col3.metric("Avg Condition", f"{avg_condition:.1f} / 5")

# ===============================
# グラフ
# ===============================
st.divider()
st.subheader("Trends")

RECOMMENDED_SLEEP = 7.0
df["Recommended sleep"] = RECOMMENDED_SLEEP

st.caption("Sleep duration")
st.line_chart(df[["sleep_hours", "Recommended sleep"]])

st.caption("Exercise time")
st.bar_chart(df["exercise_minutes"].clip(lower=0))

st.caption("Condition")
st.line_chart(df["condition"].clip(lower=1))

# ===============================
# ログ一覧
# ===============================
st.divider()
st.subheader("Records")

for log in reversed(logs):
    with st.container():
        cols = st.columns([2, 2, 2, 2, 2, 1])

        cols[0].write(log["log_date"])
        cols[1].write(f"{log['sleep_hours']} h")
        cols[2].write(f"{log['exercise_minutes']} min")
        cols[3].write(f"{log['condition']} / 5")
        cols[4].write(log["meal_type"])

        if cols[5].button("✕", key=f"del{log['id']}"):
            supabase.table("health_logs").delete().eq(
                "id", log["id"]
            ).execute()
            st.rerun()
