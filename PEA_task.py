import streamlit as st
import pandas as pd
import requests
from collections import Counter
from io import StringIO
import re

# 🔁 แปลงลิงก์ Google Sheet ให้โหลดแบบ CSV ได้
def convert_to_csv_url(google_sheet_url):
    try:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', google_sheet_url)
        sheet_id = match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', google_sheet_url)
        gid = gid_match.group(1) if gid_match else '0'
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    except Exception:
        return None

# 📥 โหลด Google Sheet (Google Form Support: header=1)
def read_google_sheet(sheet_url):
    csv_url = convert_to_csv_url(sheet_url)
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), encoding="utf-8-sig", header=1)  # 👈 ข้ามแถวแรก
        df.columns = df.columns.str.strip()  # 💡 ล้าง space ซ่อน
        return df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

# ================================
# 🧠 ส่วนหลักของแอป Streamlit
# ================================
st.title("📊 วิเคราะห์งานที่พนักงานทำ")

sheet_url = st.text_input("🔗 วางลิงก์ Google Sheet ที่แชร์แบบ Anyone (Viewer)")

if sheet_url:
    df = read_google_sheet(sheet_url)

    if df is not None:
        required_cols = ["รหัสพนักงาน", "รายการงานที่ทำ"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"❌ ไม่พบคอลัมน์: {missing}")
        else:
            emp_id = st.text_input("🔍 ใส่รหัสพนักงานที่ต้องการค้นหา")
            if emp_id:
                df_emp = df[df["รหัสพนักงาน"].astype(str) == emp_id]
                if df_emp.empty:
                    st.warning("ไม่พบรหัสพนักงานนี้ในข้อมูล")
                else:
                    work_items = []
                    for item in df_emp["รายการงานที่ทำ"].dropna():
                        work_items.extend([i.strip() for i in item.split(',')])
                    count = Counter(work_items)
                    st.subheader(f"พนักงานรหัส {emp_id} ทำงานทั้งหมด {sum(count.values())} ครั้ง")
                    st.dataframe(
                        pd.DataFrame(count.items(), columns=["หัวข้องาน", "จำนวนครั้ง"])
                        .sort_values(by="จำนวนครั้ง", ascending=False)
                    )
