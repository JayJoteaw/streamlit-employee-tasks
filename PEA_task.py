import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re
import ftfy

# 🔁 แปลงลิงก์ Google Sheet เป็นลิงก์ CSV
def convert_to_csv_url(google_sheet_url):
    try:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', google_sheet_url)
        sheet_id = match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', google_sheet_url)
        gid = gid_match.group(1) if gid_match else '0'
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    except:
        return None

# 📥 โหลด Google Sheet
def read_google_sheet(sheet_url):
    csv_url = convert_to_csv_url(sheet_url)
    try:
        response = requests.get(csv_url)
        response.raise_for_status()

        df_raw = pd.read_csv(
            StringIO(response.text),
            encoding="utf-8",
            header=None,
            engine="python"
        )

        # ใช้แถวที่ 1 เป็น header
        df_raw.columns = ["เวลา", "รหัสพนักงาน", "รายการงานที่ทำ"]
        df_clean = df_raw[1:].reset_index(drop=True)

        # ใช้ ftfy แก้ไขตัวอักษร
        df_clean["รายการงานที่ทำ"] = df_clean["รายการงานที่ทำ"].apply(lambda x: ftfy.fix_text(x))

        st.success("✅ โหลดสำเร็จ")
        return df_clean

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

# ============================
# 🎯 ส่วนหลักของแอป Streamlit
# ============================
st.title("📊 วิเคราะห์งานที่พนักงานทำ")

sheet_url = st.text_input("🔗 วางลิงก์ Google Sheet ที่แชร์แบบ Anyone (Viewer)")

if sheet_url:
    df = read_google_sheet(sheet_url)

    if df is not None:
        emp_id = st.text_input("🔍 ใส่รหัสพนักงานที่ต้องการค้นหา")

        if emp_id:
            # กรองข้อมูลโดยใช้ rstrip() เพื่อกำจัดช่องว่าง
            df_emp = df[df["รหัสพนักงาน"].astype(str).str.strip() == emp_id.strip()]

            if df_emp.empty:
                st.warning("ไม่พบรหัสพนักงานนี้ในข้อมูล")
            else:
                # ✅ แสดงข้อมูลของพนักงานที่เจอ
                st.subheader(f"ข้อมูลของพนักงานรหัส {emp_id}")
                st.dataframe(df_emp)
