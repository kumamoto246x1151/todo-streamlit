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
st.title("健康管理アプリ")
st.caption("睡眠・運動・体調をシンプルに記録・可視化")

st.divider()

# ===============================
# 入力フォーム
# ===============================
st.subheader("新しい記録")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        log_date = st.date_input("日付", value=date.today())
        sleep_hours = st.number_input(
            "睡眠時間（時間）", min_value=0.0, max_value=24.0, step=0.5
        )
        exercise_minutes = st.number_input(
            "運動時間（分）", min_value=0, step=5
        )

    with col2:
        condition = st.slider(
            "体調", 1, 5, 3
        )
        meal_type = st.selectbox(
            "食事内容",
            ["自炊", "外食", "脂質多め", "野菜中心"]
        )

    if st.button("保存"):
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
    st.info("まだ記録がありません。")
    st.stop()

df = pd.DataFrame(logs)
df["log_date"] = pd.to_datetime(df["log_date"])
df = df.set_index("log_date")

# ===============================
# サマリー
# ===============================
st.divider()
st.subheader("サマリー")

avg_sleep = df["sleep_hours"].mean()
avg_exercise = df["exercise_minutes"].mean()
avg_condition = df["condition"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("平均睡眠時間", f"{avg_sleep:.1f} 時間")
col2.metric("平均運動時間", f"{avg_exercise:.0f} 分")
col3.metric("平均体調", f"{avg_condition:.1f} / 5")

# ===============================
# グラフ
# ===============================
st.divider()
st.subheader("推移")

RECOMMENDED_SLEEP = 7.0
df["推奨睡眠時間"] = RECOMMENDED_SLEEP

st.caption("睡眠時間")
st.line_chart(df[["sleep_hours", "推奨睡眠時間"]])

st.caption("運動時間")
st.bar_chart(df["exercise_minutes"].clip(lower=0))

st.caption("体調")
st.line_chart(df["condition"].clip(lower=1))

# ===============================
# 記録一覧
# ===============================
st.divider()
st.subheader("記録一覧")

for log in reversed(logs):
    with st.container():
        cols = st.columns([2, 2, 2, 2, 2, 1])

        cols[0].write(log["log_date"])
        cols[1].write(f"{log['sleep_hours']} 時間")
        cols[2].write(f"{log['exercise_minutes']} 分")
        cols[3].write(f"{log['condition']} / 5")
        cols[4].write(log["meal_type"])

        if cols[5].button("削除", key=f"del{log['id']}"):
            supabase.table("health_logs").delete().eq(
                "id", log["id"]
            ).execute()
            st.rerun()
