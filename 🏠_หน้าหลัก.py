"""
🏠 หน้าหลัก — การประปาส่วนภูมิภาคสาขาน่าน
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_all, apply_mobile_style

st.set_page_config(
    page_title="ประปาน่าน",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS: ลายน้ำ + หัวองค์กร + การ์ดสถานะ ───
st.markdown("""
<style>
/* ซ่อน title default ของ Streamlit */
h1:first-of-type { display: none; }

/* ลายน้ำโลโก้ประปา */
.stApp::before {
    content: '';
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 72vmin; height: 72vmin;
    background-image: url('https://upload.wikimedia.org/wikipedia/th/a/a0/Provincial_Waterworks_Authority_logo.png');
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    opacity: 0.07;
    pointer-events: none;
    z-index: 0;
}

/* Header องค์กร */
.org-header {
    text-align: center;
    padding: 3.5rem 0 0.2rem;
}
.org-name {
    font-size: 1.45rem;
    font-weight: 900;
    color: #0D47A1;
    line-height: 1.35;
    letter-spacing: 0.01em;
}
.org-branch {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1565C0;
    margin-top: 0.1rem;
}
.org-update {
    font-size: 0.8rem;
    color: #888;
    margin-top: 0.3rem;
}

/* การ์ดสถานะ */
.stat-card {
    border-radius: 16px;
    padding: 1.1rem 0.4rem 0.8rem;
    text-align: center;
    border: 2.5px solid;
    margin-bottom: 0.3rem;
}
.stat-num {
    font-size: 3rem;
    font-weight: 900;
    line-height: 1;
}
.stat-label {
    font-size: 0.95rem;
    font-weight: 700;
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ───
st.markdown(f"""
<div class="org-header">
    <div class="org-name">การประปาส่วนภูมิภาค</div>
    <div class="org-branch">สาขาน่าน</div>
    <div class="org-update">🕐 อัปเดต: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

apply_mobile_style()

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

# ─── คำนวณสถิติ ───
today   = pd.Timestamp.now().normalize()
total   = len(df)
done    = len(df[df["status"] == "เสร็จสิ้น"]) if "status" in df.columns else 0
inprog  = len(df[df["status"] == "กำลังดำเนินการ"]) if "status" in df.columns else 0
waiting = len(df[df["status"] == "รอดำเนินการ"]) if "status" in df.columns else 0
urgent  = len(df[df["urgency"] == "เร่งด่วน"]) if "urgency" in df.columns else 0
today_n = len(df[df["date"] == today]) if "date" in df.columns else 0
no_tech = len(df[
    (df.get("technician", pd.Series(dtype=str)).isna() |
     (df.get("technician", pd.Series(dtype=str)) == "")) &
    (df["status"] != "เสร็จสิ้น")
]) if "status" in df.columns else 0

# ─── session state ───
if "view_status" not in st.session_state:
    st.session_state.view_status = None

# ─── แจ้งเตือนงานไม่มีช่าง ───
if no_tech > 0:
    st.warning(f"⚠️ มี **{no_tech}** งานที่ยังไม่ได้จ่ายให้ช่าง")

st.markdown("#### 📊 สรุปสถานะงานซ่อม")

# ─── การ์ดแถว 1: ทั้งหมด / วันนี้ ───
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
    <div class="stat-card" style="background:#E3F2FD;border-color:#1565C0;">
        <div class="stat-num" style="color:#1565C0;">{total}</div>
        <div class="stat-label" style="color:#1565C0;">📋 ทั้งหมด</div>
    </div>""", unsafe_allow_html=True)
    if st.button("ดูรายการทั้งหมด →", key="b_all", use_container_width=True):
        st.session_state.view_status = "ทั้งหมด"
        st.rerun()
with c2:
    st.markdown(f"""
    <div class="stat-card" style="background:#EDE7F6;border-color:#4527A0;">
        <div class="stat-num" style="color:#4527A0;">{today_n}</div>
        <div class="stat-label" style="color:#4527A0;">📅 แจ้งวันนี้</div>
    </div>""", unsafe_allow_html=True)
    if st.button("ดูรายการวันนี้ →", key="b_today", use_container_width=True):
        st.session_state.view_status = "วันนี้"
        st.rerun()

# ─── การ์ดแถว 2: รอ / กำลังดำเนินการ ───
c3, c4 = st.columns(2)
with c3:
    st.markdown(f"""
    <div class="stat-card" style="background:#FFF8E1;border-color:#F57F17;">
        <div class="stat-num" style="color:#F57F17;">{waiting}</div>
        <div class="stat-label" style="color:#F57F17;">⏳ รอดำเนินการ</div>
    </div>""", unsafe_allow_html=True)
    if st.button("ดูรายการรอ →", key="b_wait", use_container_width=True):
        st.session_state.view_status = "รอดำเนินการ"
        st.rerun()
with c4:
    st.markdown(f"""
    <div class="stat-card" style="background:#E1F5FE;border-color:#0277BD;">
        <div class="stat-num" style="color:#0277BD;">{inprog}</div>
        <div class="stat-label" style="color:#0277BD;">🔨 กำลังดำเนินการ</div>
    </div>""", unsafe_allow_html=True)
    if st.button("ดูรายการกำลังซ่อม →", key="b_prog", use_container_width=True):
        st.session_state.view_status = "กำลังดำเนินการ"
        st.rerun()

# ─── การ์ดแถว 3: เสร็จ / เร่งด่วน ───
c5, c6 = st.columns(2)
with c5:
    st.markdown(f"""
    <div class="stat-card" style="background:#E8F5E9;border-color:#1B5E20;">
        <div class="stat-num" style="color:#1B5E20;">{done}</div>
        <div class="stat-label" style="color:#1B5E20;">✅ เสร็จสิ้น</div>
    </div>""", unsafe_allow_html=True)
    if st.button("ดูรายการเสร็จ →", key="b_done", use_container_width=True):
        st.session_state.view_status = "เสร็จสิ้น"
        st.rerun()
with c6:
    st.markdown(f"""
    <div class="stat-card" style="background:#FFEBEE;border-color:#B71C1C;">
        <div class="stat-num" style="color:#B71C1C;">{urgent}</div>
        <div class="stat-label" style="color:#B71C1C;">⚡ เร่งด่วน</div>
    </div>""", unsafe_allow_html=True)
    if st.button("ดูรายการเร่งด่วน →", key="b_urg", use_container_width=True):
        st.session_state.view_status = "เร่งด่วน"
        st.rerun()

# ─── แสดงรายการงานเมื่อกดการ์ด ───
if st.session_state.view_status:
    st.divider()
    label = st.session_state.view_status
    st.subheader(f"📋 รายการ: {label}")

    df_f = df.copy()
    if label == "วันนี้":
        df_f = df_f[df_f["date"] == today] if "date" in df_f.columns else df_f
    elif label == "เร่งด่วน":
        df_f = df_f[df_f["urgency"] == "เร่งด่วน"] if "urgency" in df_f.columns else df_f
    elif label != "ทั้งหมด" and "status" in df_f.columns:
        df_f = df_f[df_f["status"] == label]

    st.caption(f"พบ {len(df_f)} รายการ")

    for _, row in df_f.iterrows():
        status  = row.get("status", "")
        urgency = row.get("urgency", "")
        emoji   = "✅" if status == "เสร็จสิ้น" else ("🔨" if status == "กำลังดำเนินการ" else "⏳")
        urg_badge = "🔴" if urgency == "เร่งด่วน" else "🟡"

        with st.expander(f"{emoji} {row.get('job_id','')} — {row.get('customer_name','')} {urg_badge}"):
            cols = st.columns(2)
            cols[0].write(f"**วันที่:** {str(row.get('date',''))[:10]}")
            cols[1].write(f"**เวลา:** {row.get('time','')}")
            if row.get("channel"):
                st.write(f"**ช่องทาง:** {row.get('channel','')}")
            st.write(f"**ประเภท:** {row.get('repair_type','')}")
            location = row.get('location', '')
            st.write(f"**สถานที่:** {location}")
            if location:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={str(location).replace(' ', '+')}"
                st.markdown(f"[🗺️ ดูแผนที่ Google Maps]({maps_url})")
            st.write(f"**ผู้รับแจ้ง:** {row.get('assigned_to','')}")
            if row.get("technician"):
                st.write(f"**ช่างซ่อม:** {row.get('technician','')}")
            else:
                st.caption("⚠️ ยังไม่ได้จ่ายให้ช่าง")
            st.write(f"**สถานะ:** {status}  |  **เร่งด่วน:** {urgency}")
            if row.get("notes"):
                st.write(f"**หมายเหตุ:** {row.get('notes')}")

    if st.button("✖️ ปิดรายการ", use_container_width=True, key="close_list"):
        st.session_state.view_status = None
        st.rerun()

st.divider()

# ─── เมนูด่วน ───
st.subheader("⚡ เมนูด่วน")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("➕ แจ้งงานซ่อมใหม่", use_container_width=True):
        st.switch_page("pages/➕_แจ้งงานซ่อม.py")
with col_b:
    if st.button("🔧 จัดการช่าง/จ่ายงาน", use_container_width=True):
        st.switch_page("pages/🔧_จัดการช่าง.py")

col_c, col_d = st.columns(2)
with col_c:
    if st.button("✏️ อัปเดตสถานะ", use_container_width=True):
        st.switch_page("pages/✏️_อัปเดตสถานะ.py")
with col_d:
    if st.button("📊 รายงาน", use_container_width=True):
        st.switch_page("pages/📊_รายงาน.py")

if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
