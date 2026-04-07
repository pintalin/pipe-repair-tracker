# utils.py â à¸à¸±à¸à¸à¹à¸à¸±à¸à¸à¸¥à¸²à¸à¸à¸µà¹à¹à¸à¹à¸£à¹à¸§à¸¡à¸à¸±à¸à¸à¸¸à¸à¸«à¸à¹à¸²

import streamlit as st
import requests

# âââââââââââââââââââââââââââââââââââââââââ
#  CONFIG  â à¹à¸à¹à¸à¹à¸²à¹à¸«à¸¥à¹à¸²à¸à¸µà¹
# âââââââââââââââââââââââââââââââââââââââââ
SUPABASE_URL = "https://lfwdstvfqoziyewdfkdv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxmd2RzdHZmcW96aXlld2Rma2R2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxODIzNzMsImV4cCI6MjA5MDc1ODM3M30.BxVhK0oPD0YbDB7NjrGtnUzvIN94fcfh4fJPua2mc6E"
TABLE = "pipe_repairs"
TECHNICIANS_TABLE = "technicians"

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = "8719386203:AAGPqCrdE-JQ6-VbQ967dVuzD4hi7tHXgz8"
TELEGRAM_CHAT_ID = "6442934423"

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# âââââââââââââââââââââââââââââââââââââââââ
#  SUPABASE HELPERS â pipe_repairs
# âââââââââââââââââââââââââââââââââââââââââ
def fetch_all(filters: dict = None, limit: int = 500):
    """à¸à¸¶à¸à¸à¹à¸­à¸¡à¸¹à¸¥à¸à¸±à¹à¸à¸«à¸¡à¸à¸à¸²à¸ Supabase"""
    params = f"?select=*&order=recorded_at.desc&limit={limit}"
    if filters:
        for k, v in filters.items():
            params += f"&{k}=eq.{v}"
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}{params}", headers=HEADERS)
    return r.json() if r.ok else []


def insert_record(data: dict):
    """à¹à¸à¸´à¹à¸¡à¸à¹à¸­à¸¡à¸¹à¸¥à¹à¸«à¸¡à¹"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        headers=HEADERS,
        json=data,
    )
    return r.ok, r.json()


def update_record(record_id: int, data: dict):
    """à¸­à¸±à¸à¹à¸à¸à¸à¹à¸­à¸¡à¸¹à¸¥"""
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{record_id}",
        headers=h,
        json=data,
    )
    return r.ok, r.json()


def delete_record(record_id: int):
    """à¸¥à¸à¸£à¸²à¸¢à¸à¸²à¸£à¸à¸²à¸à¸à¹à¸­à¸¡"""
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{record_id}",
        headers=HEADERS,
    )
    return r.ok, r.status_code


# âââââââââââââââââââââââââââââââââââââââââ
#  SUPABASE HELPERS â technicians
# âââââââââââââââââââââââââââââââââââââââââ
def fetch_technicians(active_only: bool = True):
    """à¸à¸¶à¸à¸£à¸²à¸¢à¸à¸·à¹à¸­à¸à¸à¸±à¸à¸à¸²à¸/à¸à¹à¸²à¸"""
    params = "?select=*&order=name.asc"
    if active_only:
        params += "&active=eq.true"
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TECHNICIANS_TABLE}{params}", headers=HEADERS)
    return r.json() if r.ok else []


def insert_technician(data: dict):
    """à¹à¸à¸´à¹à¸¡à¸à¸à¸±à¸à¸à¸²à¸/à¸à¹à¸²à¸à¹à¸«à¸¡à¹"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{TECHNICIANS_TABLE}",
        headers=HEADERS,
        json=data,
    )
    return r.ok, r.json()


def update_technician(tech_id: int, data: dict):
    """à¸­à¸±à¸à¹à¸à¸à¸à¹à¸­à¸¡à¸¹à¸¥à¸à¸à¸±à¸à¸à¸²à¸"""
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{TECHNICIANS_TABLE}?id=eq.{tech_id}",
        headers=h,
        json=data,
    )
    return r.ok, r.json()


def get_technician_names(role_filter: str = None):
    """à¸à¸·à¸à¸£à¸²à¸¢à¸à¸·à¹à¸­à¸à¸à¸±à¸à¸à¸²à¸à¹à¸à¹à¸ list à¸ªà¸³à¸«à¸£à¸±à¸ selectbox"""
    techs = fetch_technicians(active_only=True)
    if role_filter:
        techs = [t for t in techs if t.get("role") == role_filter]
    names = [t["name"] for t in techs]
    return names if names else ["à¹à¸¡à¹à¸¡à¸µà¸à¹à¸­à¸¡à¸¹à¸¥"]


# âââââââââââââââââââââââââââââââââââââââââ
#  CHANNELS
# âââââââââââââââââââââââââââââââââââââââââ
CHANNELS = [
    "ð± Line",
    "ð Facebook",
    "ð Call Center 1162",
    "âï¸ à¹à¸à¸£à¸¨à¸±à¸à¸à¹à¹à¸à¹à¸",
    "ð¶ Walk-in (à¹à¸à¹à¸²à¸¡à¸²à¹à¸à¹à¸à¹à¸­à¸)",
]


# âââââââââââââââââââââââââââââââââââââââââ
#  TELEGRAM NOTIFY
# âââââââââââââââââââââââââââââââââââââââââ
def send_line_notify(message: str):
    """à¸ªà¹à¸à¹à¸à¹à¸à¹à¸à¸·à¸­à¸à¸à¹à¸²à¸ Telegram Bot"""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        return False, "à¸¢à¸±à¸à¹à¸¡à¹à¹à¸à¹à¸à¸±à¹à¸à¸à¹à¸² TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID"
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10,
        )
        return r.ok, r.text
    except Exception as e:
        return False, str(e)


# âââââââââââââââââââââââââââââââââââââââââ
#  MOBILE STYLE
# âââââââââââââââââââââââââââââââââââââââââ
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
        section[data-testid="stSidebar"] { min-width: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
