import streamlit as st
import pandas as pd
import requests
from collections import Counter
from io import StringIO
import re
from ftfy import fix_text  # สำหรับแก้ mojibake

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

# 📥 โหลด Google Sheet และจัดการ encoding เพี้ยน
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

        df_raw.columns = ["เวลา", "รหัสพนักงาน", "รายการงานที่ทำ"]
        df_clean = df_raw.drop(index=[0, 1]).reset_index(drop=True)

        st.success("✅ โหลดสำเร็จ: ใช้ engine='python' + ftfy แก้ภาษาเพี้ยน")
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
            df_emp = df[df["รหัสพนักงาน"].astype(str) == emp_id]

            if df_emp.empty:
                st.warning("ไม่พบรหัสพนักงานนี้ในข้อมูล")
            else:
                all_tasks = []
                # ✅ เก็บหัวข้องานจากทุก row
                for row in df_emp["รายการงานที่ทำ"].dropna():
                    row = fix_text(row)
                    # ✅ แยกด้วย re.split ที่รองรับ comma และเว้นวรรค
                    tasks = [t.strip() for t in re.split(r'\s*,\s*', row) if t.strip()]
                    all_tasks.extend(tasks)

                # ✅ นับจำนวนหัวข้องาน
                count = Counter(all_tasks)

                st.subheader(f"พนักงานรหัส {emp_id} ทำงานทั้งหมด {sum(count.values())} ครั้ง")
                st.dataframe(
                    pd.DataFrame(count.items(), columns=["หัวข้องาน", "จำนวนครั้ง"])
                    .sort_values(by="จำนวนครั้ง", ascending=False)
                )
