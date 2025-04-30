import streamlit as st
import pandas as pd
from collections import Counter
import re

# ฟังก์ชันแปลง Google Sheets URL ให้กลายเป็นลิงก์ CSV ที่ pandas ใช้ได้
def convert_to_csv_url(google_sheet_url):
    match = re.match(r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9-_]+)', google_sheet_url)
    if match:
        sheet_id = match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', google_sheet_url)
        gid = gid_match.group(1) if gid_match else '0'
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    return None

# ฟังก์ชันโหลดข้อมูลจากลิงก์ CSV
def read_google_sheet(sheet_url):
    csv_url = convert_to_csv_url(sheet_url)
    if csv_url:
        return pd.read_csv(csv_url, encoding="utf-8-sig")
    return None

# ==== เริ่มต้น UI Streamlit ====
st.title("📊 วิเคราะห์งานที่พนักงานทำ")

sheet_url = st.text_input("🔗 วางลิงก์ Google Sheet ที่แชร์ให้เข้าถึงได้ (Anyone with the link)")

if sheet_url:
    df = read_google_sheet(sheet_url)

    if df is not None:
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
                st.dataframe(pd.DataFrame(count.items(), columns=["หัวข้องาน", "จำนวนครั้ง"]).sort_values(by="จำนวนครั้ง", ascending=False))
    else:
        st.error("❌ ไม่สามารถโหลดข้อมูลจากลิงก์ได้ กรุณาตรวจสอบลิงก์ว่าแชร์ถูกต้องหรือไม่")
