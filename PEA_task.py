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
        df_raw.columns = ["เวลา", "รหัสพนักงาน", "ระบุงานที่ทำ"]
        df_clean = df_raw[1:].reset_index(drop=True)

        # ใช้ ftfy แก้ไขตัวอักษร
        df_clean["ระบุงานที่ทำ"] = df_clean["ระบุงานที่ทำ"].apply(lambda x: ftfy.fix_text(x))

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
                # 📊 แยกรายการงานที่ทำจากเครื่องหมาย "," และนับจำนวนงาน
                df_emp["รายการงานที่ทำแยก"] = df_emp["ระบุงานที่ทำ"].apply(lambda x: x.split(','))

                # นับจำนวนงานที่ทำ
                job_count = df_emp["รายการงานที่ทำแยก"].explode().value_counts()

                # สร้างตารางที่แสดงรายการงานและจำนวนครั้งที่ทำ
                job_count_df = job_count.reset_index()
                job_count_df.columns = ['ระบุงานที่ทำ', 'จำนวนครั้ง']
                
                # แยกหมายเลขออกจากข้อความหัวข้อเพื่อใช้ในการจัดลำดับ
                job_count_df['หมายเลข'] = job_count_df['ระบุงานที่ทำ'].apply(lambda x: int(x.split('.')[0].strip()) if x.split('.')[0].strip().isdigit() else 0)

                # เรียงลำดับงานตามหมายเลข
                job_count_df_sorted = job_count_df.sort_values(by='หมายเลข', ascending=True)

                # ลบคอลัมน์หมายเลขที่เพิ่มขึ้น
                job_count_df_sorted = job_count_df_sorted.drop(columns=["หมายเลข"])

                # แสดงผล
                st.subheader(f"จำนวนงานที่พนักงานรหัส {emp_id} ทำ")
                st.dataframe(job_count_df_sorted)

                # แสดงจำนวนงานรวมทั้งหมด
                total_jobs = job_count.sum()

                # แสดงผลข้อความในกรอบสีเขียว
                st.markdown(f'<div style="padding: 10px; border-radius: 5px; background-color: #e8f5e9; color: #388e3c; font-size: 18px; font-weight: bold;">พนักงานรหัส {emp_id} ทำงานรวมทั้งหมด {total_jobs} ครั้งในเดือนนี้</div>', unsafe_allow_html=True)
