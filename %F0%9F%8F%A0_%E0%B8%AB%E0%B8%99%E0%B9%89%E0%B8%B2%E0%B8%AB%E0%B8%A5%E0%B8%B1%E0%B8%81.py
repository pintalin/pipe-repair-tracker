"""
🏠 หน้าหลัก — Dashboard
Pipe Repair Tracker Mobile App
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_all, apply_mobile_style

st.set_page_config(
    page_title="🔧 Pipe Repair",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)
apply_mobile_style()

# ─── Header ───
st.title("🔧 Pipe Repair Tracker")
st.caption(f"อัปเดต: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ─── โหลดข้อมูล ───
@st.cache_data(ttl=30)
def load_data():
    rows = fetch_all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "recorded_at" in df.columns:
        df["recorded_at"] = pd.to_datetime(df["recorded_at"], errors="coerce")
    return df

df = load_data()

if df.empty:
    st.warning("ไม่พบข้อมูลหรือเชื่อมต่อไม่ได้")
    st.stop()

# ─── Metrics ───
today = pd.Timestamp.now().normalize()
total = len(df)
done  = len(df[df["status"] == "เสร็จสิ้น"]) if "status" in df.columns else 0
inprog = len(df[df["status"] == "กำลังดำเนินการ"]) if "status" in df.columns else 0
waiting = len(df[df["status"] == "รอดำเนินการ"]) if "status" in df.columns else 0
urgent = len(df[df["urgency"] == "เร่งด่วน"]) if "urgency" in df.columns else 0
today_n = len(df[df["date"] == today]) if "date" in df.columns else 0

c1, c2 = st.columns(2)
c1.metric("📋 ทั้งหมด", f"{total}")
c2.metric("📅 วันนี้", f"{today_n}")
c3, c4 = st.columns(2)
c3.metric("✅ เสร็จสิ้น", f"{done}")
c4.metric("⚡ เร่งด่วน", f"{urgent}")
c5, c6 = st.columns(2)
c5.metric("🔨 กำลังดำเนินการ", f"{inprog}")
c6.metric("⏳ รอดำเนินการ", f"{waiting}")

st.divider()

# ─── ตัวกรองและค้นหา ───
st.subheader("🔍 ค้นหาและกรอง")
search = st.text_input("ค้นหา", placeholder="ชื่อลูกค้า / สถานที่ / เลขที่")
status_filter = st.selectbox("สถานะ", ["ทั้งหมด", "รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น"])

df_f = df.copy()
if search:
    mask = df_f.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
    df_f = df_f[mask]
if status_filter != "ทั้งหมด" and "status" in df_f.columns:
    df_f = df_f[df_f["status"] == status_filter]

# ─── รายการงาน ───
st.subheader(f"📋 รายการงาน ({len(df_f)} รายการ)")

for _, row in df_f.iterrows():
    status = row.get("status", "")
    urgency = row.get("urgency", "")
    emoji = "✅" if status == "เสร็จสิ้น" else ("🔨" if status == "กำลังดำเนินการ" else "⏳")
    urg_badge = "🔴" if urgency == "เร่งด่วน" else "🟡"

    with st.expander(f"{emoji} {row.get('job_id','')} — {row.get('customer_name','')} {urg_badge}"):
        cols = st.columns(2)
        cols[0].write(f"**วันที่:** {str(row.get('date',''))[:10]}")
        cols[1].write(f"**เวลา:** {row.get('time','')}")
        st.write(f"**ประเภท:** {row.get('repair_type','')}")
        st.write(f"**สถานที่:** {row.get('location','')}")
        st.write(f"**ผู้รับแจ้ง:** {row.get('assigned_to','')}")
        st.write(f"**สถานะ:** {status}  |  **เร่งด่วน:** {urgency}")
        if row.get("notes"):
            st.write(f"**หมายเหตุ:** {row.get('notes')}")

st.divider()

# ─── ปุ่มลัด ───
st.subheader("⚡ เมนูด่วน")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("➕ แจ้งงานซ่อมใหม่", use_container_width=True):
        st.switch_page("pages/➕_แจ้งงานซ่อม.py")
with col_b:
    if st.button("✏️ อัปเดตสถานะ", use_container_width=True):
        st.switch_page("pages/✏️_อัปเดตสถานะ.py")

# ─── Auto Refresh ───
if st.button("🔄 รีเฟรช", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
