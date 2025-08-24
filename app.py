import streamlit as st
import json
import os
from datetime import datetime

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="📘 STUDY PLANNER",
    page_icon="📘",
    layout="wide"
)

st.markdown("""
    <style>
    .title {
        font-size: 28px;
        font-weight: bold;
        color: #3366cc;
        margin-bottom: 10px;
    }
    .main {
        background-color: #f5f8ff;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------- SESSION ----------------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("current_user", None)

# ---------------------- FUNCTIONS ----------------------
def get_user_filename():
    user = st.session_state.current_user
    return f"data_{user['email'].replace('@', '_at_')}.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------- LOGIN ----------------------
if not st.session_state.logged_in:
    st.image("https://cdn-icons-png.flaticon.com/512/4369/4369654.png", width=100)
    st.markdown('<div class="title">📘 STUDY PLANNER</div>', unsafe_allow_html=True)
    st.caption("ผู้ช่วยจัดการตารางอ่านหนังสืออย่างมีระบบ ⏳📚")

    with st.form("login_form"):
        email = st.text_input("อีเมล")
        name = st.text_input("ชื่อ")
        submitted = st.form_submit_button("เข้าสู่ระบบ")
        if submitted:
            if email.strip() == "" or name.strip() == "":
                st.error("กรุณากรอกชื่อและอีเมล")
            else:
                st.session_state.logged_in = True
                st.session_state.current_user = {
                    "email": email.strip(),
                    "name": name.strip()
                }
                st.success("✅ เข้าสู่ระบบเรียบร้อย")
                st.experimental_rerun()
    st.stop()

# ---------------------- HEADER AFTER LOGIN ----------------------
st.image("https://cdn-icons-png.flaticon.com/512/4369/4369654.png", width=70)
st.markdown('<div class="title">📘 STUDY PLANNER</div>', unsafe_allow_html=True)
st.markdown(f"👋 สวัสดีคุณ **{st.session_state.current_user['name']}** — ยินดีต้อนรับเข้าสู่ระบบ")
st.divider()

# ---------------------- MENU ----------------------
menu = st.sidebar.selectbox("📌 ไปยังหน้า", ["เพิ่มตาราง", "ดูตาราง", "ออกจากระบบ"])
filename = get_user_filename()

# ---------------------- LOGOUT ----------------------
if menu == "ออกจากระบบ":
    st.session_state.logged_in = False
    st.sessi
