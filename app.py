import streamlit as st
import json
import os
from datetime import datetime

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

st.set_page_config(page_title="Study Planner", layout="wide")
st.title("📚 แอพตารางอ่านหนังสือแบบตารางช่อง ๆ")

menu = st.sidebar.selectbox("เลือกหน้า", ["เพิ่มตาราง", "ดูตาราง"])

if menu == "เพิ่มตาราง":
    st.header("➕ เพิ่มวิชาในตาราง")

    with st.form("add_schedule"):
        subject = st.text_input("ชื่อวิชา")
        date = st.date_input("วันที่จะอ่าน")
        start_time = st.time_input("เวลาเริ่มต้น")
        end_time = st.time_input("เวลาสิ้นสุด")
        priority = st.number_input("ลำดับความสำคัญ (1 = สูงสุด)", min_value=1, max_value=5, value=3)

        submitted = st.form_submit_button("บันทึก")

        if submitted:
            if subject.strip() == "":
                st.error("กรุณาใส่ชื่อวิชา")
            elif start_time >= end_time:
                st.error("เวลาเริ่มต้นต้องก่อนเวลาสิ้นสุด")
            else:
                schedule = load_data("schedule_table.json")
                schedule.append({
                    "subject": subject.strip(),
                    "date": date.strftime("%Y-%m-%d"),
                    "start": start_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M"),
                    "priority": priority
                })
                save_data("schedule_table.json", schedule)
                st.success("✅ บันทึกเรียบร้อย")

elif menu == "ดูตาราง":
    st.header("📅 ตารางอ่านหนังสือ")

    schedule = load_data("schedule_table.json")

    if not schedule:
        st.info("ยังไม่มีรายการในตาราง")
    else:
        # เรียงตาม date, start time, และ priority
        schedule.sort(key=lambda x: (x["date"], x["start"], x["priority"]))

        # สร้าง DataFrame เพื่อแสดงเป็นตาราง
        st.markdown("### 🔎 ตารางทั้งหมด (เรียงตามวัน/เวลา/ความสำคัญ)")
        st.dataframe(schedule, use_container_width=True)

        st.markdown("### 🧩 ตารางรายวัน")
        # แยกตามวัน
        dates = sorted(list(set(item["date"] for item in schedule)))
        for d in dates:
            st.subheader(f"🗓️ วันที่ {d}")
            daily = [item for item in schedule if item["date"] == d]
            daily.sort(key=lambda x: (x["start"], x["priority"]))
            for item in daily:
                st.markdown(f"""
                - ⏰ {item['start']} - {item['end']} | 📝 {item['subject']} | ⭐ ลำดับความสำคัญ: {item['priority']}
                """)

