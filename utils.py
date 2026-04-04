# utils.py — ฟังก์ชันกลางที่ใช้ร่วมกันทุกหน้า

import streamlit as st
import requests

# ─────────────────────────────────────────
#  CONFIG  ← แก้ค่าเหล่านี้
# ─────────────────────────────────────────
SUPABASE_URL = "https://lfwdstvfqoziyewdfkdv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxmd2RzdHZmcW96aXlld2Rma2R2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxODIzNzMsImV4cCI6MjA5MDc1ODM3M30.BxVhK0oPD0YbDB7NjrGtnUzvIN94fcfh4fJPua2mc6E"
TABLE = "pipe_repairs"

# Telegram Bot Settings
# วิธีขอ: คุยกับ @BotFather ใน Telegram → /newbot → copy token
TELEGRAM_BOT_TOKEN = "8719386203:AAGPqCrdE-JQ6-VbQ967dVuzD4hi7tHXgz8"
TELEGRAM_CHAT_ID = "6442934423"

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ─────────────────────────────────────────
#  SUPABASE HELPERS
# ─────────────────────────────────────────
def fetch_all(filters: dict = None, limit: int = 500):
    """ดึงข้อมูลทั้งหมดจาก Supabase"""
    params = f"?select=*&order=recorded_at.desc&limit={limit}"
    if filters:
        for k, v in filters.items():
            params += f"&{k}=eq.{v}"
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}{params}", headers=HEADERS)
    return r.json() if r.ok else []


def insert_record(data: dict):
    """เพิ่มข้อมูลใหม่"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        headers=HEADERS,
        json=data,
    )
    return r.ok, r.json()


def update_record(record_id: int, data: dict):
    """อัปเดตข้อมูล"""
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{record_id}",
        headers=h,
        json=data,
    )
    return r.ok, r.json()


# ─────────────────────────────────────────
#  TELEGRAM NOTIFY
# ─────────────────────────────────────────
def send_line_notify(message: str):
    """ส่งแจ้งเตือนผ่าน Telegram Bot"""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        return False, "ยังไม่ได้ตั้งค่า TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID"
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=10,
        )
        return r.ok, r.text
    except Exception as e:
        return False, str(e)


# ─────────────────────────────────────────
#  MOBILE STYLE
# ─────────────────────────────────────────
def apply_mobile_style():
    st.markdown("""
    <style>
        /* Mobile-friendly */
        .block-container { padding: 1rem 0.8rem !important; max-width: 480px; margin: auto; }
        .stButton > button { width: 100%; border-radius: 12px; padding: 0.6rem; font-size: 1rem; }
        .stSelectbox, .stTextInput, .stTextArea { font-size: 1rem; }
        [data-testid="metric-container"] {
            background: #f0f4ff; border-radius: 12px;
            padding: 12px; border: 1px solid #d0daff;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        /* ซ่อน sidebar header บน mobile */
        section[data-testid="stSidebar"] { min-width: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
