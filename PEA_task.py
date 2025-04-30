import streamlit as st
import pandas as pd
import requests
from collections import Counter
from io import StringIO
import re

# ✅ แก้ภาษาไทยเพี้ยน (Mojibake)
def decode_mojibake(text):
    try:
        return text.encode('latin1').decode('tis-620')
    except:
        return text

# 🔁 แปลง Google Sheet URL → export CSV URL
def convert_to_csv_url(google_sheet_url):
    try:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', google_sheet_url)
        sheet_id = match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', google_sheet_url)
        gid = gid_match.group(1) if gid_match else '0'
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    except:
        return None

# 📥 โหลดข้อมูลจาก Google Sheet แบบไม่มี header แล้วแมปเอง
def read_google_sheet(sheet_url):
    csv_url = convert_to_csv_url(sheet_url)
    try:
        response = requests.get(csv_url)
        response.raise_for_status()

        # อ่านแบบไม่มี header
        df_raw = pd.read_csv(StringIO(response.text), encoding="utf-8-sig", header=None)

        # ตั้งชื่อคอลัมน์เอง (จากตำแหน่ง): A=เวลา, B=รหัส, C=รายการงานที่ทำ
        df_raw.columns = ["เวลา", "รหัสพนักงาน", "รายการงานที่ทำ"]

        # ลบแถวหัวตารางของ Google Form (index 0 และ 1)
        df_clean = df_raw.drop(index=[0, 1]).reset_index(drop=True)

        st.success("✅ โหลดสำเร็จ: ใช้คอลัมน์จากตำแหน่ง และแก้ภาษาไทยเพี้ยน")
        return df_clean

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

# ========================
# 🧠 ส่วนหลักของแอป
# ========================
st.title("📊 วิเคราะห์งานที่พนักงานทำ")

sheet_url = st.text_input("🔗 วางลิงก์ Google Sheet ที่แชร์แบบ Anyone (Viewer)")

if sheet_url:
    df = read_google_sheet(sheet_url)

    if df is not None:
        emp_id = st.text_input("🔍 ใส่รหัสพนักงานที่ต้องการค้นหา")

        if emp_id:
            df_emp = df[df["รหัสพนักงาน"].astype(str) == emp_id]

            if df_emp.empty:
                st.warning("ไม่พบรหัสพนักงานนี้ในข้อมูล")
            else:
                # ✅ แก้ภาษาไทยเพี้ยนใน cell และนับทุกหัวข้อย่อย
                all_tasks = []
                for row in df_emp["รายการงานที่ทำ"].dropna():
                    row = decode_mojibake(row)
                    tasks = [t.strip() for t in row.split(',') if t.strip()]
                    all_tasks.extend(tasks)

                count = Counter(all_tasks)

                st.subheader(f"พนักงานรหัส {emp_id} ทำงานทั้งหมด {sum(count.values())} ครั้ง")
                st.dataframe(
                    pd.DataFrame(count.items(), columns=["หัวข้องาน", "จำนวนครั้ง"])
                    .sort_values(by="จำนวนครั้ง", ascending=False)
                )
