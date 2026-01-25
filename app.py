import streamlit as st
from supabase import create_client

@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

supabase = init_supabase()

st.title("ToDo リスト")

task = st.text_input("新しいタスク")

if st.button("追加"):
    if task:
        supabase.table("todos").insert({
            "task": task,
            "is_complete": False
        }).execute()
        st.rerun()

todos = (
    supabase.table("todos")
    .select("*")
    .order("created_at", desc=True)
    .execute()
).data

for todo in todos:
    col1, col2, col3 = st.columns([1, 6, 2])

    with col1:
        done = st.checkbox("", value=todo["is_complete"], key=todo["id"])
        if done != todo["is_complete"]:
            supabase.table("todos").update(
                {"is_complete": done}
            ).eq("id", todo["id"]).execute()
            st.rerun()

    with col2:
        st.write(todo["task"])

    with col3:
        if st.button("削除", key=f"del{todo['id']}"):
            supabase.table("todos").delete().eq(
                "id", todo["id"]
            ).execute()
            st.rerun()
