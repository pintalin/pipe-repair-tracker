"""
🔧 จัดการช่าง — รับเรื่อง จ่ายงาน ติดตาม จัดการพนักงาน
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (
    fetch_all, update_record, fetch_technicians,
    insert_technician, update_technician,
    apply_mobile_style, send_line_notify
)

st.set_page_config(page_title="🔧 จัดการช่าง", page_icon="🔧", layout="centered",
                   initial_sidebar_state="collapsed")
apply_mobile_style()

st.title("🔧 จัดการงานบริการ")

tab1, tab2, tab3 = st.tabs(["🛠 จ่ายงานช่าง", "📋 ติดตามงาน", "👥 จัดการพนักงาน"])

# ══════════════════════════════════════════
# TAB 1: จ่ายงานให้ช่าง
# ══════════════════════════════════════════
with tab1:
    st.subheader("🛠 จ่ายงานให้ช่างซ่อม")
    st.caption("เลือกงานที่รอจ่าย → เลือกช่าง → บันทึก")

    @st.cache_data(ttl=15)
    def load_unassigned():
        rows = fetch_all()
        # งานที่ยังไม่ถูกจ่ายให้ช่าง และยังไม่เสร็จ
        return [r for r in rows if not r.get("technician") and r.get("status") != "เสร็จสิ้น"]

    @st.cache_data(ttl=60)
    def load_repair_techs():
        techs = fetch_technicians(active_only=True)
        # เอาเฉพาะช่างซ่อม (role = ช่างซ่อม)
        repair = [t for t in techs if t.get("role") == "ช่างซ่อม"]
        if not repair:
            repair = techs  # fallback: ใช้ทุกคน
        return repair

    jobs = load_unassigned()

    if not jobs:
        st.success("✅ ทุกงานถูกจ่ายให้ช่างแล้ว!")
    else:
        st.info(f"📋 มี **{len(jobs)}** งานที่รอจ่ายให้ช่าง")

        job_labels = {
            f"{r.get('job_id','')} | {r.get('customer_name','')} | {r.get('repair_type','')} | {r.get('urgency','')}": r
            for r in jobs
        }

        selected_label = st.selectbox("🔎 เลือกงาน", list(job_labels.keys()), key="assign_job")
        selected = job_labels[selected_label]

        # แสดงรายละเอียดงาน
        with st.expander("📄 รายละเอียดงาน", expanded=True):
            c1, c2 = st.columns(2)
            c1.write(f"**เลขที่:** {selected.get('job_id','')}")
            c2.write(f"**วันที่:** {str(selected.get('date',''))[:10]}")
            st.write(f"**ลูกค้า:** {selected.get('customer_name','')}  |  📞 {selected.get('phone','')}")
            st.write(f"**ประเภท:** {selected.get('repair_type','')}")

            location = selected.get('location', '')
            maps_url = f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"
            st.write(f"**📍 สถานที่:** {location}")
            st.markdown(f"[🗺️ ดูแผนที่ Google Maps]({maps_url})", unsafe_allow_html=False)

            channel = selected.get('channel', '-')
            st.write(f"**📡 ช่องทางรับแจ้ง:** {channel}")
            urgency = selected.get('urgency', '')
            badge = "🔴 เร่งด่วน" if urgency == "เร่งด่วน" else "🟡 ปกติ"
            st.write(f"**ความเร่งด่วน:** {badge}")
            st.write(f"**ผู้รับแจ้ง:** {selected.get('assigned_to','')}")

        # เลือกช่าง
        techs = load_repair_techs()
        tech_names = [t["name"] for t in techs]

        if not tech_names:
            st.warning("⚠️ ยังไม่มีรายชื่อช่าง กรุณาเพิ่มช่างในแท็บ 'จัดการพนักงาน' ก่อน")
        else:
            selected_tech = st.selectbox("👷 เลือกช่างซ่อม", tech_names, key="select_tech")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 จ่ายงาน", use_container_width=True, type="primary"):
                    ok, _ = update_record(selected["id"], {
                        "technician": selected_tech,
                        "status": "กำลังดำเนินการ"
                    })
                    if ok:
                        st.success(f"✅ จ่ายงาน {selected.get('job_id','')} ให้ **{selected_tech}** แล้ว!")
                        msg = (
                            f"\n🔨 จ่ายงานใหม่ [{selected.get('job_id','')}]\n"
                            f"👷 ช่าง: {selected_tech}\n"
                            f"👤 ลูกค้า: {selected.get('customer_name','')}\n"
                            f"🛠 ประเภท: {selected.get('repair_type','')}\n"
                            f"📍 สถานที่: {location}"
                        )
                        send_line_notify(msg)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ บันทึกไม่สำเร็จ")
            with col2:
                if st.button("🏠 หน้าหลัก", use_container_width=True):
                    st.switch_page("🏠_หน้าหลัก.py")


# ══════════════════════════════════════════
# TAB 2: ติดตามสถานะงานของช่าง
# ══════════════════════════════════════════
with tab2:
    st.subheader("📋 ติดตามสถานะงาน")

    @st.cache_data(ttl=20)
    def load_assigned_jobs():
        rows = fetch_all()
        return [r for r in rows if r.get("technician")]

    assigned_jobs = load_assigned_jobs()

    if not assigned_jobs:
        st.info("ยังไม่มีงานที่จ่ายให้ช่าง")
    else:
        # กรองตามช่าง
        all_techs_in_jobs = sorted(set(r.get("technician","") for r in assigned_jobs if r.get("technician")))
        filter_tech = st.selectbox("🔎 กรองตามช่าง", ["ทั้งหมด"] + all_techs_in_jobs, key="filter_tech")
        filter_status = st.selectbox("สถานะ", ["ทั้งหมด", "กำลังดำเนินการ", "เสร็จสิ้น"], key="filter_status2")

        filtered = assigned_jobs
        if filter_tech != "ทั้งหมด":
            filtered = [r for r in filtered if r.get("technician") == filter_tech]
        if filter_status != "ทั้งหมด":
            filtered = [r for r in filtered if r.get("status") == filter_status]

        st.caption(f"แสดง {len(filtered)} รายการ")

        for row in filtered:
            status = row.get("status", "")
            urgency = row.get("urgency", "")
            emoji = "✅" if status == "เสร็จสิ้น" else "🔨"
            urg = "🔴" if urgency == "เร่งด่วน" else "🟡"

            with st.expander(f"{emoji} {row.get('job_id','')} — {row.get('customer_name','')} {urg}"):
                st.write(f"**ช่าง:** {row.get('technician','')}")
                st.write(f"**ประเภท:** {row.get('repair_type','')}")
                location = row.get('location', '')
                st.write(f"**สถานที่:** {location}")
                if location:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"
                    st.markdown(f"[🗺️ แผนที่]({maps_url})")
                st.write(f"**ช่องทาง:** {row.get('channel', '-')}")
                st.write(f"**สถานะ:** {status}  |  **เร่งด่วน:** {urgency}")

                # อัปเดตสถานะด้านใน expander
                if status != "เสร็จสิ้น":
                    new_st = st.selectbox(
                        "เปลี่ยนสถานะ",
                        ["กำลังดำเนินการ", "เสร็จสิ้น"],
                        key=f"st_{row['id']}"
                    )
                    if st.button("บันทึก", key=f"save_{row['id']}"):
                        ok, _ = update_record(row["id"], {"status": new_st})
                        if ok:
                            st.success(f"✅ อัปเดตเป็น {new_st}")
                            st.cache_data.clear()
                            st.rerun()

        if st.button("🔄 รีเฟรช", use_container_width=True, key="refresh_tab2"):
            st.cache_data.clear()
            st.rerun()


# ══════════════════════════════════════════
# TAB 3: จัดการรายชื่อพนักงาน
# ══════════════════════════════════════════
with tab3:
    st.subheader("👥 จัดการรายชื่อพนักงาน")

    @st.cache_data(ttl=30)
    def load_all_techs():
        return fetch_technicians(active_only=False)

    all_staff = load_all_techs()

    # ─── รายชื่อปัจจุบัน ───
    active_staff = [t for t in all_staff if t.get("active", True)]
    inactive_staff = [t for t in all_staff if not t.get("active", True)]

    st.write(f"**พนักงานที่ใช้งานอยู่: {len(active_staff)} คน**")

    for tech in active_staff:
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(f"**{tech['name']}**")
        col2.caption(tech.get("role", "ช่างซ่อม"))
        if col3.button("🗑️", key=f"del_{tech['id']}", help="ปิดการใช้งาน"):
            ok, _ = update_technician(tech["id"], {"active": False})
            if ok:
                st.success(f"ปิดการใช้งาน {tech['name']} แล้ว")
                st.cache_data.clear()
                st.rerun()

    if inactive_staff:
        with st.expander(f"พนักงานที่ปิดใช้งาน ({len(inactive_staff)} คน)"):
            for tech in inactive_staff:
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"~~{tech['name']}~~")
                col2.caption(tech.get("role", "-"))
                if col3.button("✅", key=f"act_{tech['id']}", help="เปิดการใช้งาน"):
                    ok, _ = update_technician(tech["id"], {"active": True})
                    if ok:
                        st.success(f"เปิดการใช้งาน {tech['name']} แล้ว")
                        st.cache_data.clear()
                        st.rerun()

    st.divider()

    # ─── เพิ่มพนักงานใหม่ ───
    st.subheader("➕ เพิ่มพนักงานใหม่")
    with st.form("add_staff_form", clear_on_submit=True):
        new_name = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อพนักงาน")
        new_phone = st.text_input("เบอร์โทรศัพท์", placeholder="0812345678")
        new_role = st.selectbox("ตำแหน่ง", ["ผู้รับเรื่อง", "ช่างซ่อม"])

        add_btn = st.form_submit_button("➕ เพิ่มพนักงาน", use_container_width=True, type="primary")

    if add_btn:
        if not new_name.strip():
            st.error("❌ กรุณากรอกชื่อพนักงาน")
        else:
            ok, result = insert_technician({
                "name": new_name.strip(),
                "phone": new_phone.strip(),
                "role": new_role,
                "active": True,
            })
            if ok:
                st.success(f"✅ เพิ่ม **{new_name}** ({new_role}) สำเร็จ!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ เพิ่มไม่สำเร็จ: {result}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 รีเฟรช", use_container_width=True, key="refresh_tab3"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("🏠 หน้าหลัก", use_container_width=True, key="home_tab3"):
            st.switch_page("🏠_หน้าหลัก.py")
