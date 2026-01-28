import streamlit as st
from supabase import create_client

# Supabase 初期化
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

supabase = init_supabase()

st.title("健康管理アプリ")

# 入力欄
sleep_hours = st.number_input(
    "睡眠時間（時間）", min_value=0.0, max_value=24.0, step=0.5
)
exercise_minutes = st.number_input(
    "運動時間（分）", min_value=0, step=5
)

# データ追加
if st.button("記録する"):
    supabase.table("health_logs").insert({
        "sleep_hours": sleep_hours,
        "exercise_minutes": exercise_minutes
    }).execute()
    st.rerun()

st.subheader("記録一覧")

# データ取得
logs = (
    supabase.table("health_logs")
    .select("*")
    .order("created_at", desc=True)
    .execute()
).data

# 表示
for log in logs:
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

    with col1:
        st.write(log["created_at"][:16])

    with col2:
        st.write(f"睡眠：{log['sleep_hours']} 時間")

    with col3:
        st.write(f"運動：{log['exercise_minutes']} 分")

    with col4:
        if st.button("削除", key=f"del{log['id']}"):
            supabase.table("health_logs").delete().eq(
                "id", log["id"]
            ).execute()
            st.rerun()
