"""
📊 รายงานสรุป
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import fetch_all, apply_mobile_style

st.set_page_config(page_title="📊 รายงาน", page_icon="📊", layout="centered",
                   initial_sidebar_state="collapsed")
apply_mobile_style()

st.title("📊 รายงานสรุป")

@st.cache_data(ttl=60)
def load():
    rows = fetch_all()
    if not rows: return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

df = load()
if df.empty:
    st.warning("ไม่พบข้อมูล")
    st.stop()

# ─── สรุปตามสถานะ ───
st.subheader("📈 สรุปตามสถานะ")
if "status" in df.columns:
    s = df["status"].value_counts().reset_index()
    s.columns = ["สถานะ", "จำนวน"]
    st.bar_chart(s.set_index("สถานะ"))
    for _, r in s.iterrows():
        pct = r["จำนวน"] / len(df) * 100
        st.write(f"- **{r['สถานะ']}**: {r['จำนวน']} งาน ({pct:.0f}%)")

st.divider()

# ─── สรุปตามประเภทซ่อม ───
st.subheader("🔧 ประเภทงานซ่อมยอดนิยม")
if "repair_type" in df.columns:
    rt = df["repair_type"].value_counts().head(5).reset_index()
    rt.columns = ["ประเภท", "จำนวน"]
    st.bar_chart(rt.set_index("ประเภท"))

st.divider()

# ─── สรุปตามผู้รับแจ้ง ───
st.subheader("👷 งานตามผู้รับแจ้ง")
if "assigned_to" in df.columns:
    at = df["assigned_to"].value_counts().reset_index()
    at.columns = ["ผู้รับแจ้ง", "งาน"]
    st.dataframe(at, use_container_width=True, hide_index=True)

st.divider()

# ─── Export ───
st.subheader("⬇️ Export ข้อมูล")
csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button("📥 Download CSV", csv,
    file_name=f"pipe_repair_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv", use_container_width=True)

buf = io.BytesIO()
df.to_excel(buf, index=False, engine="openpyxl")
st.download_button("📥 Download Excel", buf.getvalue(),
    file_name=f"pipe_repair_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

if st.button("🔄 รีเฟรช", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
