import streamlit as st
import pandas as pd
from collections import Counter

def read_google_sheet(sheet_url):
    # แปลง URL ธรรมดาให้เป็น CSV link
    if "/edit" in sheet_url:
        sheet_url = sheet_url.replace("/edit", "/export?format=csv")
    elif "gid=" in sheet_url:
        sheet_url = sheet_url.replace("/view?usp=sharing", "").replace("open?", "export?format=csv&")
    return pd.read_csv(sheet_url)

# UI ส่วนบน
st.title("📊 วิเคราะห์งานที่พนักงานทำ")
sheet_url = st.text_input("🔗 วางลิงก์ Google Sheet ที่แชร์ให้เข้าถึงได้ (Anyone with the link)")

if sheet_url:
    try:
        df = read_google_sheet(sheet_url)

        emp_id = st.text_input("🔍 ใส่รหัสพนักงานที่ต้องการค้นหา")

        if emp_id:
            df_emp = df[df["รหัสพนักงาน"] == emp_id]

            if df_emp.empty:
                st.warning("ไม่พบรหัสพนักงานนี้ในข้อมูล")
            else:
                # รวมหัวข้อจากรายการงานที่ทำ
                work_items = []
                for item in df_emp["รายการงานที่ทำ"]:
                    if pd.notna(item):
                        work_items.extend([i.strip() for i in item.split(',')])

                # นับจำนวนงานแต่ละประเภท
                count = Counter(work_items)

                # แสดงผล
                st.subheader(f"พนักงานรหัส {emp_id} ทำงานทั้งหมด {sum(count.values())} ครั้ง")
                st.dataframe(pd.DataFrame(count.items(), columns=["หัวข้องาน", "จำนวนครั้ง"]).sort_values(by="จำนวนครั้ง", ascending=False))

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
