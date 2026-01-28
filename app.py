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

st.title("🕹️ 健康管理RPG")

# ===============================
# データ取得
# ===============================
logs = (
    supabase.table("health_logs")
    .select("*")
    .order("log_date", desc=False)
    .execute()
).data

df = pd.DataFrame(logs) if logs else pd.DataFrame()

# ===============================
# プレイヤーステータス
# ===============================
st.subheader("プレイヤーステータス")

total_logs = len(df)
xp = total_logs * 10
level = xp // 50 + 1
next_level_xp = (level * 50) - xp

col1, col2, col3 = st.columns(3)

col1.metric("Lv", level)
col2.metric("XP", xp)
col3.metric("次のLvまで", f"{next_level_xp} XP")

st.progress(min(xp % 50 / 50, 1.0))

st.divider()

# ===============================
# 入力フォーム
# ===============================
st.subheader("今日のクエスト")

with st.container():
    log_date = st.date_input("日付", value=date.today())

    sleep_hours = st.number_input(
        "睡眠時間（時間）", min_value=0.0, max_value=24.0, step=0.5
    )

    exercise_minutes = st.number_input(
        "運動時間（分）", min_value=0, step=5
    )

    condition = st.slider(
        "体調ゲージ", 1, 5, 3
    )

    meal_type = st.selectbox(
        "食事タイプ",
        ["自炊", "外食", "脂質多め", "野菜中心"]
    )

    if st.button("▶ クエスト完了"):
        supabase.table("health_logs").insert({
            "log_date": str(log_date),
            "sleep_hours": sleep_hours,
            "exercise_minutes": exercise_minutes,
            "condition": condition,
            "meal_type": meal_type
        }).execute()

        if sleep_hours >= 7:
            st.success("ボーナス達成！ 推奨睡眠時間クリア")

        st.rerun()

# ===============================
# データがない場合
# ===============================
if df.empty:
    st.info("まだ冒険が始まっていません。")
    st.stop()

df["log_date"] = pd.to_datetime(df["log_date"])

# ===============================
# グラフ
# ===============================
st.subheader("ステータス推移")

RECOMMENDED_SLEEP = 7.0
df["推奨睡眠時間"] = RECOMMENDED_SLEEP
df = df.set_index("log_date")

col_graph, col_info = st.columns([4, 1])

with col_graph:
    st.line_chart(df[["sleep_hours", "推奨睡眠時間"]])

with col_info:
    avg_sleep = df["sleep_hours"].mean()
    st.metric("平均睡眠", f"{avg_sleep:.1f} h")
    st.caption("目標：7時間")

st.subheader("運動ポイント")
st.bar_chart(df["exercise_minutes"].clip(lower=0))

st.subheader("体調ゲージ")
st.line_chart(df["condition"].clip(lower=1))

# ===============================
# ログ一覧
# ===============================
st.subheader("冒険ログ")

for log in reversed(logs):
    with st.container():
        cols = st.columns([2, 2, 2, 2, 2, 1])
        cols[0].write(log["log_date"])
        cols[1].write(f"睡眠 {log['sleep_hours']}h")
        cols[2].write(f"運動 {log['exercise_minutes']}分")
        cols[3].write(f"体調 {log['condition']}")
        cols[4].write(log["meal_type"])

        if cols[5].button("削除", key=f"del{log['id']}"):
            supabase.table("health_logs").delete().eq(
                "id", log["id"]
            ).execute()
            st.rerun()
