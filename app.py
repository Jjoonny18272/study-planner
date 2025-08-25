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
    return f"data_{user['email'].replace('@', '_at_').replace('.', '_dot_')}.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def priority_icon(priority):
    colors = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🔵", 5: "🟢"}
    return colors.get(priority, "⚪")

def calc_total_hours(schedule):
    total = 0
    for i in schedule:
        start = datetime.strptime(i["start"], "%H:%M")
        end = datetime.strptime(i["end"], "%H:%M")
        total += (end - start).seconds / 3600
    return total

# ---------------------- LOGIN ----------------------
if not st.session_state.logged_in:
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
    st.stop()

# ---------------------- HEADER AFTER LOGIN ----------------------
st.markdown('<div class="title">📘 STUDY PLANNER</div>', unsafe_allow_html=True)
st.markdown(f"👋 สวัสดีคุณ **{st.session_state.current_user['name']}** — ยินดีต้อนรับเข้าสู่ระบบ")
st.divider()

# ---------------------- MENU ----------------------
menu = st.sidebar.selectbox("📌 ไปยังหน้า", ["เพิ่มตาราง", "ดูตาราง", "ออกจากระบบ"])
filename = get_user_filename()

# ---------------------- LOGOUT ----------------------
if menu == "ออกจากระบบ":
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.success("คุณได้ออกจากระบบแล้ว")
    st.stop()

# ---------------------- ADD SCHEDULE ----------------------
if menu == "เพิ่มตาราง":
    st.subheader("➕ เพิ่มรายการอ่านหนังสือ")

    with st.form("add_form"):
        subject = st.text_input("ชื่อวิชา")
        date = st.date_input("วันที่จะอ่าน")
        start_time = st.time_input("เวลาเริ่มต้น")
        end_time = st.time_input("เวลาสิ้นสุด")
        priority = st.number_input("ลำดับความสำคัญ (1 = สูงสุด)", min_value=1, max_value=5, value=3)
        submitted = st.form_submit_button("➕ เพิ่มลงตาราง")

        if submitted:
            if subject.strip() == "":
                st.error("กรุณาใส่ชื่อวิชา")
            elif start_time >= end_time:
                st.error("เวลาเริ่มต้องน้อยกว่าสิ้นสุด")
            else:
                schedule = load_data(filename)
                schedule.append({
                    "subject": subject.strip(),
                    "date": date.strftime("%Y-%m-%d"),
                    "start": start_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M"),
                    "priority": priority
                })
                save_data(filename, schedule)
                st.success("✅ บันทึกเรียบร้อยแล้ว!")

# ---------------------- VIEW SCHEDULE ----------------------
elif menu == "ดูตาราง":
    st.subheader("📅 ตารางอ่านหนังสือของคุณ")
    schedule = load_data(filename)

    if not schedule:
        st.info("ยังไม่มีรายการ")
    else:
        # เรียงลำดับตามวัน เวลา และความสำคัญ
        schedule.sort(key=lambda x: (x["date"], x["start"], x["priority"]))

        # รวมเวลาทั้งหมด
        total_hours = calc_total_hours(schedule)
        st.info(f"⏳ เวลารวมทั้งหมด: {total_hours:.1f} ชั่วโมง")

        st.markdown("### 🔍 ตารางทั้งหมด (เรียงตามวัน/เวลา/ความสำคัญ)")
        st.dataframe(schedule, use_container_width=True)

        st.markdown("### 🧩 ตารางรายวัน")
        dates = sorted(list(set(item["date"] for item in schedule)))
        for d in dates:
            st.subheader(f"📆 {d}")
            daily = [item for item in schedule if item["date"] == d]
            daily.sort(key=lambda x: (x["start"], x["priority"]))
            for idx, item in enumerate(daily):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(
                        f"{priority_icon(item['priority'])} "
                        f"**{item['start']} - {item['end']}** | "
                        f"{item['subject']} | "
                        f"⭐ ความสำคัญ: {item['priority']}"
                    )
                with col2:
                    if st.button("🗑 ลบ", key=f"del-{d}-{idx}"):
                        schedule.remove(item)
                        save_data(filename, schedule)
                        st.experimental_rerun()
