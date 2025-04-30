import streamlit as st
import pandas as pd
import requests
from collections import Counter
import re
from io import StringIO

def convert_to_csv_url(google_sheet_url):
    """
    แปลง Google Sheet URL ให้เป็นลิงก์ CSV ที่โหลดได้
    """
    match = re.match(r'https://docs.google.com/spreadsheets/d/([a-zA-Z0-9-_]+)', google_sheet_url)
    if match:
        sheet_id = match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', google_sheet_url)
        gid = gid_match.group(1) if gid_match else '0'
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    return None

def read_google_sheet(sheet_url):
    """
    อ่านข้อมูลจาก Google Sheet ที่แชร์แบบสาธารณะโดยใช้ requests
    """
    csv_url = convert_to_csv_url(sheet_url)
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text), encoding="utf-8-sig")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

# ======================
# ส่วนของ Streamlit App
# ======================

st.title("📊 วิเคราะห์งานที่พนักงานทำ")

sheet_url = st.text_input("🔗 วางลิงก์ Google Sheet ที่แชร์แบบ Anyone (viewer ได้ก็พอ)")

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
