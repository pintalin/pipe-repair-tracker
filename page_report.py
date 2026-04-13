"""
📊 รายงานสรุป — พร้อมกราฟระยะเวลาการซ่อม
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import fetch_all, apply_mobile_style

apply_mobile_style()

st.title("📊 รายงานสรุป")

@st.cache_data(ttl=60)
def load():
    rows = fetch_all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    # แปลงวันที่
    for col in ["date", "recorded_at", "started_at", "completed_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    # ── คำนวณระยะเวลา (หน่วย: ชั่วโมง) ──
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

df = load()
if df.empty:
    st.warning("ไม่พบข้อมูล")
    st.stop()

# ══════════════════════════════════════════
# 1. สรุปตามสถานะ
# ══════════════════════════════════════════
st.subheader("📈 สรุปตามสถานะ")
if "status" in df.columns:
    s = df["status"].value_counts().reset_index()
    s.columns = ["สถานะ", "จำนวน"]
    st.bar_chart(s.set_index("สถานะ"))
    for _, r in s.iterrows():
        pct = r["จำนวน"] / len(df) * 100
        st.write(f"- **{r['สถานะ']}**: {r['จำนวน']} งาน ({pct:.0f}%)")

st.divider()

# ══════════════════════════════════════════
# 2. ประเภทงานซ่อมยอดนิยม
# ══════════════════════════════════════════
st.subheader("🔧 ประเภทงานซ่อมยอดนิยม")
if "repair_type" in df.columns:
    rt = df["repair_type"].value_counts().head(7).reset_index()
    rt.columns = ["ประเภท", "จำนวน"]
    st.bar_chart(rt.set_index("ประเภท"))

st.divider()

# ══════════════════════════════════════════
# 3. ⏱️ วิเคราะห์ระยะเวลาการซ่อม
# ══════════════════════════════════════════
st.subheader("⏱️ วิเคราะห์ระยะเวลาการซ่อม")

done_df = df[df.get("status", pd.Series(dtype=str)) == "เสร็จสิ้น"].copy() \
          if "status" in df.columns else pd.DataFrame()

if not done_df.empty and "total_hours" in done_df.columns:
    valid = done_df[done_df["total_hours"].notna() & (done_df["total_hours"] > 0)]

    if not valid.empty:
        # ── สถิติโดยรวม ──
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

        # ── กราฟ 1: เฉลี่ยระยะเวลารวม ตามประเภทงาน ──
        if "repair_type" in valid.columns:
            st.markdown("**🔧 เวลาเฉลี่ย (ชม.) แยกตามประเภทงาน**")
            by_type = (
                valid.groupby("repair_type")["total_hours"]
                .mean()
                .sort_values(ascending=False)
                .round(2)
            )
            st.bar_chart(by_type, color="#1565C0")
            # ตารางประกอบ
            by_type_tbl = valid.groupby("repair_type").agg(
                จำนวนงาน=("total_hours", "count"),
                เฉลี่ย_ชม=("total_hours", lambda x: round(x.mean(), 2)),
                น้อยสุด_ชม=("total_hours", lambda x: round(x.min(), 2)),
                มากสุด_ชม=("total_hours", lambda x: round(x.max(), 2)),
            ).reset_index().rename(columns={"repair_type": "ประเภทงาน"})
            st.dataframe(by_type_tbl, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── กราฟ 2: เฉลี่ยระยะเวลา ตามช่าง ──
        if "technician" in valid.columns:
            tech_v = valid[valid["technician"].notna() & (valid["technician"] != "")]
            if not tech_v.empty:
                st.markdown("**👷 เวลาเฉลี่ย (ชม.) แยกตามช่าง**")
                by_tech = (
                    tech_v.groupby("technician")["total_hours"]
                    .mean()
                    .sort_values(ascending=False)
                    .round(2)
                )
                st.bar_chart(by_tech, color="#2E7D32")
                by_tech_tbl = tech_v.groupby("technician").agg(
                    จำนวนงาน=("total_hours", "count"),
                    เฉลี่ย_ชม=("total_hours", lambda x: round(x.mean(), 2)),
                ).reset_index().rename(columns={"technician": "ช่าง"})
                st.dataframe(by_tech_tbl, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── กราฟ 3: เวลาตอบสนอง (รับแจ้ง → เริ่มซ่อม) ──
        if "response_hours" in valid.columns:
            resp_v = valid[valid["response_hours"].notna() & (valid["response_hours"] >= 0)]
            if not resp_v.empty:
                st.markdown("**🚀 เวลาตอบสนองเฉลี่ย (ชม.) — รับแจ้ง → เริ่มซ่อม**")
                avg_resp = resp_v["response_hours"].mean()
                st.metric("เฉลี่ยเวลาตอบสนอง", f"{avg_resp:.1f} ชม.")
                if "urgency" in resp_v.columns:
                    by_urg = (
                        resp_v.groupby("urgency")["response_hours"]
                        .mean()
                        .round(2)
                    )
                    st.markdown("แยกตามความเร่งด่วน:")
                    st.bar_chart(by_urg, color="#E65100")

        st.markdown("---")

        # ── กราฟ 4: แนวโน้มรายวัน (7 วันล่าสุด) ──
        if "date" in df.columns:
            st.markdown("**📅 จำนวนงานรายวัน (30 วันล่าสุด)**")
            daily = (
                df[df["date"].notna()]
                .groupby(df["date"].dt.date)
                .size()
                .reset_index()
            )
            daily.columns = ["วันที่", "จำนวนงาน"]
            daily = daily.sort_values("วันที่").tail(30)
            st.line_chart(daily.set_index("วันที่"), color="#6A1B9A")

    else:
        st.info("ยังไม่มีงานที่เสร็จสิ้นพร้อม timestamp ครบ — ข้อมูลจะแสดงเมื่อมีงานเสร็จ")
else:
    st.info("ยังไม่มีงานที่เสร็จสิ้น — กราฟระยะเวลาจะแสดงเมื่อมีงานสำเร็จ")

st.divider()

# ══════════════════════════════════════════
# 4. งานตามผู้รับแจ้ง
# ══════════════════════════════════════════
st.subheader("👷 งานตามผู้รับแจ้ง")
if "assigned_to" in df.columns:
    at = df["assigned_to"].value_counts().reset_index()
    at.columns = ["ผู้รับแจ้ง", "จำนวนงาน"]
    st.dataframe(at, use_container_width=True, hide_index=True)

st.divider()

# ══════════════════════════════════════════
# 5. Export ข้อมูล
# ══════════════════════════════════════════
st.subheader("⬇️ Export ข้อมูล")

# แปลง datetime กลับเป็น string สำหรับ export
df_export = df.copy()
for col in ["date", "recorded_at", "started_at", "completed_at"]:
    if col in df_export.columns:
        df_export[col] = df_export[col].astype(str)

csv = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button("📥 Download CSV", csv,
    file_name=f"pipe_repair_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv", use_container_width=True)

buf = io.BytesIO()
df_export.to_excel(buf, index=False, engine="openpyxl")
st.download_button("📥 Download Excel", buf.getvalue(),
    file_name=f"pipe_repair_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

if st.button("🔄 รีเฟรช", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if st.button("🏠 หน้าหลัก", use_container_width=True):
    st.switch_page("page_home.py")
