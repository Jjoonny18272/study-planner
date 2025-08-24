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

st.header("📝 ลงทะเบียน")

name = st.text_input("ชื่อ")
email = st.text_input("อีเมล")
level = st.selectbox("ระดับชั้น", ["ม.ต้น", "ม.ปลาย", "มหาวิทยาลัย"])

if st.button("บันทึก"):
    users = load_data("users.json")
    users.append({"name": name, "email": email, "level": level})
    save_data("users.json", users)
    st.success("✅ ลงทะเบียนเรียบร้อยแล้ว!")
