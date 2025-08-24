import streamlit as st
import json
import os
from datetime import datetime, timedelta

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

st.title("📚 แอพจัดตารางอ่านหนังสือ")

menu = st.sidebar.selectbox("เลือกหน้า", [
    "ลงทะเบียนผู้ใช้",
    "จัดตารางเวลา",
    "ดูตารางอ่านหนังสือ",
    "แจ้งเตือน / สรุป"
])

if menu == "ลงทะเบียนผู้ใช้":
    st.header("📝 ลงทะเบียนผู้ใช้")
    name = st.text_input("ชื่อ")
    email = st.text_input("อีเมล")
    level = st.selectbox("ระดับชั้น", ["ม.ต้น", "ม.ปลาย", "มหาวิทยาลัย"])

    if st.button("บันทึก"):
        if not name or not email:
            st.error("กรุณากรอกชื่อและอีเมลให้ครบ")
        else:
            users = load_data("users.json")
            users.append({"name": name, "email": email, "level": level})
            save_data("users.json", users)
            st.success("✅ ลงทะเบียนเรียบร้อยแล้ว!")

elif menu == "จัดตารางเวลา":
    st.header("🗓️ จัดตารางเวลาอ่านหนังสือ")
    subjects = ["คณิต", "วิทย์", "อังกฤษ", "ประวัติศาสตร์", "อื่น ๆ"]
    subject = st.selectbox("เลือกวิชา", subjects)
    start_date = st.date_input("วันที่เริ่มต้นอ่าน")
    end_date = st.date_input("วันที่สิ้นสุดอ่าน")
    start_time = st.time_input("เวลาเริ่มอ่าน")
    end_time = st.time_input("เวลาสิ้นสุดอ่าน")

    if start_date > end_date:
        st.error("❌ วันที่เริ่มต้นต้องไม่มากกว่าวันสิ้นสุด")
    elif start_time >= end_time:
        st.error("❌ เวลาเริ่มอ่านต้องน้อยกว่าเวลาสิ้นสุดอ่าน")
    else:
        if st.button("บันทึกตาราง"):
            schedule = load_data("schedule.json")
            schedule.append({
                "subject": subject,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "done_days": []
            })
            save_data("schedule.json", schedule)
            st.success("✅ บันทึกตารางเวลาเรียบร้อยแล้ว!")

elif menu == "ดูตารางอ่านหนังสือ":
    st.header("📅 ตารางอ่านหนังสือ")
    schedule = load_data("schedule.json")

    if not schedule:
        st.info("ยังไม่มีตารางอ่านหนังสือ")
    else:
        # ขยายตารางเป็นวัน ๆ
        expanded_schedule = []
        for idx, item in enumerate(schedule):
            sd = datetime.strptime(item["start_date"], "%Y-%m-%d")
            ed = datetime.strptime(item["end_date"], "%Y-%m-%d")
            delta_days = (ed - sd).days
            for i in range(delta_days + 1):
                day = sd + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                expanded_schedule.append({
                    "schedule_idx": idx,
                    "subject": item["subject"],
                    "date": date_str,
                    "start_time": item["start_time"],
                    "end_time": item["end_time"],
                    "done": date_str in item["done_days"]
                })

        # เรียงลำดับตาม date และเวลาเริ่ม
        expanded_schedule.sort(key=lambda x: (x["date"], x["start_time"]))

        for i, entry in enumerate(expanded_schedule):
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                st.write(f"📅 {entry['date']} เวลา {entry['start_time']} - {entry['end_time']} : วิชา {entry['subject']}")
            with col2:
                if not entry["done"]:
                    if st.button(f"✓ อ่านเสร็จ {i}", key=f"done-{i}"):
                        schedule = load_data("schedule.json")  # reload
                        done_days = schedule[entry["schedule_idx"]].get("done_days", [])
                        done_days.append(entry["date"])
                        schedule[entry["schedule_idx"]]["done_days"] = done_days
                        save_data("schedule.json", schedule)
                        st.experimental_rerun()
                else:
                    st.markdown("✔️")
            with col3:
                if st.button(f"❌ ลบ {i}", key=f"del-{i}"):
                    schedule = load_data("schedule.json")
                    idx = entry["schedule_idx"]
                    schedule.pop(idx)
                    save_data("schedule.json", schedule)
                    st.experimental_rerun()


