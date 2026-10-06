import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timezone, timedelta
import os
import hashlib
from io import BytesIO

IST = timezone(timedelta(hours=5, minutes=30))
st.set_page_config(page_title="NE Circle Telecom DG Ops Center | Enterprise NOC", layout="wide", page_icon="⚡", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.90)), 
                    url("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1920&q=80");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .block-container { padding-top: 0.4rem !important; padding-bottom: 0.5rem !important; }
    div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] summary span, div[data-testid="stExpander"] summary {
        color: #facc15 !important; font-weight: 800 !important; font-size: 14px !important;
    }
    div[data-testid="stRadio"] label, div[data-testid="stRadio"] div[role="radiogroup"] label {
        color: #facc15 !important; font-weight: 700 !important; font-size: 13px !important;
    }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; font-weight: 800 !important; }
    .previous-remarks-box { background-color: rgba(15, 23, 42, 0.85) !important; border: 1px solid #facc15 !important; border-radius: 8px !important; padding: 10px 14px !important; color: #ffffff !important; font-size: 14px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio.xlsx"

DEFAULT_ILA = None
for f in os.listdir('.'):
    if "ILA" in f.upper() and f.endswith(('.xlsx', '.xls')) and not f.startswith('~$'):
        DEFAULT_ILA = f
        break

BUCKET_LIST = ["GCU", "Fuel Sensor", "DG Breakdown", "DG battery", "IPMS", "OEM Spare parts", "New DG Req", "AMF Req", "Owner issue", "Access issue", "Theft case", "Jio Support", "Other Issue"]
STATUS_CHOICES = ["Automation Ok", "Manual Mode", "DG Breakdown", "DG BER", "DG Overload", "Access issue"]
FUEL_STATUS_CHOICES = ["Ok", "Fuel Sensor faulty"]

def clean_date_str(val):
    if pd.isna(val) or val is None: return ""
    val_str = str(val).strip()
    if val_str.lower() in ['nat', 'nan', 'none', '', '0']: return ""
    try:
        dt = pd.to_datetime(val)
        return dt.strftime('%Y-%m-%d')
    except:
        return val_str.split(' ')[0] if ' ' in val_str else val_str

USER_CREDENTIALS = {
    "tridip2.gogoi": {"password_hash": hashlib.sha256("Gogoi@6095".encode()).hexdigest(), "role": "Super Admin / Operations Head", "name": "Tridip Gogoi", "access": ["all"]},
    "ptpl": {"password_hash": hashlib.sha256("Rintu@2026".encode()).hexdigest(), "role": "NOC Viewer", "name": "PTPL Operations Desk", "access": ["read_only"]}
}

def verify_login(username, password):
    if username in USER_CREDENTIALS:
        if hashlib.sha256(password.encode()).hexdigest() == USER_CREDENTIALS[username]["password_hash"]:
            return USER_CREDENTIALS[username]
    return None

def is_valid_source(src):
    if hasattr(src, 'read'): return True
    if isinstance(src, str) and os.path.exists(src): return True
    return False

def load_all_trackers(dg_file, cm_file, ila_file=None):
    df_status = pd.DataFrame()
    df_fuel = pd.DataFrame()
    df_open_cm = pd.DataFrame()
    df_ila = pd.DataFrame()
    if is_valid_source(dg_file):
        try:
            xls_dg = pd.ExcelFile(dg_file)
            sheet_target = "Automation Status" if "Automation Status" in xls_dg.sheet_names else xls_dg.sheet_names[0]
            df_status = pd.read_excel(xls_dg, sheet_name=sheet_target)
            for col in df_status.columns: df_status[col] = df_status[col].astype(object)
            ac_col_name = None
            for idx, col in enumerate(df_status.columns):
                c_str = str(col).strip().upper()
                if 'AC' in c_str or 'PDF' in c_str or idx == 28:
                    ac_col_name = col
                    break
            if ac_col_name:
                df_status['Col AC (FSR PDF link)'] = df_status[ac_col_name].apply(lambda x: "" if pd.isna(x) else str(x).strip())
            else:
                if 'Col AC (FSR PDF link)' not in df_status.columns: df_status['Col AC (FSR PDF link)'] = ""
            if 'SAIP ID' in df_status.columns:
                df_status = df_status[df_status['SAIP ID'].notna()]
                df_status['SAIP ID'] = df_status['SAIP ID'].astype(str).str.strip()
        except:
            pass
    return df_status, df_fuel, df_open_cm, df_ila, pd.DataFrame()

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("### DG NOC Portal Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            rec = verify_login(u.strip().lower(), p)
            if rec:
                st.session_state.authenticated = True
                st.session_state.user_info = rec
                st.rerun()
            else: st.error("Invalid Credentials")
    st.stop()

user_data = st.session_state.user_info
detected_excel = DEFAULT_EXCEL
if not os.path.exists(DEFAULT_EXCEL):
    for lf in os.listdir('.'):
        if lf.endswith(('.xlsx', '.xls')) and 'CM' not in lf.upper() and 'ILA' not in lf.upper():
            detected_excel = lf
            break

df_status, _, df_open_cm, df_ila, _ = load_all_trackers(detected_excel, DEFAULT_CM_TRACKER, DEFAULT_ILA)
st.session_state.master_tracker_df = df_status

page = st.radio("Select View:", ["Dashboard", "AI Site Diagnostics"], horizontal=True)
if page == "AI Site Diagnostics":
    st.markdown("## AI Site Diagnostics & FSR Link Viewer")
    sq = st.text_input("Enter SAIP ID:").strip().upper()
    if sq and not df_status.empty:
        m = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)]
        if not m.empty:
            r = m.iloc[0]
            st.markdown(f"### Site ID: {r.get('SAIP ID')} | Status: {r.get('DG Automation Status')}")
            st.markdown(f"**Previous Remarks:** {r.get('Previous Remarks', 'None')}")
            pdf_link = str(r.get('Col AC (FSR PDF link)', '')).strip()
            if pdf_link and pdf_link.lower() not in ['', 'nan', 'none', '0', '0.0']:
                st.markdown(f'<div style="background: rgba(30,41,59,0.9); border: 1px solid #38bdf8; padding: 14px; border-radius: 8px;"><b style="color: #38bdf8;">Col AC (FSR PDF Link):</b><br>{pdf_link}</div>', unsafe_allow_html=True)
                if pdf_link.startswith(('http://', 'https://', 'www.')):
                    t_url = pdf_link if pdf_link.startswith('http') else f"https://{pdf_link}"
                    st.link_button("Open FSR PDF / Google Drive Link", t_url, use_container_width=True)
        else: st.error("Site not found.")
