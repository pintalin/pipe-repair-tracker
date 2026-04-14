# -*- coding: utf-8 -*-
# utils.py — ฟังก์ชันกลางที่ใช้ร่วมกันทุกหน้า

import streamlit as st
import requests

# ─────────────────────────────────────────
#  CONFIG — อ่านจาก st.secrets (Streamlit Cloud)
#  หรือ .streamlit/secrets.toml (local)
# ─────────────────────────────────────────
def _get_secret(section: str, key: str, fallback: str = "") -> str:
    """อ่าน secret แบบปลอดภัย — ถ้าไม่มีใช้ fallback"""
    try:
        return st.secrets[section][key]
    except Exception:
        return fallback

SUPABASE_URL      = _get_secret("supabase", "url",      "https://lfwdstvfqoziyewdfkdv.supabase.co")
SUPABASE_ANON_KEY = _get_secret("supabase", "anon_key", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxmd2RzdHZmcW96aXlld2Rma2R2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxODIzNzMsImV4cCI6MjA5MDc1ODM3M30.BxVhK0oPD0YbDB7NjrGtnUzvIN94fcfh4fJPua2mc6E")
TABLE             = "pipe_repairs"
TECHNICIANS_TABLE = "technicians"

TELEGRAM_BOT_TOKEN = _get_secret("telegram", "bot_token", "8719386203:AAGPqCrdE-JQ6-VbQ967dVuzD4hi7tHXgz8")
TELEGRAM_CHAT_ID   = _get_secret("telegram", "chat_id",   "-1003878541089")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ─────────────────────────────────────────
#  SUPABASE HELPERS — pipe_repairs
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


def delete_record(record_id: int):
    """ลบรายการงานซ่อม"""
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{record_id}",
        headers=HEADERS,
    )
    return r.ok, r.status_code


# ─────────────────────────────────────────
#  SUPABASE HELPERS — technicians
# ─────────────────────────────────────────
def fetch_technicians(active_only: bool = True):
    """ดึงรายชื่อพนักงาน/ช่าง"""
    params = "?select=*&order=name.asc"
    if active_only:
        params += "&active=eq.true"
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TECHNICIANS_TABLE}{params}", headers=HEADERS)
    return r.json() if r.ok else []


def insert_technician(data: dict):
    """เพิ่มพนักงาน/ช่างใหม่"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{TECHNICIANS_TABLE}",
        headers=HEADERS,
        json=data,
    )
    return r.ok, r.json()


def update_technician(tech_id: int, data: dict):
    """อัปเดตข้อมูลพนักงาน"""
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{TECHNICIANS_TABLE}?id=eq.{tech_id}",
        headers=h,
        json=data,
    )
    return r.ok, r.json()


def get_technician_names(role_filter: str = None):
    """คืนรายชื่อพนักงานเป็น list สำหรับ selectbox"""
    techs = fetch_technicians(active_only=True)
    if role_filter:
        techs = [t for t in techs if t.get("role") == role_filter]
    names = [t["name"] for t in techs]
    return names if names else ["ไม่มีข้อมูล"]


# ─────────────────────────────────────────
#  CHANNELS
# ─────────────────────────────────────────
CHANNELS = [
    "Line",
    "Facebook",
    "Call Center 1162",
    "โทรศัพท์แจ้ง",
    "Walk-in (เข้ามาแจ้งเอง)",
]


# ─────────────────────────────────────────
#  TELEGRAM NOTIFY
# ─────────────────────────────────────────
def send_line_notify(message: str):
    """ส่งแจ้งเตือนผ่าน Telegram Bot"""
    token = _get_secret("telegram", "bot_token", TELEGRAM_BOT_TOKEN)
    chat_id = _get_secret("telegram", "chat_id", TELEGRAM_CHAT_ID)
    if not token or not chat_id:
        return False, "ยังไม่ได้ตั้งค่า Telegram"
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": message},
            timeout=10,
        )
        return r.ok, r.text
    except Exception as e:
        return False, str(e)


# ─────────────────────────────────────────
#  MOBILE STYLE
# ─────────────────────────────────────────
def apply_mobile_style():
    import streamlit.components.v1 as components

    # ── CSS: Thai font + Material Symbols fix + กปภ. Blue Theme ──
    st.markdown("""
    <style>
        /* โหลด Material Symbols Rounded จาก Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        /* ฟอนต์ไทย */
        html, body, * {
            font-family: 'Leelawadee UI', 'Leelawadee', 'Tahoma',
                         'Noto Sans Thai', 'Noto Sans', 'Arial Unicode MS',
                         sans-serif !important;
        }

        /* คืนฟอนต์ Material Symbols ให้ Streamlit icons */
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        span[class*="material"] {
            font-family: 'Material Symbols Rounded' !important;
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
            font-style: normal !important;
            font-weight: normal !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            display: inline-block !important;
        }

        /* ════════════════════════════════
           กปภ. BLUE THEME
        ════════════════════════════════ */

        /* พื้นหลังหลัก — ฟ้าอ่อน */
        .stApp {
            background-color: #EBF5FB !important;
        }

        /* ═══ SIDEBAR — navy gradient ═══ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D3B6E 0%, #1565C0 100%) !important;
            min-width: 0 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        /* Nav links */
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
            border-radius: 10px !important;
            margin: 2px 8px !important;
            padding: 0.5rem 0.75rem !important;
            color: rgba(255,255,255,0.88) !important;
            transition: background 0.2s;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
            background: rgba(255,255,255,0.18) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
            background: rgba(255,255,255,0.28) !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        /* ซ่อนลูกศร collapse sidebar บน mobile */
        [data-testid="collapsedControl"] {
            background: #0D3B6E !important;
            color: white !important;
        }

        /* ═══ MAIN CONTENT ═══ */
        .block-container {
            padding: 1rem 0.8rem !important;
            max-width: 480px;
            margin: auto;
        }

        /* ═══ CARDS / EXPANDERS ═══ */
        [data-testid="stExpander"] {
            background: #FFFFFF !important;
            border: 1px solid #BBDEFB !important;
            border-radius: 14px !important;
            box-shadow: 0 2px 8px rgba(0,102,204,0.08) !important;
            margin-bottom: 0.5rem !important;
        }
        [data-testid="stExpander"] summary {
            border-radius: 14px !important;
        }

        /* ═══ METRIC CONTAINERS ═══ */
        [data-testid="metric-container"] {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #BBDEFB;
            box-shadow: 0 2px 8px rgba(0,102,204,0.08);
        }

        /* ═══ BUTTONS ═══ */
        .stButton > button {
            background: linear-gradient(135deg, #0066CC 0%, #1565C0 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.6rem !important;
            font-size: 1rem !important;
            width: 100%;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px rgba(0,102,204,0.25) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #004FA3 0%, #0D47A1 100%) !important;
            box-shadow: 0 4px 14px rgba(0,102,204,0.38) !important;
            transform: translateY(-1px) !important;
        }
        /* ปุ่มลบ — แดง */
        .stButton > button[kind="secondary"],
        div[data-testid="stButton-delete"] > button {
            background: linear-gradient(135deg, #E53935 0%, #C62828 100%) !important;
            box-shadow: 0 2px 8px rgba(229,57,53,0.25) !important;
        }

        /* ═══ INPUT / SELECT ═══ */
        .stSelectbox, .stTextInput, .stTextArea { font-size: 1rem; }
        .stTextInput input, .stTextArea textarea {
            border: 1.5px solid #BBDEFB !important;
            border-radius: 10px !important;
            background: #FFFFFF !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #0066CC !important;
            box-shadow: 0 0 0 3px rgba(0,102,204,0.12) !important;
        }

        /* ═══ TABS ═══ */
        [data-testid="stTabs"] [role="tablist"] {
            background: #D6EAF8;
            border-radius: 12px;
            padding: 4px;
            gap: 4px;
        }
        [data-testid="stTabs"] [role="tab"] {
            border-radius: 9px !important;
            font-weight: 600 !important;
            color: #1565C0 !important;
            transition: all 0.2s !important;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background: #FFFFFF !important;
            color: #0D3B6E !important;
            box-shadow: 0 1px 6px rgba(0,102,204,0.15) !important;
        }

        /* ═══ DIVIDER ═══ */
        hr { border-color: #BBDEFB !important; }

        /* ═══ TYPOGRAPHY ═══ */
        h1 { font-size: 1.5rem !important; color: #0D3B6E !important; }
        h2 { font-size: 1.2rem !important; color: #1565C0 !important; }
        h3 { color: #1565C0 !important; }

        /* ═══ ALERTS ═══ */
        [data-testid="stAlert"] {
            border-radius: 12px !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    components.html("""
    <script>
    (function() {
        var MAP = {
            'keyboard_arrow_right': '▶',
            'keyboard_arrow_down':  '▼',
            'keyboard_arrow_up':    '▲',
            'keyboard_arrow_left':  '◀',
            'expand_more':          '▼',
            'expand_less':          '▲',
            'chevron_right':        '›',
            'chevron_left':         '‹',
            'arrow_forward_ios':    '›',
            'arrow_back_ios':       '‹',
            'search':               '🔍',
            'close':                '✕',
            'check':                '✓',
            'refresh':              '↺',
            'download':             '⬇',
            'upload':               '⬆',
            'edit':                 '✏',
            'delete':               '🗑',
            'add':                  '+',
            'remove':               '−',
            'info':                 'ℹ',
            'warning':              '⚠',
            'error':                '✗',
        };
        function isBroken(el) { return el.scrollWidth > 30; }
        function fix() {
            try {
                var icons = window.parent.document.querySelectorAll('[data-testid="stIconMaterial"]');
                icons.forEach(function(el) {
                    var txt = el.textContent.trim();
                    if (MAP[txt] && isBroken(el)) {
                        el.textContent = MAP[txt];
                        el.style.fontFamily = 'sans-serif';
                        el.style.fontSize   = '14px';
                        el.style.lineHeight = '1';
                    }
                });
            } catch(e) {}
        }
        fix();
        try {
            new MutationObserver(fix).observe(
                window.parent.document.body,
                { childList: true, subtree: true }
            );
        } catch(e) {}
    })();
    </script>
    """, height=0)
