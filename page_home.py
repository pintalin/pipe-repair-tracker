"""
🏠 หน้าหลัก — การประปาส่วนภูมิภาคสาขาน่าน
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import (fetch_all, update_record, delete_record,
                   apply_mobile_style, get_technician_names, CHANNELS)


# ─── CSS ───
st.markdown("""
<style>
h1:first-of-type { display: none; }

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

# ─── session state ───
for key, default in [
    ("view_status", None),
    ("edit_job", None),
    ("confirm_delete_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

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

# ─── แจ้งเตือนงานไม่มีช่าง ───
if no_tech > 0:
    st.warning(f"⚠️ มี **{no_tech}** งานที่ยังไม่ได้จ่ายให้ช่าง")

# ══════════════════════════════════════════
#  EDIT FORM (แสดงเมื่อกดปุ่มแก้ไข)
# ══════════════════════════════════════════
if st.session_state.edit_job:
    job = st.session_state.edit_job
    st.subheader(f"✏️ แก้ไขรายการ {job.get('job_id','')}")

    REPAIR_TYPES = [
        "ท่อแตก/รั่ว", "ท่อตัน/อุดตัน", "มิเตอร์ชำรุด",
        "ไม่มีน้ำ/น้ำอ่อน", "น้ำขุ่น/น้ำมีกลิ่น", "อื่นๆ",
    ]
    STATUS_OPTS = ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น"]
    URGENCY_OPTS = ["ปกติ", "เร่งด่วน"]

    with st.form("edit_form"):
        c1, c2 = st.columns(2)
        new_name  = c1.text_input("ชื่อลูกค้า", value=job.get("customer_name", ""))
        new_phone = c2.text_input("เบอร์โทร", value=job.get("phone", ""))

        # วันที่
        raw_date = job.get("date", "")
        try:
            init_date = date.fromisoformat(str(raw_date)[:10])
        except Exception:
            init_date = date.today()
        new_date = st.date_input("วันที่แจ้ง", value=init_date)
        new_time = st.text_input("เวลา", value=job.get("time", ""))

        new_repair = st.selectbox(
            "ประเภทการซ่อม",
            REPAIR_TYPES,
            index=REPAIR_TYPES.index(job.get("repair_type", REPAIR_TYPES[0]))
                  if job.get("repair_type") in REPAIR_TYPES else 0,
        )
        new_channel = st.selectbox(
            "ช่องทางรับแจ้ง",
            CHANNELS,
            index=CHANNELS.index(job.get("channel", CHANNELS[0]))
                  if job.get("channel") in CHANNELS else 0,
        )
        new_location = st.text_area("สถานที่", value=job.get("location", ""))
        new_urgency = st.radio(
            "ความเร่งด่วน", URGENCY_OPTS,
            index=URGENCY_OPTS.index(job.get("urgency", "ปกติ"))
                  if job.get("urgency") in URGENCY_OPTS else 0,
            horizontal=True,
        )

        # ผู้รับแจ้ง (service staff)
        service_names = get_technician_names(role_filter="service_staff")
        cur_service = job.get("assigned_to", "")
        srv_opts = service_names if service_names else ["ไม่มีข้อมูล"]
        srv_idx = srv_opts.index(cur_service) if cur_service in srv_opts else 0
        new_service = st.selectbox("ผู้รับแจ้ง (พนักงานบริการ)", srv_opts, index=srv_idx)

        # ช่างซ่อม
        tech_names = get_technician_names(role_filter="technician")
        cur_tech = job.get("technician", "")
        tech_opts = ["(ยังไม่มอบหมาย)"] + (tech_names if tech_names else [])
        tech_idx = tech_opts.index(cur_tech) if cur_tech in tech_opts else 0
        new_tech = st.selectbox("ช่างซ่อม", tech_opts, index=tech_idx)

        new_status = st.selectbox(
            "สถานะ",
            STATUS_OPTS,
            index=STATUS_OPTS.index(job.get("status", "รอดำเนินการ"))
                  if job.get("status") in STATUS_OPTS else 0,
        )
        new_notes = st.text_area("หมายเหตุ", value=job.get("notes", "") or "")

        sb1, sb2 = st.columns(2)
        save_btn   = sb1.form_submit_button("💾 บันทึกการแก้ไข", use_container_width=True, type="primary")
        cancel_btn = sb2.form_submit_button("❌ ยกเลิก", use_container_width=True)

    if save_btn:
        patch = {
            "customer_name": new_name,
            "phone": new_phone,
            "date": str(new_date),
            "time": new_time,
            "repair_type": new_repair,
            "channel": new_channel,
            "location": new_location,
            "urgency": new_urgency,
            "assigned_to": new_service,
            "technician": "" if new_tech == "(ยังไม่มอบหมาย)" else new_tech,
            "status": new_status,
            "notes": new_notes,
        }
        ok, _ = update_record(job["id"], patch)
        if ok:
            st.success("✅ แก้ไขรายการสำเร็จ!")
            st.session_state.edit_job = None
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("❌ เกิดข้อผิดพลาดในการบันทึก")

    if cancel_btn:
        st.session_state.edit_job = None
        st.rerun()

    st.stop()

# ══════════════════════════════════════════
#  STAT CARDS
# ══════════════════════════════════════════
st.markdown("#### 📊 สรุปสถานะงานซ่อม")

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

# ══════════════════════════════════════════
#  รายการงาน (เมื่อกดการ์ด)
# ══════════════════════════════════════════
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
        row_dict = row.to_dict()
        job_id   = row.get("job_id", "")
        rec_id   = row.get("id")
        status   = row.get("status", "")
        urgency  = row.get("urgency", "")
        emoji    = "✅" if status == "เสร็จสิ้น" else ("🔨" if status == "กำลังดำเนินการ" else "⏳")
        urg_badge = "🔴" if urgency == "เร่งด่วน" else "🟡"

        with st.expander(f"{emoji} {job_id} — {row.get('customer_name','')} {urg_badge}"):
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

            # ─── ระยะเวลา ───
            recorded = row.get("recorded_at")
            if recorded:
                try:
                    rec_dt = datetime.fromisoformat(str(recorded).replace("Z",""))
                    comp = row.get("completed_at")
                    start = row.get("started_at")
                    if comp:
                        comp_dt = datetime.fromisoformat(str(comp).replace("Z",""))
                        total_sec = (comp_dt - rec_dt).total_seconds()
                        th = int(total_sec // 3600); tm = int((total_sec % 3600) // 60)
                        st.success(f"⏱️ เสร็จภายใน {th} ชม. {tm} นาที")
                    else:
                        elapsed_sec = (datetime.now() - rec_dt).total_seconds()
                        eh = int(elapsed_sec // 3600); em = int((elapsed_sec % 3600) // 60)
                        clr = "🔴" if eh >= 24 else ("🟡" if eh >= 4 else "🟢")
                        st.caption(f"{clr} รับแจ้งมา {eh} ชม. {em} นาที")
                    if start:
                        st.caption(f"🔨 เริ่มซ่อม: {str(start)[:16].replace('T',' ')}")
                    if comp:
                        st.caption(f"✅ เสร็จ: {str(comp)[:16].replace('T',' ')}")
                except Exception:
                    pass

            st.divider()

            # ─── ปุ่มแก้ไข / ลบ ───
            btn_e, btn_d = st.columns(2)
            if btn_e.button("✏️ แก้ไข", key=f"edit_{rec_id}", use_container_width=True):
                st.session_state.edit_job = row_dict
                st.session_state.view_status = None
                st.rerun()

            if btn_d.button("🗑️ ลบรายการ", key=f"del_{rec_id}", use_container_width=True):
                st.session_state.confirm_delete_id = rec_id
                st.rerun()

            # ─── ยืนยันการลบ ───
            if st.session_state.confirm_delete_id == rec_id:
                st.error(f"⚠️ ยืนยันการลบรายการ **{job_id}** — ไม่สามารถกู้คืนได้!")
                cd1, cd2 = st.columns(2)
                if cd1.button("✅ ยืนยันลบ", key=f"confirm_{rec_id}", use_container_width=True, type="primary"):
                    ok, _ = delete_record(rec_id)
                    if ok:
                        st.success("🗑️ ลบรายการสำเร็จ!")
                        st.session_state.confirm_delete_id = None
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ เกิดข้อผิดพลาดในการลบ")
                if cd2.button("❌ ยกเลิก", key=f"cancel_del_{rec_id}", use_container_width=True):
                    st.session_state.confirm_delete_id = None
                    st.rerun()

    if st.button("✖️ ปิดรายการ", use_container_width=True, key="close_list"):
        st.session_state.view_status = None
        st.rerun()

st.divider()

# ─── เมนูด่วน ───
st.subheader("⚡ เมนูด่วน")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("➕ แจ้งงานซ่อมใหม่", use_container_width=True):
        st.switch_page("page_report_job.py")
with col_b:
    if st.button("🔧 จัดการช่าง/จ่ายงาน", use_container_width=True):
        st.switch_page("page_manage_tech.py")

col_c, col_d = st.columns(2)
with col_c:
    if st.button("✏️ อัปเดตสถานะ", use_container_width=True):
        st.switch_page("page_update_status.py")
with col_d:
    if st.button("📊 รายงาน", use_container_width=True):
        st.switch_page("page_report.py")

if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
