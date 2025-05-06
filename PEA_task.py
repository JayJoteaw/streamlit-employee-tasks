import pandas as pd
import gspread
from google.auth import default

# ลิงค์ของ Google Sheets ที่ต้องการ
sheet_url = "https://docs.google.com/spreadsheets/d/your_spreadsheet_id_here"

# เชื่อมต่อกับ Google Sheets
gc = gspread.service_account(filename='credentials.json')  # ใช้ไฟล์ credentials ของ Google API
worksheet = gc.open_by_url(sheet_url).sheet1

# ดึงข้อมูลทั้งหมดจาก Google Sheets
data = worksheet.get_all_values()

# สร้าง DataFrame โดยให้แถวที่ 1 เป็น header และข้อมูลจากแถวที่ 2 เป็นต้นไป
df = pd.DataFrame(data[1:], columns=data[0])

# ทดสอบการแสดงผลข้อมูล
st.write(df)

# ข้อมูลจาก DataFrame
emp_id = st.text_input('ใส่รหัสพนักงานที่ต้องการค้นหา')

# ค้นหาข้อมูลของพนักงานที่กรอก
df_emp = df[df['รหัสพนักงาน'] == emp_id]

# แสดงข้อมูลของพนักงาน
if not df_emp.empty:
    st.write(f"ข้อมูลของพนักงานรหัส {emp_id}:")
    st.write(df_emp)
else:
    st.write(f"ไม่พบข้อมูลพนักงานรหัส {emp_id}")
