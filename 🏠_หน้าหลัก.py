"""
ð  à¸«à¸à¹à¸²à¸«à¸¥à¸±à¸ â à¸à¸²à¸£à¸à¸£à¸°à¸à¸²à¸ªà¹à¸§à¸à¸ à¸¹à¸¡à¸´à¸ à¸²à¸à¸ªà¸²à¸à¸²à¸à¹à¸²à¸
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import (fetch_all, update_record, delete_record,
                   apply_mobile_style, get_technician_names, CHANNELS)

st.set_page_config(
    page_title="à¸à¸£à¸°à¸à¸²à¸à¹à¸²à¸",
    page_icon="ð§",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# âââ CSS âââ
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

# âââ Header âââ
st.markdown(f"""
<div class="org-header">
    <div class="org-name">à¸à¸²à¸£à¸à¸£à¸°à¸à¸²à¸ªà¹à¸§à¸à¸ à¸¹à¸¡à¸´à¸ à¸²à¸</div>
    <div class="org-branch">à¸ªà¸²à¸à¸²à¸à¹à¸²à¸</div>
    <div class="org-update">ð à¸­à¸±à¸à¹à¸à¸: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

apply_mobile_style()

# âââ session state âââ
for key, default in [
    ("view_status", None),
    ("edit_job", None),
    ("confirm_delete_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# âââ à¹à¸«à¸¥à¸à¸à¹à¸­à¸¡à¸¹à¸¥ âââ
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
    st.warning("à¹à¸¡à¹à¸à¸à¸à¹à¸­à¸¡à¸¹à¸¥à¸«à¸£à¸·à¸­à¹à¸à¸·à¹à¸­à¸¡à¸à¹à¸­à¹à¸¡à¹à¹à¸à¹")
    st.stop()

# âââ à¸à¸³à¸à¸§à¸à¸ªà¸à¸´à¸à¸´ âââ
today   = pd.Timestamp.now().normalize()
total   = len(df)
done    = len(df[df["status"] == "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸"]) if "status" in df.columns else 0
inprog  = len(df[df["status"] == "à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£"]) if "status" in df.columns else 0
waiting = len(df[df["status"] == "à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£"]) if "status" in df.columns else 0
urgent  = len(df[df["urgency"] == "à¹à¸£à¹à¸à¸à¹à¸§à¸"]) if "urgency" in df.columns else 0
today_n = len(df[df["date"] == today]) if "date" in df.columns else 0
no_tech = len(df[
    (df.get("technician", pd.Series(dtype=str)).isna() |
     (df.get("technician", pd.Series(dtype=str)) == "")) &
    (df["status"] != "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸")
]) if "status" in df.columns else 0

# âââ à¹à¸à¹à¸à¹à¸à¸·à¸­à¸à¸à¸²à¸à¹à¸¡à¹à¸¡à¸µà¸à¹à¸²à¸ âââ
if no_tech > 0:
    st.warning(f"â ï¸ à¸¡à¸µ **{no_tech}** à¸à¸²à¸à¸à¸µà¹à¸¢à¸±à¸à¹à¸¡à¹à¹à¸à¹à¸à¹à¸²à¸¢à¹à¸«à¹à¸à¹à¸²à¸")

# ââââââââââââââââââââââââââââââââââââââââââ
#  EDIT FORM (à¹à¸ªà¸à¸à¹à¸¡à¸·à¹à¸­à¸à¸à¸à¸¸à¹à¸¡à¹à¸à¹à¹à¸)
# ââââââââââââââââââââââââââââââââââââââââââ
if st.session_state.edit_job:
    job = st.session_state.edit_job
    st.subheader(f"âï¸ à¹à¸à¹à¹à¸à¸£à¸²à¸¢à¸à¸²à¸£ {job.get('job_id','')}")

    REPAIR_TYPES = [
        "à¸à¹à¸­à¹à¸à¸/à¸£à¸±à¹à¸§", "à¸à¹à¸­à¸à¸±à¸/à¸­à¸¸à¸à¸à¸±à¸", "à¸¡à¸´à¹à¸à¸­à¸£à¹à¸à¸³à¸£à¸¸à¸",
        "à¹à¸¡à¹à¸¡à¸µà¸à¹à¸³/à¸à¹à¸³à¸­à¹à¸­à¸", "à¸à¹à¸³à¸à¸¸à¹à¸/à¸à¹à¸³à¸¡à¸µà¸à¸¥à¸´à¹à¸", "à¸­à¸·à¹à¸à¹",
    ]
    STATUS_OPTS = ["à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£", "à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£", "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸"]
    URGENCY_OPTS = ["à¸à¸à¸à¸´", "à¹à¸£à¹à¸à¸à¹à¸§à¸"]

    with st.form("edit_form"):
        c1, c2 = st.columns(2)
        new_name  = c1.text_input("à¸à¸·à¹à¸­à¸¥à¸¹à¸à¸à¹à¸²", value=job.get("customer_name", ""))
        new_phone = c2.text_input("à¹à¸à¸­à¸£à¹à¹à¸à¸£", value=job.get("phone", ""))

        # à¸§à¸±à¸à¸à¸µà¹
        raw_date = job.get("date", "")
        try:
            init_date = date.fromisoformat(str(raw_date)[:10])
        except Exception:
            init_date = date.today()
        new_date = st.date_input("à¸§à¸±à¸à¸à¸µà¹à¹à¸à¹à¸", value=init_date)
        new_time = st.text_input("à¹à¸§à¸¥à¸²", value=job.get("time", ""))

        new_repair = st.selectbox(
            "à¸à¸£à¸°à¹à¸ à¸à¸à¸²à¸£à¸à¹à¸­à¸¡",
            REPAIR_TYPES,
            index=REPAIR_TYPES.index(job.get("repair_type", REPAIR_TYPES[0]))
                  if job.get("repair_type") in REPAIR_TYPES else 0,
        )
        new_channel = st.selectbox(
            "à¸à¹à¸­à¸à¸à¸²à¸à¸£à¸±à¸à¹à¸à¹à¸",
            CHANNELS,
            index=CHANNELS.index(job.get("channel", CHANNELS[0]))
                  if job.get("channel") in CHANNELS else 0,
        )
        new_location = st.text_area("à¸ªà¸à¸²à¸à¸à¸µà¹", value=job.get("location", ""))
        new_urgency = st.radio(
            "à¸à¸§à¸²à¸¡à¹à¸£à¹à¸à¸à¹à¸§à¸", URGENCY_OPTS,
            index=URGENCY_OPTS.index(job.get("urgency", "à¸à¸à¸à¸´"))
                  if job.get("urgency") in URGENCY_OPTS else 0,
            horizontal=True,
        )

        # à¸à¸¹à¹à¸£à¸±à¸à¹à¸à¹à¸ (service staff)
        service_names = get_technician_names(role_filter="service_staff")
        cur_service = job.get("assigned_to", "")
        srv_opts = service_names if service_names else ["à¹à¸¡à¹à¸¡à¸µà¸à¹à¸­à¸¡à¸¹à¸¥"]
        srv_idx = srv_opts.index(cur_service) if cur_service in srv_opts else 0
        new_service = st.selectbox("à¸à¸¹à¹à¸£à¸±à¸à¹à¸à¹à¸ (à¸à¸à¸±à¸à¸à¸²à¸à¸à¸£à¸´à¸à¸²à¸£)", srv_opts, index=srv_idx)

        # à¸à¹à¸²à¸à¸à¹à¸­à¸¡
        tech_names = get_technician_names(role_filter="technician")
        cur_tech = job.get("technician", "")
        tech_opts = ["(à¸¢à¸±à¸à¹à¸¡à¹à¸¡à¸­à¸à¸«à¸¡à¸²à¸¢)"] + (tech_names if tech_names else [])
        tech_idx = tech_opts.index(cur_tech) if cur_tech in tech_opts else 0
        new_tech = st.selectbox("à¸à¹à¸²à¸à¸à¹à¸­à¸¡", tech_opts, index=tech_idx)

        new_status = st.selectbox(
            "à¸ªà¸à¸²à¸à¸°",
            STATUS_OPTS,
            index=STATUS_OPTS.index(job.get("status", "à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£"))
                  if job.get("status") in STATUS_OPTS else 0,
        )
        new_notes = st.text_area("à¸«à¸¡à¸²à¸¢à¹à¸«à¸à¸¸", value=job.get("notes", "") or "")

        sb1, sb2 = st.columns(2)
        save_btn   = sb1.form_submit_button("ð¾ à¸à¸±à¸à¸à¸¶à¸à¸à¸²à¸£à¹à¸à¹à¹à¸", use_container_width=True, type="primary")
        cancel_btn = sb2.form_submit_button("â à¸¢à¸à¹à¸¥à¸´à¸", use_container_width=True)

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
            "technician": "" if new_tech == "(à¸¢à¸±à¸à¹à¸¡à¹à¸¡à¸­à¸à¸«à¸¡à¸²à¸¢)" else new_tech,
            "status": new_status,
            "notes": new_notes,
        }
        ok, _ = update_record(job["id"], patch)
        if ok:
            st.success("â à¹à¸à¹à¹à¸à¸£à¸²à¸¢à¸à¸²à¸£à¸ªà¸³à¹à¸£à¹à¸!")
            st.session_state.edit_job = None
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("â à¹à¸à¸´à¸à¸à¹à¸­à¸à¸´à¸à¸à¸¥à¸²à¸à¹à¸à¸à¸²à¸£à¸à¸±à¸à¸à¸¶à¸")

    if cancel_btn:
        st.session_state.edit_job = None
        st.rerun()

    st.stop()

# ââââââââââââââââââââââââââââââââââââââââââ
#  STAT CARDS
# ââââââââââââââââââââââââââââââââââââââââââ
st.markdown("#### ð à¸ªà¸£à¸¸à¸à¸ªà¸à¸²à¸à¸°à¸à¸²à¸à¸à¹à¸­à¸¡")

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
    <div class="stat-card" style="background:#E3F2FD;border-color:#1565C0;">
        <div class="stat-num" style="color:#1565C0;">{total}</div>
        <div class="stat-label" style="color:#1565C0;">ð à¸à¸±à¹à¸à¸«à¸¡à¸</div>
    </div>""", unsafe_allow_html=True)
    if st.button("à¸à¸¹à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸±à¹à¸à¸«à¸¡à¸ â", key="b_all", use_container_width=True):
        st.session_state.view_status = "à¸à¸±à¹à¸à¸«à¸¡à¸"
        st.rerun()
with c2:
    st.markdown(f"""
    <div class="stat-card" style="background:#EDE7F6;border-color:#4527A0;">
        <div class="stat-num" style="color:#4527A0;">{today_n}</div>
        <div class="stat-label" style="color:#4527A0;">ð à¹à¸à¹à¸à¸§à¸±à¸à¸à¸µà¹</div>
    </div>""", unsafe_allow_html=True)
    if st.button("à¸à¸¹à¸£à¸²à¸¢à¸à¸²à¸£à¸§à¸±à¸à¸à¸µà¹ â", key="b_today", use_container_width=True):
        st.session_state.view_status = "à¸§à¸±à¸à¸à¸µà¹"
        st.rerun()

c3, c4 = st.columns(2)
with c3:
    st.markdown(f"""
    <div class="stat-card" style="background:#FFF8E1;border-color:#F57F17;">
        <div class="stat-num" style="color:#F57F17;">{waiting}</div>
        <div class="stat-label" style="color:#F57F17;">â³ à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£</div>
    </div>""", unsafe_allow_html=True)
    if st.button("à¸à¸¹à¸£à¸²à¸¢à¸à¸²à¸£à¸£à¸­ â", key="b_wait", use_container_width=True):
        st.session_state.view_status = "à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£"
        st.rerun()
with c4:
    st.markdown(f"""
    <div class="stat-card" style="background:#E1F5FE;border-color:#0277BD;">
        <div class="stat-num" style="color:#0277BD;">{inprog}</div>
        <div class="stat-label" style="color:#0277BD;">ð¨ à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£</div>
    </div>""", unsafe_allow_html=True)
    if st.button("à¸à¸¹à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸³à¸¥à¸±à¸à¸à¹à¸­à¸¡ â", key="b_prog", use_container_width=True):
        st.session_state.view_status = "à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£"
        st.rerun()

c5, c6 = st.columns(2)
with c5:
    st.markdown(f"""
    <div class="stat-card" style="background:#E8F5E9;border-color:#1B5E20;">
        <div class="stat-num" style="color:#1B5E20;">{done}</div>
        <div class="stat-label" style="color:#1B5E20;">â à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸</div>
    </div>""", unsafe_allow_html=True)
    if st.button("à¸à¸¹à¸£à¸²à¸¢à¸à¸²à¸£à¹à¸ªà¸£à¹à¸ â", key="b_done", use_container_width=True):
        st.session_state.view_status = "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸"
        st.rerun()
with c6:
    st.markdown(f"""
    <div class="stat-card" style="background:#FFEBEE;border-color:#B71C1C;">
        <div class="stat-num" style="color:#B71C1C;">{urgent}</div>
        <div class="stat-label" style="color:#B71C1C;">â¡ à¹à¸£à¹à¸à¸à¹à¸§à¸</div>
    </div>""", unsafe_allow_html=True)
    if st.button("à¸à¸¹à¸£à¸²à¸¢à¸à¸²à¸£à¹à¸£à¹à¸à¸à¹à¸§à¸ â", key="b_urg", use_container_width=True):
        st.session_state.view_status = "à¹à¸£à¹à¸à¸à¹à¸§à¸"
        st.rerun()

# ââââââââââââââââââââââââââââââââââââââââââ
#  à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸²à¸ (à¹à¸¡à¸·à¹à¸­à¸à¸à¸à¸²à¸£à¹à¸)
# ââââââââââââââââââââââââââââââââââââââââââ
if st.session_state.view_status:
    st.divider()
    label = st.session_state.view_status
    st.subheader(f"ð à¸£à¸²à¸¢à¸à¸²à¸£: {label}")

    df_f = df.copy()
    if label == "à¸§à¸±à¸à¸à¸µà¹":
        df_f = df_f[df_f["date"] == today] if "date" in df_f.columns else df_f
    elif label == "à¹à¸£à¹à¸à¸à¹à¸§à¸":
        df_f = df_f[df_f["urgency"] == "à¹à¸£à¹à¸à¸à¹à¸§à¸"] if "urgency" in df_f.columns else df_f
    elif label != "à¸à¸±à¹à¸à¸«à¸¡à¸" and "status" in df_f.columns:
        df_f = df_f[df_f["status"] == label]

    st.caption(f"à¸à¸ {len(df_f)} à¸£à¸²à¸¢à¸à¸²à¸£")

    for _, row in df_f.iterrows():
        row_dict = row.to_dict()
        job_id   = row.get("job_id", "")
        rec_id   = row.get("id")
        status   = row.get("status", "")
        urgency  = row.get("urgency", "")
        emoji    = "â" if status == "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸" else ("ð¨" if status == "à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£" else "â³")
        urg_badge = "ð´" if urgency == "à¹à¸£à¹à¸à¸à¹à¸§à¸" else "ð¡"

        with st.expander(f"{emoji} {job_id} â {row.get('customer_name','')} {urg_badge}"):
            cols = st.columns(2)
            cols[0].write(f"**à¸§à¸±à¸à¸à¸µà¹:** {str(row.get('date',''))[:10]}")
            cols[1].write(f"**à¹à¸§à¸¥à¸²:** {row.get('time','')}")
            if row.get("channel"):
                st.write(f"**à¸à¹à¸­à¸à¸à¸²à¸:** {row.get('channel','')}")
            st.write(f"**à¸à¸£à¸°à¹à¸ à¸:** {row.get('repair_type','')}")
            location = row.get('location', '')
            st.write(f"**à¸ªà¸à¸²à¸à¸à¸µà¹:** {location}")
            if location:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={str(location).replace(' ', '+')}"
                st.markdown(f"[ðºï¸ à¸à¸¹à¹à¸à¸à¸à¸µà¹ Google Maps]({maps_url})")
            st.write(f"**à¸à¸¹à¹à¸£à¸±à¸à¹à¸à¹à¸:** {row.get('assigned_to','')}")
            if row.get("technician"):
                st.write(f"**à¸à¹à¸²à¸à¸à¹à¸­à¸¡:** {row.get('technician','')}")
            else:
                st.caption("â ï¸ à¸¢à¸±à¸à¹à¸¡à¹à¹à¸à¹à¸à¹à¸²à¸¢à¹à¸«à¹à¸à¹à¸²à¸")
            st.write(f"**à¸ªà¸à¸²à¸à¸°:** {status}  |  **à¹à¸£à¹à¸à¸à¹à¸§à¸:** {urgency}")
            if row.get("notes"):
                st.write(f"**à¸«à¸¡à¸²à¸¢à¹à¸«à¸à¸¸:** {row.get('notes')}")

            st.divider()

            # âââ à¸à¸¸à¹à¸¡à¹à¸à¹à¹à¸ / à¸¥à¸ âââ
            btn_e, btn_d = st.columns(2)
            if btn_e.button("âï¸ à¹à¸à¹à¹à¸", key=f"edit_{rec_id}", use_container_width=True):
                st.session_state.edit_job = row_dict
                st.session_state.view_status = None
                st.rerun()

            if btn_d.button("ðï¸ à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£", key=f"del_{rec_id}", use_container_width=True):
                st.session_state.confirm_delete_id = rec_id
                st.rerun()

            # âââ à¸¢à¸·à¸à¸¢à¸±à¸à¸à¸²à¸£à¸¥à¸ âââ
            if st.session_state.confirm_delete_id == rec_id:
                st.error(f"â ï¸ à¸¢à¸·à¸à¸¢à¸±à¸à¸à¸²à¸£à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£ **{job_id}** â à¹à¸¡à¹à¸ªà¸²à¸¡à¸²à¸£à¸à¸à¸¹à¹à¸à¸·à¸à¹à¸à¹!")
                cd1, cd2 = st.columns(2)
                if cd1.button("â à¸¢à¸·à¸à¸¢à¸±à¸à¸¥à¸", key=f"confirm_{rec_id}", use_container_width=True, type="primary"):
                    ok, _ = delete_record(rec_id)
                    if ok:
                        st.success("ðï¸ à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£à¸ªà¸³à¹à¸£à¹à¸!")
                        st.session_state.confirm_delete_id = None
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("â à¹à¸à¸´à¸à¸à¹à¸­à¸à¸´à¸à¸à¸¥à¸²à¸à¹à¸à¸à¸²à¸£à¸¥à¸")
                if cd2.button("â à¸¢à¸à¹à¸¥à¸´à¸", key=f"cancel_del_{rec_id}", use_container_width=True):
                    st.session_state.confirm_delete_id = None
                    st.rerun()

    if st.button("âï¸ à¸à¸´à¸à¸£à¸²à¸¢à¸à¸²à¸£", use_container_width=True, key="close_list"):
        st.session_state.view_status = None
        st.rerun()

st.divider()

# âââ à¹à¸¡à¸à¸¹à¸à¹à¸§à¸ âââ
st.subheader("â¡ à¹à¸¡à¸à¸¹à¸à¹à¸§à¸")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("â à¹à¸à¹à¸à¸à¸²à¸à¸à¹à¸­à¸¡à¹à¸«à¸¡à¹", use_container_width=True):
        st.switch_page("pages/â_à¹à¸à¹à¸à¸à¸²à¸à¸à¹à¸­à¸¡.py")
with col_b:
    if st.button("ð§ à¸à¸±à¸à¸à¸²à¸£à¸à¹à¸²à¸/à¸à¹à¸²à¸¢à¸à¸²à¸", use_container_width=True):
        st.switch_page("pages/ð§_à¸à¸±à¸à¸à¸²à¸£à¸à¹à¸²à¸.py")

col_c, col_d = st.columns(2)
with col_c:
    if st.button("âï¸ à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°", use_container_width=True):
        st.switch_page("pages/âï¸_à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°.py")
with col_d:
    if st.button("ð à¸£à¸²à¸¢à¸à¸²à¸", use_container_width=True):
        st.switch_page("pages/ð_à¸£à¸²à¸¢à¸à¸²à¸.py")

if st.button("ð à¸£à¸µà¹à¸à¸£à¸à¸à¹à¸­à¸¡à¸¹à¸¥", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
