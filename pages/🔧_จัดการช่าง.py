"""
🔧 จัดการช่าง — จ่ายงาน ติดตาม จัดการพนักงาน
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
# TAB 1: จ่ายงานให้ช่าง (มีพนักงานบริการตรวจสอบก่อน)
# ══════════════════════════════════════════
with tab1:
    st.subheader("🛠 จ่ายงานให้ช่างซ่อม")
    st.caption("เลือกงาน → เลือกพนักงานบริการออกตรวจ → เลือกช่าง/บริษัทซ่อม → บันทึก")

    @st.cache_data(ttl=15)
    def load_unassigned():
        rows = fetch_all()
        return [r for r in rows if not r.get("technician") and r.get("status") != "เสร็จสิ้น"]

    @st.cache_data(ttl=60)
    def load_service_staff():
        techs = fetch_technicians(active_only=True)
        staff = [t for t in techs if t.get("role") == "พนักงานบริการ"]
        return [t["name"] for t in staff] if staff else []

    @st.cache_data(ttl=60)
    def load_repair_techs():
        techs = fetch_technicians(active_only=True)
        repair = [t for t in techs if t.get("role") == "ช่างซ่อม"]
        return [t["name"] for t in repair] if repair else []

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
            st.markdown(f"[🗺️ ดูแผนที่ Google Maps]({maps_url})")

            channel = selected.get('channel', '-')
            st.write(f"**📡 ช่องทางรับแจ้ง:** {channel}")
            urgency = selected.get('urgency', '')
            badge = "🔴 เร่งด่วน" if urgency == "เร่งด่วน" else "🟡 ปกติ"
            st.write(f"**ความเร่งด่วน:** {badge}")
            st.write(f"**ผู้รับแจ้ง:** {selected.get('assigned_to','')}")

        st.divider()

        # ── Step 1: เลือกพนักงานบริการออกตรวจ ──
        st.markdown("#### 👷 Step 1 — พนักงานบริการออกตรวจสอบหน้างาน")
        service_names = load_service_staff()

        if not service_names:
            st.warning("⚠️ ยังไม่มีรายชื่อพนักงานบริการ กรุณาเพิ่มในแท็บ 'จัดการพนักงาน' ก่อน")
            selected_service = None
        else:
            selected_service = st.selectbox("👷 เลือกพนักงานบริการ *", service_names, key="select_service")

        # ── Step 2: เลือกช่าง/บริษัทซ่อม ──
        st.markdown("#### 🔨 Step 2 — พนักงานบริการแจ้งช่าง/บริษัทเข้าซ่อม")
        tech_names = load_repair_techs()

        if not tech_names:
            st.warning("⚠️ ยังไม่มีรายชื่อช่างซ่อม กรุณาเพิ่มในแท็บ 'จัดการพนักงาน' ก่อน")
            selected_tech = None
        else:
            selected_tech = st.selectbox("🔧 เลือกช่าง/บริษัทซ่อม *", tech_names, key="select_tech")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 จ่ายงาน", use_container_width=True, type="primary"):
                if not selected_service:
                    st.error("❌ กรุณาเลือกพนักงานบริการก่อน")
                elif not selected_tech:
                    st.error("❌ กรุณาเลือกช่าง/บริษัทซ่อม")
                else:
                    ok, _ = update_record(selected["id"], {
                        "service_staff": selected_service,
                        "technician": selected_tech,
                        "status": "กำลังดำเนินการ"
                    })
                    if ok:
                        st.success(f"✅ จ่ายงาน **{selected.get('job_id','')}** สำเร็จ!")
                        msg = (
                            f"\n🔨 จ่ายงาน [{selected.get('job_id','')}]\n"
                            f"👷 พนักงานบริการ: {selected_service}\n"
                            f"🔧 ช่าง/บริษัทซ่อม: {selected_tech}\n"
                            f"👤 ลูกค้า: {selected.get('customer_name','')}\n"
                            f"📞 โทร: {selected.get('phone','')}\n"
                            f"🛠 ประเภท: {selected.get('repair_type','')}\n"
                            f"📍 สถานที่: {location}\n"
                            f"⚠️ ความเร่งด่วน: {urgency}"
                        )
                        send_line_notify(msg)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ บันทึกไม่สำเร็จ กรุณาลองใหม่")
        with col2:
            if st.button("🏠 หน้าหลัก", use_container_width=True):
                st.switch_page("🏠_หน้าหลัก.py")


# ══════════════════════════════════════════
# TAB 2: ติดตามสถานะงาน
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
            status  = row.get("status", "")
            urgency = row.get("urgency", "")
            emoji   = "✅" if status == "เสร็จสิ้น" else "🔨"
            urg     = "🔴" if urgency == "เร่งด่วน" else "🟡"

            with st.expander(f"{emoji} {row.get('job_id','')} — {row.get('customer_name','')} {urg}"):
                if row.get("service_staff"):
                    st.write(f"**👷 พนักงานบริการ:** {row.get('service_staff','')}")
                st.write(f"**🔧 ช่าง/บริษัทซ่อม:** {row.get('technician','')}")
                st.write(f"**ประเภท:** {row.get('repair_type','')}")
                location = row.get('location', '')
                st.write(f"**📍 สถานที่:** {location}")
                if location:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"
                    st.markdown(f"[🗺️ แผนที่]({maps_url})")
                st.write(f"**ช่องทาง:** {row.get('channel', '-')}")
                st.write(f"**สถานะ:** {status}  |  **เร่งด่วน:** {urgency}")

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

    # ─── แยกตาม role ───
    roles_order = ["พนักงานบริการ", "ช่างซ่อม", "ผู้รับเรื่อง"]
    role_emojis = {"พนักงานบริการ": "👷", "ช่างซ่อม": "🔧", "ผู้รับเรื่อง": "📞"}

    active_staff   = [t for t in all_staff if t.get("active", True)]
    inactive_staff = [t for t in all_staff if not t.get("active", True)]

    st.write(f"**พนักงานที่ใช้งานอยู่: {len(active_staff)} คน**")

    for role in roles_order:
        role_members = [t for t in active_staff if t.get("role") == role]
        if not role_members:
            continue
        st.markdown(f"**{role_emojis.get(role,'')} {role}**")
        for tech in role_members:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{tech['name']}**")
            col2.caption(tech.get("phone", ""))
            if col3.button("🗑️", key=f"del_{tech['id']}", help="ปิดการใช้งาน"):
                ok, _ = update_technician(tech["id"], {"active": False})
                if ok:
                    st.cache_data.clear()
                    st.rerun()

    # แสดงพนักงานที่ไม่อยู่ใน roles_order
    other_active = [t for t in active_staff if t.get("role") not in roles_order]
    if other_active:
        st.markdown("**📋 อื่นๆ**")
        for tech in other_active:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{tech['name']}**")
            col2.caption(tech.get("role", "-"))
            if col3.button("🗑️", key=f"del_o_{tech['id']}", help="ปิดการใช้งาน"):
                ok, _ = update_technician(tech["id"], {"active": False})
                if ok:
                    st.cache_data.clear()
                    st.rerun()

    if inactive_staff:
        with st.expander(f"พนักงานที่ปิดใช้งาน ({len(inactive_staff)} คน)"):
            for tech in inactive_staff:
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"~~{tech['name']}~~")
                col2.caption(tech.get("role", "-"))
                if col3.button("✅", key=f"act_{tech['id']}", help="เปิดใช้งาน"):
                    ok, _ = update_technician(tech["id"], {"active": True})
                    if ok:
                        st.cache_data.clear()
                        st.rerun()

    st.divider()

    # ─── เพิ่มพนักงานใหม่ ───
    st.subheader("➕ เพิ่มพนักงานใหม่")
    with st.form("add_staff_form", clear_on_submit=True):
        new_name  = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อพนักงาน")
        new_phone = st.text_input("เบอร์โทรศัพท์", placeholder="0812345678")
        new_role  = st.selectbox("ตำแหน่ง", ["พนักงานบริการ", "ช่างซ่อม", "ผู้รับเรื่อง"])
        add_btn   = st.form_submit_button("➕ เพิ่มพนักงาน", use_container_width=True, type="primary")

    if add_btn:
        if not new_name.strip():
            st.error("❌ กรุณากรอกชื่อพนักงาน")
        else:
            ok, result = insert_technician({
                "name":   new_name.strip(),
                "phone":  new_phone.strip(),
                "role":   new_role,
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
