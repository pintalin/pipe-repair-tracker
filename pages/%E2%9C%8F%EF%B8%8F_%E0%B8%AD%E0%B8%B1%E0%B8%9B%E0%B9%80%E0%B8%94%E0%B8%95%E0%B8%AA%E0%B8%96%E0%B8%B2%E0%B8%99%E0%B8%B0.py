"""
✏️ อัปเดตสถานะงาน
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import fetch_all, update_record, send_line_notify, apply_mobile_style

st.set_page_config(page_title="✏️ อัปเดตสถานะ", page_icon="✏️", layout="centered",
                   initial_sidebar_state="collapsed")
apply_mobile_style()

st.title("✏️ อัปเดตสถานะงาน")
st.caption("เลือกงานที่ต้องการอัปเดตสถานะ")

# ─── โหลดรายการงานที่ยังไม่เสร็จ ───
@st.cache_data(ttl=15)
def load_pending():
    rows = fetch_all()
    return [r for r in rows if r.get("status") != "เสร็จสิ้น"]

jobs = load_pending()

if not jobs:
    st.success("🎉 ไม่มีงานค้างอยู่แล้ว! ทุกงานเสร็จสิ้นแล้ว")
    if st.button("🏠 กลับหน้าหลัก"):
        st.switch_page("🏠_หน้าหลัก.py")
    st.stop()

# ─── เลือกงาน ───
job_labels = {
    f"{r['job_id']} | {r.get('customer_name','')} | {r.get('repair_type','')} | {r.get('status','')}": r
    for r in jobs
}

selected_label = st.selectbox("🔎 เลือกงานที่ต้องการอัปเดต", list(job_labels.keys()))
selected = job_labels[selected_label]

# ─── แสดงรายละเอียดงาน ───
with st.expander("📄 รายละเอียดงาน", expanded=True):
    c1, c2 = st.columns(2)
    c1.write(f"**เลขที่:** {selected.get('job_id','')}")
    c2.write(f"**วันที่:** {str(selected.get('date',''))[:10]}")
    st.write(f"**ลูกค้า:** {selected.get('customer_name','')}  |  📞 {selected.get('phone','')}")
    st.write(f"**ประเภท:** {selected.get('repair_type','')}")
    st.write(f"**สถานที่:** {selected.get('location','')}")
    st.write(f"**ผู้รับแจ้ง:** {selected.get('assigned_to','')}")
    urgency = selected.get('urgency','')
    badge = "🔴 เร่งด่วน" if urgency == "เร่งด่วน" else "🟡 ปกติ"
    st.write(f"**ความเร่งด่วน:** {badge}")
    st.write(f"**สถานะปัจจุบัน:** {selected.get('status','')}")

st.divider()

# ─── ฟอร์มอัปเดต ───
st.subheader("🔄 อัปเดตสถานะ")

current_status = selected.get("status", "รอดำเนินการ")
status_options = ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น"]
current_idx = status_options.index(current_status) if current_status in status_options else 0

new_status = st.radio(
    "สถานะใหม่",
    status_options,
    index=current_idx,
    horizontal=False,
)

update_notes = st.text_area("หมายเหตุ (ถ้ามี)", placeholder="เช่น ซ่อมเสร็จ รอตรวจสอบ ฯลฯ")

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 บันทึก", use_container_width=True, type="primary"):
        if new_status == current_status:
            st.warning("⚠️ สถานะเหมือนเดิม ไม่มีการเปลี่ยนแปลง")
        else:
            update_data = {"status": new_status}
            if update_notes.strip():
                old_notes = selected.get("notes") or ""
                update_data["notes"] = f"{old_notes}\n[{datetime.now().strftime('%d/%m %H:%M')}] {update_notes.strip()}".strip()

            ok, result = update_record(selected["id"], update_data)

            if ok:
                st.success(f"✅ อัปเดตสถานะเป็น **{new_status}** สำเร็จ!")
                if new_status == "เสร็จสิ้น":
                    st.balloons()

                # แจ้ง LINE
                msg = (
                    f"\n🔄 อัปเดตสถานะ [{selected.get('job_id','')}]\n"
                    f"👤 {selected.get('customer_name','')} | {selected.get('repair_type','')}\n"
                    f"📍 {selected.get('location','')}\n"
                    f"📊 {current_status} → {new_status}\n"
                    f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )
                if update_notes:
                    msg += f"\n📝 {update_notes}"
                send_line_notify(msg)

                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ เกิดข้อผิดพลาด: {result}")

with col2:
    if st.button("🏠 หน้าหลัก", use_container_width=True):
        st.switch_page("🏠_หน้าหลัก.py")

# ─── รายการงานทั้งหมดที่รออยู่ ───
st.divider()
st.subheader(f"⏳ งานที่ยังค้างอยู่ ({len(jobs)} รายการ)")
for j in jobs:
    status_e = "🔨" if j.get("status") == "กำลังดำเนินการ" else "⏳"
    urg_e = "🔴" if j.get("urgency") == "เร่งด่วน" else "🟡"
    st.caption(f"{status_e}{urg_e} {j.get('job_id','')} — {j.get('customer_name','')} — {j.get('repair_type','')}")
