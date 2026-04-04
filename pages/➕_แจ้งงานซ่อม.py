"""
➕ แจ้งงานซ่อมใหม่
"""
import streamlit as st
from datetime import datetime, date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import insert_record, send_line_notify, apply_mobile_style, fetch_all

st.set_page_config(page_title="➕ แจ้งซ่อม", page_icon="➕", layout="centered",
                   initial_sidebar_state="collapsed")
apply_mobile_style()

st.title("➕ แจ้งงานซ่อมใหม่")
st.caption("กรอกข้อมูลแล้วกดบันทึก — ข้อมูลจะอัปเดตทันที")

# ─── สร้าง Job ID อัตโนมัติ ───
@st.cache_data(ttl=10)
def get_next_job_id():
    rows = fetch_all()
    if not rows:
        return "N0001"
    ids = [r.get("job_id","N0000") for r in rows if r.get("job_id","").startswith("N")]
    nums = []
    for i in ids:
        try: nums.append(int(i[1:]))
        except: pass
    next_n = (max(nums) + 1) if nums else 1
    return f"N{next_n:04d}"

with st.form("repair_form", clear_on_submit=True):
    st.subheader("📝 ข้อมูลงานซ่อม")

    job_id = st.text_input("เลขที่งาน", value=get_next_job_id(), disabled=True)
    repair_date = st.date_input("วันที่", value=date.today())
    repair_time = st.time_input("เวลา", value=datetime.now().time())

    st.divider()
    st.subheader("👤 ข้อมูลลูกค้า")
    customer_name = st.text_input("ชื่อลูกค้า *", placeholder="ชื่อ-นามสกุล")
    phone = st.text_input("เบอร์โทรศัพท์ *", placeholder="0812345678")

    st.divider()
    st.subheader("🔧 รายละเอียดงาน")
    repair_type = st.selectbox("ประเภทงานซ่อม *", [
        "ท่อแตก/รั่ว", "ท่อเมนรั่ว", "น้ำไม่ไหล", "น้ำไหลอ่อน",
        "มาตรวัดน้ำเสีย", "มิเตอร์โดนตัด/หาย", "อื่นๆ"
    ])
    location = st.text_input("สถานที่ *", placeholder="บ้านเลขที่ / ถนน / ตำบล")

    assigned_to = st.selectbox("ผู้รับแจ้ง *", [
        "อโนทัย แก้วเมืองมา", "อรุณี คำปัญโญ", "พิกุล มงคลวิสุทธื์",
        "ศิริลักษณ์ สุหงษา", "อรัญญา กังวาล", "ชนัญชิดา เลขะผล", "อื่นๆ"
    ])

    urgency = st.radio("ความเร่งด่วน", ["เร่งด่วน", "ปกติ"], horizontal=True)
    notes = st.text_area("หมายเหตุ", placeholder="รายละเอียดเพิ่มเติม (ถ้ามี)")

    submitted = st.form_submit_button("💾 บันทึกงานซ่อม", use_container_width=True, type="primary")

if submitted:
    if not customer_name or not phone or not location:
        st.error("❌ กรุณากรอกข้อมูลที่มี * ให้ครบถ้วน")
    else:
        record = {
            "job_id": job_id,
            "date": str(repair_date),
            "time": repair_time.strftime("%H:%M"),
            "customer_name": customer_name.strip(),
            "phone": phone.strip(),
            "repair_type": repair_type,
            "location": location.strip(),
            "assigned_to": assigned_to,
            "urgency": urgency,
            "notes": notes.strip() if notes else None,
            "status": "รอดำเนินการ",
            "recorded_at": datetime.now().isoformat(),
        }

        ok, result = insert_record(record)
        if ok:
            st.success(f"✅ บันทึกงาน **{job_id}** สำเร็จ!")
            st.balloons()

            # แจ้ง LINE
            msg = (
                f"\n🔧 งานซ่อมใหม่ [{job_id}]\n"
                f"👤 ลูกค้า: {customer_name}\n"
                f"📞 โทร: {phone}\n"
                f"🛠 ประเภท: {repair_type}\n"
                f"📍 สถานที่: {location}\n"
                f"⚡ ความเร่งด่วน: {urgency}\n"
                f"👷 ผู้รับแจ้ง: {assigned_to}\n"
                f"🕐 เวลา: {repair_time.strftime('%H:%M')}"
            )
            line_ok, _ = send_line_notify(msg)

            if line_ok:
                st.info("📲 ส่งแจ้งเตือน LINE สำเร็จ")

            st.cache_data.clear()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ แจ้งงานใหม่อีก"):
                    st.rerun()
            with col2:
                if st.button("🏠 กลับหน้าหลัก"):
                    st.switch_page("🏠_หน้าหลัก.py")
        else:
            st.error(f"❌ บันทึกไม่สำเร็จ: {result}")
