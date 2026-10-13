import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timezone, timedelta
import os
import hashlib
from io import BytesIO
import re

IST = timezone(timedelta(hours=5, minutes=30))
st.set_page_config(
    page_title="NE Circle Telecom DG Ops Center | Enterprise NOC",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
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
    
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.95) !important;
        border: 2px solid #facc15 !important;
        border-radius: 16px !important;
        padding: 2.2rem 2rem !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.7) !important;
    }
    div[data-testid="stForm"] label p, div[data-testid="stForm"] label span, div[data-testid="stForm"] h2, div[data-testid="stForm"] p {
        color: #facc15 !important; font-weight: 800 !important;
    }
    div[data-testid="stForm"] input {
        color: #ffffff !important; background-color: #1e293b !important; border: 2px solid #facc15 !important; border-radius: 6px !important;
    }

    div[data-testid="stMetric"] label {
        color: #facc15 !important; font-weight: 800 !important;
    }

    div[data-testid="stRadio"] label p, div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #facc15 !important; font-weight: 800 !important; font-size: 14px !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.6);
    }

    div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] summary span, div[data-testid="stExpander"] summary {
        color: #facc15 !important; font-weight: 800 !important; font-size: 14px !important;
    }
    h1, h2, h3, h4, h5, h6 { color: #facc15 !important; font-weight: 800 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }
    .previous-remarks-box { background-color: rgba(15, 23, 42, 0.85) !important; border: 1px solid #facc15 !important; border-radius: 8px !important; padding: 10px 14px !important; color: #ffffff !important; font-size: 14px !important; font-weight: 600 !important; }
    .custom-header-banner { background-color: #0f172a !important; border: 2px solid #facc15 !important; border-radius: 8px !important; padding: 14px 20px !important; margin-top: 6px !important; margin-bottom: 8px !important; }
    .yellow-success-msg { background-color: #1e293b; color: #facc15 !important; border: 1px solid #facc15; padding: 10px 15px; border-radius: 6px; font-weight: 800; margin-top: 10px; margin-bottom: 10px; }
    .status-badge { padding: 4px 10px; border-radius: 9999px; font-weight: 800; font-size: 12px; text-transform: uppercase; display: inline-block; }
    .badge-ok { background-color: #10b981; color: #ffffff; }
    .badge-warn { background-color: #f59e0b; color: #ffffff; }
    .badge-crit { background-color: #dc2626; color: #ffffff; }

    div[data-testid="stTabs"] button p {
        color: #facc15 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: #facc15 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p {
        color: #ffffff !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom-color: #facc15 !important;
    }
    div[data-testid="stTabs"] button:hover p {
        color: #fef08a !important;
    }

    .stApp p, .stApp span, .stApp div, .stApp label, .stMarkdownContainer p, .element-container p {
        color: #ffffff !important;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdownContainer h1, .stMarkdownContainer h2, .stMarkdownContainer h3, .stMarkdownContainer h4 {
        color: #facc15 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1uwOZ9HRC833CfC-hO8Aj1davBQ8qDyXa2f7L0-uu7QQ/export?format=xlsx"
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1uwOZ9HRC833CfC-hO8Aj1davBQ8qDyXa2f7L0-uu7QQ/gviz/tq?tqx=out:csv"
DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio.xlsx"

DEFAULT_ILA = None
if os.path.exists('.'):
    for f in os.listdir('.'):
        if "ILA" in f.upper() and f.endswith(('.xlsx', '.xls')) and not f.startswith('~\$'):
            DEFAULT_ILA = f
            break

BUCKET_LIST = [
    "GCU", "Fuel Sensor", "DG Breakdown", "DG battery", "IPMS",
    "OEM Spare parts", "New DG Req", "AMF Req", "Owner issue",
    "Access issue", "Theft case", "Jio Support", "Other Issue"
]
STATUS_CHOICES = [
    "Automation Ok", "Manual Mode", "DG Breakdown",
    "DG BER", "DG Overload", "Access issue"
]
FUEL_STATUS_CHOICES = ["Ok", "Fuel Sensor faulty"]

def clean_date_str(val):
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).strip()
    if val_str.lower() in ['nat', 'nan', 'none', '', '0']:
        return ""
    try:
        dt = pd.to_datetime(val)
        return dt.strftime('%Y-%m-%d')
    except:
        return val_str.split(' ')[0] if ' ' in val_str else val_str

PASSWORD_CREDENTIALS = {
    hashlib.sha256("Gogoi&6095".encode()).hexdigest(): {"role": "Super Admin", "name": "Tridip Gogoi", "is_admin": True},
    hashlib.sha256("Sukanta@2026".encode()).hexdigest(): {"role": "Super Admin", "name": "SME Operations Desk", "is_admin": True},
    hashlib.sha256("Rintu@2026".encode()).hexdigest(): {"role": "NOC Viewer", "name": "PTPL Operations Desk", "is_admin": False},
    hashlib.sha256("SHQ@2026".encode()).hexdigest(): {"role": "NOC Viewer", "name": "SHQ Operations Desk", "is_admin": False},
    hashlib.sha256("Nipl@2026".encode()).hexdigest(): {"role": "NOC Viewer", "name": "Field Operations Desk", "is_admin": False},
}

def verify_login(password):
    p_hash = hashlib.sha256(password.encode()).hexdigest()
    if p_hash in PASSWORD_CREDENTIALS:
        return PASSWORD_CREDENTIALS[p_hash]
    return None

def extract_link(val):
    if pd.isna(val) or val is None: return ""
    s = str(val).strip()
    if s.lower() in ['', 'nan', 'none', '0', '0.0', 'nat', 'null'] or '00:00:00' in s: return ""
    if 'http://' in s or 'https://' in s:
        for part in s.split():
            if part.startswith('http://') or part.startswith('https://'):
                return part.strip("'")
    if 'drive.google.com' in s:
        return s if s.startswith('http') else f"https://{s}"
    digits = s.replace('.0', '').replace('-', '').replace(' ', '')
    if digits.isdigit() and len(digits) == 10 and digits[0] in ['6', '7', '8', '9']:
        return ""
    return s

def process_dataframe(df_status):
    for col in df_status.columns:
        df_status[col] = df_status[col].astype(object)

    orig_cols = list(df_status.columns)
    c_cm, c_pm = None, None
    for idx, c in enumerate(orig_cols):
        cu = str(c).strip().upper()
        if any(bad in cu for bad in ['CONTACT', 'ACCESS', 'ACTION', 'ACTIVITY', 'REMARK']): continue
        if cu in ['COL AC', 'COLUMN AC', 'AC'] or (('CM' in cu or 'CORRECTIVE' in cu) and any(kw in cu for kw in ['LINK', 'FSR', 'DRIVE', 'URL'])):
            if not c_cm: c_cm = c
        if cu in ['COL AD', 'COLUMN AD', 'AD'] or (('PM' in cu or 'PREVENTIVE' in cu) and any(kw in cu for kw in ['LINK', 'FSR', 'DRIVE', 'URL'])):
            if not c_pm: c_pm = c
    if not c_cm and len(orig_cols) > 28: c_cm = orig_cols[28]
    if not c_pm and len(orig_cols) > 29: c_pm = orig_cols[29]
    if c_cm and c_pm and c_cm == c_pm and len(orig_cols) > 29:
        c_cm = orig_cols[28]
        c_pm = orig_cols[29]

    df_status['Google Drive Link CM'] = df_status[c_cm].apply(extract_link) if c_cm else ""
    df_status['Google Drive Link PM'] = df_status[c_pm].apply(extract_link) if c_pm else ""

    if 'SAIP ID' in df_status.columns:
        df_status = df_status[df_status['SAIP ID'].notna()]
        df_status['SAIP ID'] = df_status['SAIP ID'].astype(str).str.strip()
        df_status = df_status[~df_status['SAIP ID'].str.lower().isin(['', 'nan', 'none', 'total', '0', 'null'])]
    if 'DG Make' in df_status.columns:
        df_status = df_status[df_status['DG Make'].notna()]
        df_status['DG Make'] = df_status['DG Make'].astype(str).str.strip()
    if 'JC' in df_status.columns:
        df_status['JC'] = df_status['JC'].astype(str).str.strip()
    if 'State' in df_status.columns:
        df_status['State'] = df_status['State'].astype(str).str.strip()
    if 'Bucket' in df_status.columns:
        df_status['Bucket'] = df_status['Bucket'].astype(str).str.strip()
        df_status['Bucket'] = df_status['Bucket'].apply(lambda x: None if str(x).lower() in ['nan', 'none', '', 'nat'] else x)
    return df_status

@st.cache_data(ttl=5)
def load_google_sheet_tracker():
    if 'persistent_master_df' in st.session_state and st.session_state.persistent_master_df is not None and not st.session_state.persistent_master_df.empty:
        st.session_state['data_source_mode'] = "Uploaded Excel File"
        return st.session_state.persistent_master_df

    df_status = pd.DataFrame()
    source_status = "Google Sheet Live"
    success = False

    try:
        csv_url = f"{GOOGLE_SHEET_CSV}&cb={datetime.now().timestamp()}"
        df_status = pd.read_csv(csv_url)
        if df_status is not None and not df_status.empty:
            success = True
    except: pass

    if not success:
        try:
            xls_dg = pd.ExcelFile(GOOGLE_SHEET_URL)
            sheet_target = "Automation Status" if "Automation Status" in xls_dg.sheet_names else xls_dg.sheet_names[0]
            df_status = pd.read_excel(xls_dg, sheet_name=sheet_target)
            if df_status is not None and not df_status.empty:
                success = True
        except: pass

    if not success:
        source_status = "Local File (Backup)"
        if os.path.exists(DEFAULT_EXCEL):
            try:
                xls_local = pd.ExcelFile(DEFAULT_EXCEL)
                s_name = "Automation Status" if "Automation Status" in xls_local.sheet_names else xls_local.sheet_names[0]
                df_status = pd.read_excel(xls_local, sheet_name=s_name)
                if df_status is not None and not df_status.empty:
                    success = True
            except: pass

    if df_status is None or df_status.empty:
        df_status = pd.DataFrame()
    else:
        df_status = process_dataframe(df_status)

    st.session_state['data_source_mode'] = source_status
    return df_status

def load_ila_tracker():
    df_ila = pd.DataFrame()
    if DEFAULT_ILA and os.path.exists(DEFAULT_ILA):
        try:
            xls_ila = pd.ExcelFile(DEFAULT_ILA)
            ila_sheet = "IPMS Site Automation Status" if "IPMS Site Automation Status" in xls_ila.sheet_names else xls_ila.sheet_names[0]
            df_ila = pd.read_excel(xls_ila, sheet_name=ila_sheet)
            for col in df_ila.columns: df_ila[col] = df_ila[col].astype(object)
            if 'Sap ID' in df_ila.columns:
                df_ila = df_ila[df_ila['Sap ID'].notna()]
                df_ila['Sap ID'] = df_ila['Sap ID'].astype(str).str.strip()
        except: pass
    return df_ila

def save_master_to_disk():
    try:
        if "master_tracker_df" in st.session_state and not st.session_state.master_tracker_df.empty:
            with pd.ExcelWriter(DEFAULT_EXCEL, engine='openpyxl') as writer:
                st.session_state.master_tracker_df.to_excel(writer, sheet_name="Automation Status", index=False)
                if "ila_tracker_df" in st.session_state and not st.session_state.ila_tracker_df.empty:
                    st.session_state.ila
