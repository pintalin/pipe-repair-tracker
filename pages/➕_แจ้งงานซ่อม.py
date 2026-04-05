"""
➕ แจ้งงานซ่อมใหม่
"""
import streamlit as st
from datetime import datetime, date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (insert_record, send_line_notify, apply_mobile_style,
                   fetch_all, get_technician_names, CHANNELS,
                   fetch_technicians, insert_technician, update_technician)

st.set_page_config(page_title="➕ แจ้งซ่อม", page_icon="➕", layout="centered",
                   initial_sidebar_state="collapsed")
apply_mobile_style()

st.title("➕ แจ้งงานซ่อมใหม่")
st.caption("กริกข้อมูลแล้วกดบันทึก — ข้อมูลจะอัปเดตทันที")

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

# ─── โหลดรายชื่อพนักงาน ───
@st.cache_data(ttl=60)
def load_staff():
    names = get_technician_names(role_filter="ผู้รับเรื่อง")
    if not names or names == ["ไม่มีข้อมูล"]:
        return ["อโนทัย แก้วเมืองมา", "อรุณี คำปัญโญ", "พิกุล มงคลวิสุทธื์",
                "ศิริลักษณ์ สุหงษา", "อรัญญา กังวาล", "ชนัญชิดา เลขะผล", "อื่นๆ"]
    return names + ["อื่นๆ"]

with st.form("repair_form", clear_on_submit=True):
    st.subheader("📝 ข้อมูลงานซ่อม")

    job_id = st.text_input("เลขที่งาน", value=get_next_job_id(), disabled=True)
    repair_date = st.date_input("วันที่", value=date.today())
    repair_time = st.time_input("เวลา", value=datetime.now().time())

    st.divider()
    st.subheader("📡 ช่องทางการรับแจ้ง")
    channel = st.selectbox("รับแจ้งจาก *", CHANNELS)

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

    st.divider()
    st.subheader("👷 ผู้รับเรื่อง")
    staff_list = load_staff()
    assigned_to = st.selectbox("ผู้รับแจ้ง *", staff_list)

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
            "channel": channel,
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

            msg = (
                f"\n🔧 งานซ่อมใหม่ [{job_id}]\n"
                f"📡 ช่องทาง: {channel}\n"
                f"👤 ลูกค้า: {customer_name}\n"
                f"📞 โทร: {phone}\n"
                f"🛠 ประเภท: {repair_type}\n"
                f"📍 สถานที่: {location}\n"
                f"⚡ ความเร่งด่วน: {urgency}\n"
                f"👷 ผู้รับแจ้ง: {assigned_to}\n"
                f"🕐 เวลา: {repair_time.strftime('%H:%M')}"
            )
            send_line_notify(msg)
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

# ════════════════════════════════════════
# จัดการรายชื่อผู้รับเรื่อง
# ════════════════════════════════════════
st.divider()
with st.expander("👥 จัดการรายชื่อผู้รับเรื่อง (เพิ่ม/ปิดใช้งาน)"):

    @st.cache_data(ttl=30)
    def load_reception_staff():
        return fetch_technicians(active_only=False)

    all_staff = load_reception_staff()
    reception = [t for t in all_staff if t.get("role") == "ผู้รับเรื่อง"]
    active_r   = [t for t in reception if t.get("active", True)]
    inactive_r = [t for t in reception if not t.get("active", True)]

    st.write(f"**พนักงานผู้รับเรื่อง ({len(active_r)} คน)**")
    for tech in active_r:
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.write(f"**{tech['name']}**")
        c2.caption(tech.get("phone", ""))
        if c3.button("🚫", key=f"del_r_{tech['id']}", help="ปิดใช้งาน"):
            ok, _ = update_technician(tech["id"], {"active": False})
            if ok:
                st.cache_data.clear()
                st.rerun()

    if inactive_r:
        with st.expander(f"พนักงานที่ปิดใช้งาน ({len(inactive_r)} คน)"):
            for tech in inactive_r:
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"~~{tech['name']}~~")
                c2.caption(tech.get("phone", ""))
                if c3.button("✅", key=f"act_r_{tech['id']}", help="เปิดใช้งาน"):
                    ok, _ = update_technician(tech["id"], {"active": True})
                    if ok:
                        st.cache_data.clear()
                        st.rerun()

    st.divider()
    st.write("**➕ เพิ่มพนักงานผู้รับเรื่องใหม่**")
    with st.form("add_reception_form", clear_on_submit=True):
        new_name  = st.text_input("ชื่อ-นามสกุล *", placeholder="ชื่อพนักงาน")
        new_phone = st.text_input("เบอร์โทร", placeholder="0812345678")
        add_btn = st.form_submit_button("➕ เพิ่มพนักงาน", use_container_width=True, type="primary")

    if add_btn:
        if not new_name.strip():
            st.error("❌ กรุณากรอกชื่อ-นามสกุล")
        else:
            ok, result = insert_technician({
                "name": new_name.strip(),
                "phone": new_phone.strip(),
                "role": "ผู้รับเรื่อง",
                "active": True,
            })
            if ok:
                st.success(f"✅ เพิ่ม **{new_name}** เรียบร้อยแล้ว!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ เพิ่มไม่สำเร็จ: {result}")

col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🏠 หน้าหลัก", use_container_width=True):
        st.switch_page("🏠_หน้าหลัก.py")
with col_nav2:
    if st.button("🔧 จัดการช่าง", use_container_width=True):
        st.switch_page("pages/🔧_จัดการช่าง.py")
