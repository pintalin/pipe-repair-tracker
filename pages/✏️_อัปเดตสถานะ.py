"""
âï¸ à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°à¸à¸²à¸
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import fetch_all, update_record, delete_record, send_line_notify, apply_mobile_style

st.set_page_config(page_title="âï¸ à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°", page_icon="âï¸", layout="centered",
                   initial_sidebar_state="collapsed")
apply_mobile_style()

st.title("âï¸ à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°à¸à¸²à¸")
st.caption("à¹à¸¥à¸·à¸­à¸à¸à¸²à¸à¸à¸µà¹à¸à¹à¸­à¸à¸à¸²à¸£à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°")

# âââ session state âââ
if "confirm_delete_status" not in st.session_state:
    st.session_state.confirm_delete_status = False

# âââ à¹à¸«à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸²à¸à¸à¸µà¹à¸¢à¸±à¸à¹à¸¡à¹à¹à¸ªà¸£à¹à¸ âââ
@st.cache_data(ttl=15)
def load_pending():
    rows = fetch_all()
    return [r for r in rows if r.get("status") != "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸"]

jobs = load_pending()

if not jobs:
    st.success("ð à¹à¸¡à¹à¸¡à¸µà¸à¸²à¸à¸à¹à¸²à¸à¸­à¸¢à¸¹à¹à¹à¸¥à¹à¸§! à¸à¸¸à¸à¸à¸²à¸à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸à¹à¸¥à¹à¸§")
    if st.button("ð  à¸à¸¥à¸±à¸à¸«à¸à¹à¸²à¸«à¸¥à¸±à¸"):
        st.switch_page("ð _à¸«à¸à¹à¸²à¸«à¸¥à¸±à¸.py")
    st.stop()

# âââ à¹à¸¥à¸·à¸­à¸à¸à¸²à¸ âââ
job_labels = {
    f"{r['job_id']} | {r.get('customer_name','')} | {r.get('repair_type','')} | {r.get('status','')}": r
    for r in jobs
}

selected_label = st.selectbox("ð à¹à¸¥à¸·à¸­à¸à¸à¸²à¸à¸à¸µà¹à¸à¹à¸­à¸à¸à¸²à¸£à¸­à¸±à¸à¹à¸à¸", list(job_labels.keys()))
selected = job_labels[selected_label]

# âââ à¹à¸ªà¸à¸à¸£à¸²à¸¢à¸¥à¸°à¹à¸­à¸µà¸¢à¸à¸à¸²à¸ âââ
with st.expander("ð à¸£à¸²à¸¢à¸¥à¸°à¹à¸­à¸µà¸¢à¸à¸à¸²à¸", expanded=True):
    c1, c2 = st.columns(2)
    c1.write(f"**à¹à¸¥à¸à¸à¸µà¹:** {selected.get('job_id','')}")
    c2.write(f"**à¸§à¸±à¸à¸à¸µà¹:** {str(selected.get('date',''))[:10]}")
    st.write(f"**à¸¥à¸¹à¸à¸à¹à¸²:** {selected.get('customer_name','')}  |  ð {selected.get('phone','')}")
    st.write(f"**à¸à¸£à¸°à¹à¸ à¸:** {selected.get('repair_type','')}")
    st.write(f"**à¸ªà¸à¸²à¸à¸à¸µà¹:** {selected.get('location','')}")
    st.write(f"**à¸à¸¹à¹à¸£à¸±à¸à¹à¸à¹à¸:** {selected.get('assigned_to','')}")
    if selected.get('technician'):
        st.write(f"**à¸à¹à¸²à¸à¸à¹à¸­à¸¡:** {selected.get('technician','')}")
    urgency = selected.get('urgency','')
    badge = "ð´ à¹à¸£à¹à¸à¸à¹à¸§à¸" if urgency == "à¹à¸£à¹à¸à¸à¹à¸§à¸" else "ð¡ à¸à¸à¸à¸´"
    st.write(f"**à¸à¸§à¸²à¸¡à¹à¸£à¹à¸à¸à¹à¸§à¸:** {badge}")
    st.write(f"**à¸ªà¸à¸²à¸à¸°à¸à¸±à¸à¸à¸¸à¸à¸±à¸:** {selected.get('status','')}")

st.divider()

# âââ à¸à¸­à¸£à¹à¸¡à¸­à¸±à¸à¹à¸à¸ âââ
st.subheader("ð à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°")

current_status = selected.get("status", "à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£")
status_options = ["à¸£à¸­à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£", "à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£", "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸"]
current_idx = status_options.index(current_status) if current_status in status_options else 0

new_status = st.radio(
    "à¸ªà¸à¸²à¸à¸°à¹à¸«à¸¡à¹",
    status_options,
    index=current_idx,
    horizontal=False,
)

update_notes = st.text_area("à¸«à¸¡à¸²à¸¢à¹à¸«à¸à¸¸ (à¸à¹à¸²à¸¡à¸µ)", placeholder="à¹à¸à¹à¸ à¸à¹à¸­à¸¡à¹à¸ªà¸£à¹à¸ à¸£à¸­à¸à¸£à¸§à¸à¸ªà¸­à¸ à¸¯à¸¥à¸¯")

col1, col2 = st.columns(2)

with col1:
    if st.button("ð¾ à¸à¸±à¸à¸à¸¶à¸", use_container_width=True, type="primary"):
        if new_status == current_status:
            st.warning("â ï¸ à¸ªà¸à¸²à¸à¸°à¹à¸«à¸¡à¸·à¸­à¸à¹à¸à¸´à¸¡ à¹à¸¡à¹à¸¡à¸µà¸à¸²à¸£à¹à¸à¸¥à¸µà¹à¸¢à¸à¹à¸à¸¥à¸")
        else:
            update_data = {"status": new_status}
            if update_notes.strip():
                old_notes = selected.get("notes") or ""
                update_data["notes"] = f"{old_notes}\n[{datetime.now().strftime('%d/%m %H:%M')}] {update_notes.strip()}".strip()

            ok, result = update_record(selected["id"], update_data)

            if ok:
                st.success(f"â à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸°à¹à¸à¹à¸ **{new_status}** à¸ªà¸³à¹à¸£à¹à¸!")
                if new_status == "à¹à¸ªà¸£à¹à¸à¸ªà¸´à¹à¸":
                    st.balloons()

                msg = (
                    f"\nð à¸­à¸±à¸à¹à¸à¸à¸ªà¸à¸²à¸à¸° [{selected.get('job_id','')}]\n"
                    f"ð¤ {selected.get('customer_name','')} | {selected.get('repair_type','')}\n"
                    f"ð {selected.get('location','')}\n"
                    f"ð {current_status} â {new_status}\n"
                    f"ð {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )
                if update_notes:
                    msg += f"\nð {update_notes}"
                send_line_notify(msg)

                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"â à¹à¸à¸´à¸à¸à¹à¸­à¸à¸´à¸à¸à¸¥à¸²à¸: {result}")

with col2:
    if st.button("ð  à¸«à¸à¹à¸²à¸«à¸¥à¸±à¸", use_container_width=True):
        st.switch_page("ð _à¸«à¸à¹à¸²à¸«à¸¥à¸±à¸.py")

# âââ à¸à¸¸à¹à¸¡à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£ âââ
st.divider()
st.subheader("ðï¸ à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£")

if not st.session_state.confirm_delete_status:
    if st.button("ðï¸ à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸µà¹", use_container_width=True):
        st.session_state.confirm_delete_status = True
        st.rerun()
else:
    st.error(f"â ï¸ à¸¢à¸·à¸à¸¢à¸±à¸à¸à¸²à¸£à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£ **{selected.get('job_id','')}** ({selected.get('customer_name','')}) â à¹à¸¡à¹à¸ªà¸²à¸¡à¸²à¸£à¸à¸à¸¹à¹à¸à¸·à¸à¹à¸à¹!")
    cd1, cd2 = st.columns(2)
    if cd1.button("â à¸¢à¸·à¸à¸¢à¸±à¸à¸¥à¸", use_container_width=True, type="primary"):
        ok, _ = delete_record(selected["id"])
        if ok:
            st.success("ðï¸ à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£à¸ªà¸³à¹à¸£à¹à¸!")
            st.session_state.confirm_delete_status = False
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("â à¹à¸à¸´à¸à¸à¹à¸­à¸à¸´à¸à¸à¸¥à¸²à¸à¹à¸à¸à¸²à¸£à¸¥à¸")
    if cd2.button("â à¸¢à¸à¹à¸¥à¸´à¸", use_container_width=True):
        st.session_state.confirm_delete_status = False
        st.rerun()

# âââ à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸²à¸à¸à¸±à¹à¸à¸«à¸¡à¸à¸à¸µà¹à¸£à¸­à¸­à¸¢à¸¹à¹ âââ
st.divider()
st.subheader(f"â³ à¸à¸²à¸à¸à¸µà¹à¸¢à¸±à¸à¸à¹à¸²à¸à¸­à¸¢à¸¹à¹ ({len(jobs)} à¸£à¸²à¸¢à¸à¸²à¸£)")
for j in jobs:
    status_e = "ð¨" if j.get("status") == "à¸à¸³à¸¥à¸±à¸à¸à¸³à¹à¸à¸´à¸à¸à¸²à¸£" else "â³"
    urg_e = "ð´" if j.get("urgency") == "à¹à¸£à¹à¸à¸à¹à¸§à¸" else "ð¡"
    st.caption(f"{status_e}{urg_e} {j.get('job_id','')} â {j.get('customer_name','')} â {j.get('repair_type','')}")
