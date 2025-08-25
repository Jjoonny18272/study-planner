import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random

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
    .completed {
        text-decoration: line-through;
        color: #888888;
        background-color: #f0f0f0;
        padding: 5px;
        border-radius: 5px;
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

def generate_date_range(start_date, end_date):
    """สร้างรายการวันที่ตั้งแต่วันเริ่มต้นถึงวันสิ้นสุด"""
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates

def auto_schedule_subject(subject_name, exam_date, hours_per_day, start_date=None):
    """จัดสรรตารางอ่านแบบอัตโนมัติ"""
    if start_date is None:
        start_date = datetime.now().date()
    
    # คำนวณจำนวนวันที่มี
    days_available = (exam_date - start_date).days
    if days_available <= 0:
        return []
    
    # สร้างตารางอ่าน
    schedule_items = []
    current_date = start_date
    
    # สุ่มเวลาเริ่มต้นและสิ้นสุดในแต่ละวัน
    time_slots = [
        ("08:00", "10:00"), ("10:00", "12:00"), ("13:00", "15:00"), 
        ("15:00", "17:00"), ("19:00", "21:00"), ("21:00", "23:00")
    ]
    
    days_count = 0
    while current_date < exam_date and days_count < days_available:
        # สุ่มช่วงเวลา
        start_time, end_time = random.choice(time_slots)
        
        # คำนวณชั่วโมงจริงของช่วงเวลาที่เลือก
        actual_hours = (datetime.strptime(end_time, "%H:%M") - 
                       datetime.strptime(start_time, "%H:%M")).seconds / 3600
        
        # ปรับให้ตรงกับชั่วโมงที่ต้องการ
        if actual_hours > hours_per_day:
            # ลดเวลาสิ้นสุด
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = start_dt + timedelta(hours=hours_per_day)
            end_time = end_dt.strftime("%H:%M")
        
        schedule_items.append({
            "subject": subject_name,
            "date": current_date.strftime("%Y-%m-%d"),
            "start": start_time,
            "end": end_time,
            "priority": 3,
            "completed": False,
            "auto_generated": True
        })
        
        current_date += timedelta(days=1)
        days_count += 1
    
    return schedule_items

# ---------------------- LOGIN ----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="title">📘 STUDY PLANNER</div>', unsafe_allow_html=True)
    st.caption("ผู้ช่วยจัดการตารางอ่านหนังสืออย่างมีระบบ ⏳📚")

    with st.form("login_form", clear_on_submit=True):
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
                st.rerun()

if not st.session_state.logged_in:
    st.stop()

# ---------------------- HEADER AFTER LOGIN ----------------------
st.markdown('<div class="title">📘 STUDY PLANNER</div>', unsafe_allow_html=True)
st.markdown(f"👋 สวัสดีคุณ **{st.session_state.current_user['name']}** — ยินดีต้อนรับเข้าสู่ระบบ")
st.divider()

# ---------------------- MENU ----------------------
menu = st.sidebar.selectbox("📌 ไปยังหน้า", ["เพิ่มตารางแบบปกติ", "เพิ่มตารางอัตโนมัติ", "ดูตาราง", "ออกจากระบบ"])
filename = get_user_filename()

# ---------------------- LOGOUT ----------------------
if menu == "ออกจากระบบ":
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.success("คุณได้ออกจากระบบแล้ว")
    st.rerun()

# ---------------------- ADD SCHEDULE (MANUAL) ----------------------
if menu == "เพิ่มตารางแบบปกติ":
    st.subheader("➕ เพิ่มรายการอ่านหนังสือ (แบบปกติ)")

    with st.form("add_form"):
        subject = st.text_input("ชื่อวิชา")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("วันที่เริ่มต้น")
        with col2:
            end_date = st.date_input("วันที่สิ้นสุด")
            
        start_time = st.time_input("เวลาเริ่มต้น")
        end_time = st.time_input("เวลาสิ้นสุด")
        priority = st.number_input("ลำดับความสำคัญ (1 = สูงสุด)", min_value=1, max_value=5, value=3)
        submitted = st.form_submit_button("➕ เพิ่มลงตาราง")

        if submitted:
            if subject.strip() == "":
                st.error("กรุณาใส่ชื่อวิชา")
            elif start_time >= end_time:
                st.error("เวลาเริ่มต้องน้อยกว่าสิ้นสุด")
            elif start_date > end_date:
                st.error("วันที่เริ่มต้นต้องไม่เกินวันที่สิ้นสุด")
            else:
                schedule = load_data(filename)
                date_range = generate_date_range(start_date, end_date)
                added_count = 0
                
                for single_date in date_range:
                    schedule.append({
                        "subject": subject.strip(),
                        "date": single_date.strftime("%Y-%m-%d"),
                        "start": start_time.strftime("%H:%M"),
                        "end": end_time.strftime("%H:%M"),
                        "priority": priority,
                        "completed": False,
                        "auto_generated": False
                    })
                    added_count += 1
                
                save_data(filename, schedule)
                st.success(f"✅ เพิ่มตารางเรียบร้อยแล้ว! ({added_count} วัน)")

# ---------------------- ADD SCHEDULE (AUTO) ----------------------
elif menu == "เพิ่มตารางอัตโนมัติ":
    st.subheader("🤖 เพิ่มตารางอ่านแบบอัตโนมัติ")
    st.info("💡 ระบบจะจัดสรรเวลาอ่านให้อัตโนมัติจากวันนี้จนถึงวันสอบ")

    with st.form("auto_add_form"):
        subject = st.text_input("ชื่อวิชา")
        exam_date = st.date_input("วันที่สอบ", min_value=datetime.now().date() + timedelta(days=1))
        hours_per_day = st.number_input("ชั่วโมงที่อยากอ่านต่อวัน", min_value=0.5, max_value=8.0, value=2.0, step=0.5)
        
        submitted = st.form_submit_button("🤖 สร้างตารางอัตโนมัติ")

        if submitted:
            if subject.strip() == "":
                st.error("กรุณาใส่ชื่อวิชา")
            else:
                schedule = load_data(filename)
                
                # สร้างตารางอัตโนมัติ
                auto_items = auto_schedule_subject(subject.strip(), exam_date, hours_per_day)
                
                if not auto_items:
                    st.error("ไม่สามารถสร้างตารางได้ เนื่องจากวันสอบใกล้เกินไป")
                else:
                    schedule.extend(auto_items)
                    save_data(filename, schedule)
                    st.success(f"✅ สร้างตารางอัตโนมัติเรียบร้อย! ({len(auto_items)} วัน)")
                    
                    # แสดงตัวอย่างตารางที่สร้าง
                    st.subheader("📋 ตัวอย่างตารางที่สร้าง")
                    for item in auto_items[:5]:  # แสดง 5 รายการแรก
                        st.write(f"📅 {item['date']} | ⏰ {item['start']}-{item['end']} | 📚 {item['subject']}")
                    
                    if len(auto_items) > 5:
                        st.write(f"... และอีก {len(auto_items) - 5} รายการ")

# ---------------------- VIEW SCHEDULE ----------------------
elif menu == "ดูตาราง":
    st.subheader("📅 ตารางอ่านหนังสือของคุณ")
    schedule = load_data(filename)

    if not schedule:
        st.info("ยังไม่มีรายการ")
    else:
        # เรียงลำดับตามวัน เวลา และความสำคัญ
        schedule.sort(key=lambda x: (x["date"], x["start"], x["priority"]))

        # สถิติ
        total_hours = calc_total_hours(schedule)
        completed_count = len([x for x in schedule if x.get("completed", False)])
        total_count = len(schedule)
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏳ เวลารวม", f"{total_hours:.1f} ชั่วโมง")
        with col2:
            st.metric("✅ อ่านจบแล้ว", f"{completed_count}/{total_count}")
        with col3:
            st.metric("📊 ความคืบหน้า", f"{completion_rate:.1f}%")

        st.markdown("### 🧩 ตารางรายวัน")
        dates = sorted(list(set(item["date"] for item in schedule)))
        for d in dates:
            st.subheader(f"📆 {d}")
            daily = [item for item in schedule if item["date"] == d]
            daily.sort(key=lambda x: (x["start"], x["priority"]))
            
            for idx, item in enumerate(daily):
                completed = item.get("completed", False)
                is_auto = item.get("auto_generated", False)
                
                col1, col2, col3, col4 = st.columns([1, 5, 1, 1])
                
                with col1:
                    # Checkbox สำหรับติ๊กว่าอ่านจบแล้ว
                    new_status = st.checkbox(
                        "อ่านจบ", 
                        value=completed, 
                        key=f"complete-{d}-{idx}"
                    )
                    
                    # อัพเดทสถานะถ้าเปลี่ยน
                    if new_status != completed:
                        item["completed"] = new_status
                        save_data(filename, schedule)
                        st.rerun()
                
                with col2:
                    # แสดงข้อมูลตาราง
                    style_class = "completed" if completed else ""
                    auto_badge = "🤖" if is_auto else ""
                    
                    content = (f"{priority_icon(item['priority'])} "
                              f"**{item['start']} - {item['end']}** | "
                              f"{item['subject']} {auto_badge} | "
                              f"⭐ ความสำคัญ: {item['priority']}")
                    
                    if completed:
                        st.markdown(f'<div class="completed">{content}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(content)
                
                with col3:
                    if completed:
                        st.success("✅")
                    else:
                        st.info("⏳")
                
                with col4:
                    if st.button("🗑", key=f"del-{d}-{idx}"):
                        schedule.remove(item)
                        save_data(filename, schedule)
                        st.rerun()

        # แสดงตารางทั้งหมด
        st.markdown("### 🔍 ตารางทั้งหมด")
        
        # เตรียมข้อมูลสำหรับแสดงในตาราง
        display_data = []
        for item in schedule:
            completed_status = "✅ เสร็จแล้ว" if item.get("completed", False) else "⏳ ยังไม่เสร็จ"
            auto_status = "🤖 อัตโนมัติ" if item.get("auto_generated", False) else "✋ กรอกเอง"
            
            display_data.append({
                "วันที่": item["date"],
                "วิชา": item["subject"],
                "เวลา": f"{item['start']} - {item['end']}",
                "ความสำคัญ": item["priority"],
                "สถานะ": completed_status,
                "ประเภท": auto_status
            })
        
        st.dataframe(display_data, use_container_width=True)
