import streamlit as st
import json
import os

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

st.title("📚 แอพจัดตารางอ่านหนังสือ")

menu = st.sidebar.selectbox("เลือกหน้า", ["ลงทะเบียนผู้ใช้", "จัดตารางเวลา", "ดูตารางอ่านหนังสือ", "แจ้งเตือน / สรุป"])

if menu == "ลงทะเบียนผู้ใช้":
    st.header("📝 ลงทะเบียน")
    name = st.text_input("ชื่อ")
    email = st.text_input("อีเมล")
    level = st.selectbox("ระดับชั้น", ["ม.ต้น", "ม.ปลาย", "มหาวิทยาลัย"])
    if st.button("บันทึก"):
        users = load_data("users.json")
        users.append({"name": name, "email": email, "level": level})
        save_data("users.json", users)
        st.success("✅ ลงทะเบียนเรียบร้อยแล้ว!")

elif menu == "จัดตารางเวลา":
    st.header("🗓️ จัดตารางเวลาอ่านหนังสือ")
    subjects = ["คณิต", "วิทย์", "อังกฤษ", "ประวัติศาสตร์", "อื่น ๆ"]
    subject = st.selectbox("เลือกวิชา", subjects)
    date = st.date_input("วันที่จะอ่าน")
    start_time = st.time_input("เวลาเริ่มอ่าน")
    end_time = st.time_input("เวลาสิ้นสุด")
    
    if st.button("บันทึกตาราง"):
        schedule = load_data("schedule.json")
        schedule.append({
            "subject": subject,
            "date": str(date),
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M"),
            "done": False
        })
        save_data("schedule.json", schedule)
        st.success("✅ บันทึกตารางเวลาเรียบร้อยแล้ว!")

elif menu == "ดูตารางอ่านหนังสือ":
    st.header("📅 ตารางอ่านหนังสือ")
    schedule = load_data("schedule.json")
    if not schedule:
        st.info("ยังไม่มีตารางอ่านหนังสือ")
    else:
        for idx, item in enumerate(schedule):
            st.write(f"{idx+1}. วิชา: {item['subject']} | วันที่: {item['date']} | เวลา: {item['start']} - {item['end']} | อ่านแล้ว: {'✔' if item['done'] else '✘'}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"แก้ไข {idx+1}"):
                    st.warning("ยังไม่รองรับการแก้ไขตอนนี้")
            with col2:
                if st.button(f"ลบ {idx+1}"):
                    schedule.pop(idx)
                    save_data("schedule.json", schedule)
                    st.experimental_rerun()

elif menu == "แจ้งเตือน / สรุป":
    st.header("🔔 แจ้งเตือน / สรุปการอ่าน")
    schedule = load_data("schedule.json")
    for idx, item in enumerate(schedule):
        st.write(f"{idx+1}. วิชา: {item['subject']} | วันที่: {item['date']} | เวลา: {item['start']} - {item['end']} | อ่านแล้ว: {'✔' if item['done'] else '✘'}")
        if not item['done']:
            if st.button(f"✓ อ่านเสร็จ {idx+1}"):
                schedule[idx]['done'] = True
                save_data("schedule.json", schedule)
                st.experimental_rerun()
