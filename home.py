# -*- coding: utf-8 -*-
"""
Entry point — sets up navigation for all pages.
Uses st.navigation() to avoid pages/ directory scanning issues.
"""
import streamlit as st

st.set_page_config(
    page_title="Pipe Repair Tracker",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)


pg = st.navigation([
    st.Page("page_home.py",          title="หน้าหลัก",      icon="🏠"),
    st.Page("page_report_job.py",    title="แจ้งงานซ่อม",    icon="➕"),
    st.Page("page_manage_tech.py",   title="จัดการช่าง",     icon="🔧"),
    st.Page("page_update_status.py", title="อัปเดตสถานะ",   icon="✏️"),
    st.Page("page_report.py",        title="รายงาน",         icon="📊"),
], position="sidebar")

pg.run()
