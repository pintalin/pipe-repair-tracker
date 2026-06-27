"""
📊 รายงานสรุป — พร้อมกราฟระยะเวลาการซ่อม และสรุปรายเดือน
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import fetch_all, apply_mobile_style, now_th

apply_mobile_style()

st.title("📊 รายงานสรุป")

_MONTH_TH = ["","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.",
              "ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]

@st.cache_data(ttl=60)
def load():
    rows = fetch_all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    for col in ["date", "recorded_at", "started_at", "completed_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "recorded_at" in df.columns and "completed_at" in df.columns:
        diff = (df["completed_at"] - df["recorded_at"]).dt.total_seconds() / 3600
        df["total_hours"] = diff.clip(lower=0)
    if "recorded_at" in df.columns and "started_at" in df.columns:
        diff2 = (df["started_at"] - df["recorded_at"]).dt.total_seconds() / 3600
        df["response_hours"] = diff2.clip(lower=0)
    if "started_at" in df.columns and "completed_at" in df.columns:
        diff3 = (df["completed_at"] - df["started_at"]).dt.total_seconds() / 3600
        df["repair_hours"] = diff3.clip(lower=0)
    return df

df_all = load()
if df_all.empty:
    st.warning("ไม่พบข้อมูล")
    st.stop()

# ══════════════════════════════════════════
# Month selector
# ══════════════════════════════════════════
def _month_opts(df):
    opts = [("ทั้งหมด", None, None)]
    if "date" in df.columns:
        months = (
            df["date"].dropna()
            .dt.to_period("M")
            .drop_duplicates()
            .sort_values(ascending=False)
        )
        for p in months:
            opts.append((f"{_MONTH_TH[p.month]} {p.year+543}", p.year, p.month))
    return opts

month_opts = _month_opts(df_all)
month_labels = [o[0] for o in month_opts]
cur_y, cur_m = now_th().year, now_th().month
default_idx = next((i for i, o in enumerate(month_opts) if o[1] == cur_y and o[2] == cur_m), 0)

st.markdown("#### 📅 เลือกช่วงเวลา")
sel_label = st.selectbox("เดือน", month_labels, index=default_idx,
                          key="rep_month", label_visibility="collapsed")
sel_opt = month_opts[month_labels.index(sel_label)]
sel_year, sel_mon = sel_opt[1], sel_opt[2]

if sel_year and sel_mon and "date" in df_all.columns:
    df = df_all[
        (df_all["date"].dt.year == sel_year) & (df_all["date"].dt.month == sel_mon)
    ].copy()
    month_title = f" — {sel_label}"
else:
    df = df_all.copy()
    month_title = " — ทั้งหมด"

st.caption(f"แสดงข้อมูล{month_title} | {len(df)} รายการ")
st.divider()

# ══════════════════════════════════════════
# 0. สรุปรายเดือน (ตารางเปรียบเทียบ)
# ══════════════════════════════════════════
st.subheader("📅 สรุปรายเดือน (เปรียบเทียบ)")
if "date" in df_all.columns and not df_all.empty:
    _tmp = df_all[df_all["date"].notna()].copy()
    _tmp["_period"] = _tmp["date"].dt.to_period("M")
    monthly = _tmp.groupby("_period").agg(
        ทั้งหมด=("id", "count"),
        เสร็จสิ้น=("status", lambda x: (x == "เสร็จสิ้น").sum()),
        รอดำเนินการ=("status", lambda x: (x == "รอดำเนินการ").sum()),
        กำลังดำเนินการ=("status", lambda x: (x == "กำลังดำเนินการ").sum()),
        เร่งด่วน=("urgency", lambda x: (x == "เร่งด่วน").sum()),
    ).sort_index()
    monthly.index = [f"{_MONTH_TH[p.month]} {p.year+543}" for p in monthly.index]

    st.markdown("**กราฟเปรียบเทียบจำนวนงานรายเดือน**")
    st.bar_chart(monthly[["ทั้งหมด", "เสร็จสิ้น"]], color=["#1565C0", "#2E7D32"], height=220)

    st.markdown("**ตารางสรุปรายเดือน**")
    st.dataframe(monthly, use_container_width=True)

st.divider()

# ══════════════════════════════════════════
# 1. สรุปตามสถานะ
# ══════════════════════════════════════════
st.subheader(f"📈 สรุปตามสถานะ{month_title}")
if "status" in df.columns and not df.empty:
    s = df["status"].value_counts().reset_index()
    s.columns = ["สถานะ", "จำนวน"]
    st.bar_chart(s.set_index("สถานะ"))
    for _, r in s.iterrows():
        pct = r["จำนวน"] / len(df) * 100
        st.write(f"- **{r['สถานะ']}**: {r['จำนวน']} งาน ({pct:.0f}%)")
else:
    st.info("ไม่มีข้อมูลในเดือนที่เลือก")

st.divider()

# ══════════════════════════════════════════
# 2. ประเภทงานซ่อมยอดนิยม
# ══════════════════════════════════════════
st.subheader(f"🔧 ประเภทงานซ่อมยอดนิยม{month_title}")
if "repair_type" in df.columns and not df.empty:
    rt = df["repair_type"].value_counts().head(7).reset_index()
    rt.columns = ["ประเภท", "จำนวน"]
    st.bar_chart(rt.set_index("ประเภท"))

st.divider()

# ══════════════════════════════════════════
# 3. วิเคราะห์ระยะเวลาการซ่อม
# ══════════════════════════════════════════
st.subheader(f"⏱️ วิเคราะห์ระยะเวลาการซ่อม{month_title}")

done_df = df[df["status"] == "เสร็จสิ้น"].copy() \
          if "status" in df.columns else pd.DataFrame()

if not done_df.empty and "total_hours" in done_df.columns:
    valid = done_df[done_df["total_hours"].notna() & (done_df["total_hours"] > 0)]

    if not valid.empty:
        avg_h = valid["total_hours"].mean()
        max_h = valid["total_hours"].max()
        min_h = valid["total_hours"].min()
        med_h = valid["total_hours"].median()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⌀ เฉลี่ย",  f"{avg_h:.1f} ชม.")
        c2.metric("🏆 เร็วสุด", f"{min_h:.1f} ชม.")
        c3.metric("🐢 ช้าสุด",  f"{max_h:.1f} ชม.")
        c4.metric("📊 มัธยฐาน", f"{med_h:.1f} ชม.")

        st.markdown("---")

        if "repair_type" in valid.columns:
            st.markdown("**🔧 เวลาเฉลี่ย (ชม.) แยกตามประเภทงาน**")
            by_type = (
                valid.groupby("repair_type")["total_hours"]
                .mean().sort_values(ascending=False).round(2)
            )
            st.bar_chart(by_type, color="#1565C0")
            by_type_tbl = valid.groupby("repair_type").agg(
                จำนวนงาน=("total_hours", "count"),
                เฉลี่ย_ชม=("total_hours", lambda x: round(x.mean(), 2)),
                น้อยสุด_ชม=("total_hours", lambda x: round(x.min(), 2)),
                มากสุด_ชม=("total_hours", lambda x: round(x.max(), 2)),
            ).reset_index().rename(columns={"repair_type": "ประเภทงาน"})
            st.dataframe(by_type_tbl, use_container_width=True, hide_index=True)

        st.markdown("---")

        if "technician" in valid.columns:
            tech_v = valid[valid["technician"].notna() & (valid["technician"] != "")]
            if not tech_v.empty:
                st.markdown("**👷 เวลาเฉลี่ย (ชม.) แยกตามช่าง**")
                by_tech = (
                    tech_v.groupby("technician")["total_hours"]
                    .mean().sort_values(ascending=False).round(2)
                )
                st.bar_chart(by_tech, color="#2E7D32")
                by_tech_tbl = tech_v.groupby("technician").agg(
                    จำนวนงาน=("total_hours", "count"),
                    เฉลี่ย_ชม=("total_hours", lambda x: round(x.mean(), 2)),
                ).reset_index().rename(columns={"technician": "ช่าง"})
                st.dataframe(by_tech_tbl, use_container_width=True, hide_index=True)

        st.markdown("---")

        if "response_hours" in valid.columns:
            resp_v = valid[valid["response_hours"].notna() & (valid["response_hours"] >= 0)]
            if not resp_v.empty:
                st.markdown("**🚀 เวลาตอบสนองเฉลี่ย (ชม.) — รับแจ้ง → เริ่มซ่อม**")
                avg_resp = resp_v["response_hours"].mean()
                st.metric("เฉลี่ยเวลาตอบสนอง", f"{avg_resp:.1f} ชม.")
                if "urgency" in resp_v.columns:
                    by_urg = resp_v.groupby("urgency")["response_hours"].mean().round(2)
                    st.markdown("แยกตามความเร่งด่วน:")
                    st.bar_chart(by_urg, color="#E65100")

        st.markdown("---")

        if "date" in df.columns:
            st.markdown(f"**📅 จำนวนงานรายวัน{month_title}**")
            daily = (
                df[df["date"].notna()]
                .groupby(df["date"].dt.date).size().reset_index()
            )
            daily.columns = ["วันที่", "จำนวนงาน"]
            daily = daily.sort_values("วันที่").tail(31)
            st.line_chart(daily.set_index("วันที่"), color="#6A1B9A")

    else:
        st.info("ยังไม่มีงานที่เสร็จสิ้นพร้อม timestamp ครบในเดือนนี้")
else:
    st.info("ยังไม่มีงานที่เสร็จสิ้นในเดือนที่เลือก")

st.divider()

# ══════════════════════════════════════════
# 4. งานตามผู้รับแจ้ง
# ══════════════════════════════════════════
st.subheader(f"👷 งานตามผู้รับแจ้ง{month_title}")
if "assigned_to" in df.columns and not df.empty:
    at = df["assigned_to"].value_counts().reset_index()
    at.columns = ["ผู้รับแจ้ง", "จำนวนงาน"]
    st.dataframe(at, use_container_width=True, hide_index=True)

st.divider()

# ══════════════════════════════════════════
# 5. Export ข้อมูล
# ══════════════════════════════════════════
st.subheader(f"⬇️ Export ข้อมูล{month_title}")

df_export = df.copy()
for col in ["date", "recorded_at", "started_at", "completed_at"]:
    if col in df_export.columns:
        df_export[col] = df_export[col].astype(str)

_fname_suffix = f"{sel_year}{sel_mon:02d}" if sel_year else "all"
csv = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button("📥 Download CSV", csv,
    file_name=f"pipe_repair_{_fname_suffix}.csv",
    mime="text/csv", use_container_width=True)

buf = io.BytesIO()
df_export.to_excel(buf, index=False, engine="openpyxl")
st.download_button("📥 Download Excel", buf.getvalue(),
    file_name=f"pipe_repair_{_fname_suffix}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

if st.button("🔄 รีเฟรช", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if st.button("🏠 หน้าหลัก", use_container_width=True):
    st.switch_page("page_home.py")
