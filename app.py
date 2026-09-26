import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import hashlib
from io import BytesIO
import urllib.parse
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NE Circle Telecom DG Ops Center | Enterprise NOC",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom Corporate NOC Styling with High Contrast, Telecom Background & Custom Login UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.88)), 
                    url("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .login-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(226, 232, 240, 0.8);
        max-width: 480px;
        margin: 2rem auto;
    }
    .login-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .login-header h2 {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
        margin-bottom: 0.25rem !important;
        text-shadow: none !important;
    }
    .login-header p {
        color: #64748b !important;
        font-size: 0.9rem !important;
    }

    button[data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 8px 16px !important;
        margin-right: 4px !important;
    }
    button[data-baseweb="tab"] div p,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.25) !important;
        border-bottom: 3px solid #38bdf8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p,
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
    [data-testid="stHeader"] *,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8) !important;
    }
    .stMarkdown p, .stMarkdown span, .stCaption, [data-testid="stCaptionContainer"] {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] * {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    section[data-testid="stSidebar"] * {
        color: #0f172a !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        text-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    .stTextInput label, .stSelectbox label, .stDateInput label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploadDropzone"] * {
        color: #0f172a !important;
    }

    .status-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 11px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-ok { background-color: #dcfce7; color: #15803d !important; border: 1px solid #bbf7d0; }
    .badge-warn { background-color: #fef9c3; color: #854d0e !important; border: 1px solid #fef08a; }
    .badge-crit { background-color: #fee2e2; color: #b91c1c !important; border: 1px solid #fecaca; }

    .auto-docket-box {
        background-color: rgba(239, 246, 255, 0.98);
        border: 1px solid #93c5fd;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #0f172a !important;
    }
    .auto-docket-box * { color: #0f172a !important; }
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
</style>
""", unsafe_allow_html=True)

DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio_24th_Sep'26.xlsx"

BUCKET_LIST = [
    "GCU", "Fuel Sensor", "DG Breakdown", "DG battery", "IPMS",
    "OEM Spare parts", "New DG Req", "AMF Req", "Owner issue",
    "Access issue", "Theft case", "Jio Support", "Other Issue"
]

STATUS_CHOICES = [
    "Automation Ok", "Manual Mode", "DG Breakdown",
    "DG BER", "DG Overload", "Access issue"
]

def clean_date_str(val):
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).strip()
    if val_str.lower() in ['nat', 'nan', 'none', '', '0']:
        return ""
    try:
        dt = pd.to_datetime(val)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return val_str.split(' ')[0] if ' ' in val_str else val_str

def to_date_obj(val, fallback=None):
    if pd.isna(val) or val is None or str(val).strip().lower() in ['', 'nat', 'nan', 'none', '0']:
        return fallback or date.today()
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return fallback or date.today()

# --- MULTI-USER ROLE AUTHENTICATION SETUP ---
USER_ROLES = {
    "admin": {
        "password_hash": hashlib.sha256("admin@123".encode()).hexdigest(),
        "role": "Super Admin / Operations Head",
        "name": "Circle Operations Head",
        "access": ["all"]
    },
    "trt": {
        "password_hash": hashlib.sha256("trt@123".encode()).hexdigest(),
        "role": "TRT / Field Operations Lead",
        "name": "North East Field TRT",
        "access": ["edit_only"]
    },
    "viewer": {
        "password_hash": hashlib.sha256("viewer@123".encode()).hexdigest(),
        "role": "NOC Viewer / Executive",
        "name": "Circle Audit Desk",
        "access": ["read_only"]
    }
}

def verify_login(username, password):
    if username in USER_ROLES:
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        if hashed_pwd == USER_ROLES[username]["password_hash"]:
            return USER_ROLES[username]
    return None

def is_valid_source(src):
    if hasattr(src, 'read'): return True
    if isinstance(src, str) and os.path.exists(src): return True
    return False

@st.cache_data
def load_all_trackers(dg_file, cm_file, cr_file=None):
    df_status = pd.DataFrame()
    df_fuel = pd.DataFrame()
    df_open_cm = pd.DataFrame()
    df_cr_data = pd.DataFrame()
    
    if is_valid_source(dg_file):
        try:
            xls_dg = pd.ExcelFile(dg_file)
            if "Automation Status" in xls_dg.sheet_names:
                df_status = pd.read_excel(xls_dg, sheet_name="Automation Status")
                for d_col in ['Open Date', 'Last Closed date', 'Present Docket raise Date', 'Previous Docket raise Date', 'Last Closed date.1']:
                    if d_col in df_status.columns:
                        df_status[d_col] = df_status[d_col].apply(clean_date_str)
            if "Fuel Sensor faulty" in xls_dg.sheet_names:
                df_fuel = pd.read_excel(xls_dg, sheet_name="Fuel Sensor faulty")
                if 'COMPLAINT LOGGIN DATE' in df_fuel.columns:
                    df_fuel['COMPLAINT LOGGIN DATE'] = df_fuel['COMPLAINT LOGGIN DATE'].apply(clean_date_str)
        except Exception as e:
            st.error(f"Error loading DG tracker: {e}")

    if is_valid_source(cm_file):
        try:
            xls_cm = pd.ExcelFile(cm_file)
            if "Open Site" in xls_cm.sheet_names:
                df_open_cm = pd.read_excel(xls_cm, sheet_name="Open Site")
            elif "CM Tracket" in xls_cm.sheet_names:
                temp_cm = pd.read_excel(xls_cm, sheet_name="CM Tracket")
                df_open_cm = temp_cm[temp_cm['STATUS'].astype(str).str.lower() == 'open']
            
            if not df_open_cm.empty and 'COMPLAINT LOGGIN DATE' in df_open_cm.columns:
                df_open_cm['COMPLAINT LOGGIN DATE'] = df_open_cm['COMPLAINT LOGGIN DATE'].apply(clean_date_str)
        except Exception as e:
            st.warning(f"Note on CM tracker: {e}")

    if cr_file and is_valid_source(cr_file):
        try:
            xls_cr = pd.ExcelFile(cr_file)
            for s in xls_cr.sheet_names:
                if "TRACKER" in s.upper():
                    df_cr_data = pd.read_excel(xls_cr, sheet_name=s, header=2)
                    break
        except Exception:
            pass

    return df_status, df_fuel, df_open_cm, df_cr_data

def ai_capture_o_to_ab(site_id, df_open_cm, df_status, df_cr_data=None):
    clean_id = str(site_id).strip().upper() if site_id else ""
    res = {
        "JC": "", "Col_O_Fuel_Sensor_Status": "Ok", "Col_P_Docket_no": "",
        "Col_Q_Open_Date": "", "Col_R_Last_Closed_date": "", "Col_S_DG_Automation_Status": "Automation Ok",
        "Col_T_Present_Remarks": "", "Col_U_Bucket": "", "Col_V_Present_Docket_No": "",
        "Col_W_Present_Docket_raise_Date": "", "Col_X_Aging_Days": 0, "Col_Y_Timeline": "",
        "Col_Z_Previous_Remarks": "", "Col_AA_Previous_Docket_No": "", "Col_AB_Previous_Docket_raise_Date": "",
        "source": "None"
    }
    if not clean_id:
        return res

    if not df_status.empty and 'SAIP ID' in df_status.columns:
        dg_match = df_status[df_status['SAIP ID'].astype(str).str.strip().str.upper() == clean_id]
        if not dg_match.empty:
            prev_row = dg_match.iloc[0]
            res["JC"] = str(prev_row.get("JC", "")).strip()
            res["Col_O_Fuel_Sensor_Status"] = str(prev_row.get("Fuel Sensor Status", "Ok")).strip()
            res["Col_P_Docket_no"] = str(prev_row.get("Docket no.", "")).strip()
            res["Col_Q_Open_Date"] = clean_date_str(prev_row.get("Open Date", ""))
            res["Col_R_Last_Closed_date"] = clean_date_str(prev_row.get("Last Closed date", ""))
            res["Col_S_DG_Automation_Status"] = str(prev_row.get("DG Automation Status", "Manual Mode")).strip()
            res["Col_T_Present_Remarks"] = str(prev_row.get("Present Remarks", "")).strip()
            res["Col_U_Bucket"] = str(prev_row.get("Bucket", "")).strip()
            res["Col_V_Present_Docket_No"] = str(prev_row.get("Present Docket No.", "")).strip()
            res["Col_W_Present_Docket_raise_Date"] = clean_date_str(prev_row.get("Present Docket raise Date", ""))
            res["Col_X_Aging_Days"] = prev_row.get("Aging (Day's)", 0)
            res["Col_Y_Timeline"] = str(prev_row.get("Timeline", "")).strip()
            res["Col_Z_Previous_Remarks"] = str(prev_row.get("Previous Remarks", "")).strip()
            res["Col_AA_Previous_Docket_No"] = str(prev_row.get("Previous Docket No.", "")).strip()
            res["Col_AB_Previous_Docket_raise_Date"] = clean_date_str(prev_row.get("Previous Docket raise Date", ""))
            res["source"] = "DG Master Tracker"

    if not df_open_cm.empty and 'SITE ID' in df_open_cm.columns:
        cm_match = df_open_cm[df_open_cm['SITE ID'].astype(str).str.strip().str.upper() == clean_id]
        if not cm_match.empty:
            cm_row = cm_match.iloc[0]
            if not res["JC"] and pd.notna(cm_row.get("JC")):
                res["JC"] = str(cm_row.get("JC")).strip()
            
            new_docket = str(cm_row.get("DOCKET NUMBER", "")).strip()
            new_complaint = str(cm_row.get("NATURE OF COMPLAINT", "")).strip()
            new_bucket = str(cm_row.get("Bucket", "")).strip()
            new_timeline = str(cm_row.get("Timeline", "")).strip()
            new_aging = cm_row.get("Ageing ", 0)
            date_str = clean_date_str(cm_row.get("COMPLAINT LOGGIN DATE", ""))

            if res["Col_V_Present_Docket_No"] and res["Col_V_Present_Docket_No"] != new_docket and res["Col_V_Present_Docket_No"].lower() != 'nan':
                res["Col_AA_Previous_Docket_No"] = res["Col_V_Present_Docket_No"]
                res["Col_AB_Previous_Docket_raise_Date"] = res["Col_W_Present_Docket_raise_Date"]
                res["Col_Z_Previous_Remarks"] = res["Col_T_Present_Remarks"]

            res["Col_V_Present_Docket_No"] = new_docket
            res["Col_W_Present_Docket_raise_Date"] = date_str
            res["Col_T_Present_Remarks"] = new_complaint
            res["Col_X_Aging_Days"] = new_aging
            res["Col_Y_Timeline"] = new_timeline if new_timeline.lower() != 'nan' else ""
            
            if "FUEL" in new_complaint.upper() or "FUEL" in new_bucket.upper():
                res["Col_U_Bucket"] = "Fuel Sensor"
            elif "GCU" in new_complaint.upper() or "GCU" in new_bucket.upper():
                res["Col_U_Bucket"] = "GCU"
            elif "BATTERY" in new_complaint.upper():
                res["Col_U_Bucket"] = "DG battery"
            elif "AMF" in new_complaint.upper() or "AMF" in new_bucket.upper():
                res["Col_U_Bucket"] = "AMF Req"
            elif new_bucket and new_bucket.lower() != 'nan':
                res["Col_U_Bucket"] = new_bucket
            else:
                res["Col_U_Bucket"] = "DG Breakdown"

            if "fuel" in new_complaint.lower() or "fuel" in new_bucket.lower():
                res["Col_O_Fuel_Sensor_Status"] = "Fuel Sensor faulty"
                res["Col_P_Docket_no"] = new_docket
                res["Col_Q_Open_Date"] = date_str
            
            res["Col_S_DG_Automation_Status"] = "DG Breakdown" if "breakdown" in new_complaint.lower() else "Manual Mode"
            res["source"] = "CM Tracker (Open Site)"

    for k, v in res.items():
        if str(v).lower() == 'nan' or str(v) == 'nat':
            res[k] = ""
    return res

def auto_sync_edited_data_to_engine(df_target, df_open_cm_data, df_cr):
    if df_target.empty: return df_target
    updated = df_target.copy()
    for idx, row in updated.iterrows():
        s_id = row.get("SAIP ID")
        cap = ai_capture_o_to_ab(s_id, df_open_cm_data, updated, df_cr)
        if cap["source"] != "None":
            if pd.isna(updated.at[idx, "Fuel Sensor Status"]) or updated.at[idx, "Fuel Sensor Status"] == "":
                updated.at[idx, "Fuel Sensor Status"] = cap["Col_O_Fuel_Sensor_Status"]
            if (pd.isna(updated.at[idx, "Docket no."]) or updated.at[idx, "Docket no."] == "") and cap["Col_P_Docket_no"]:
                updated.at[idx, "Docket no."] = cap["Col_P_Docket_no"]
            if (pd.isna(updated.at[idx, "Open Date"]) or updated.at[idx, "Open Date"] == "") and cap["Col_Q_Open_Date"]:
                updated.at[idx, "Open Date"] = clean_date_str(cap["Col_Q_Open_Date"])
            if (pd.isna(updated.at[idx, "Present Docket No."]) or updated.at[idx, "Present Docket No."] == "") and cap["Col_V_Present_Docket_No"]:
                updated.at[idx, "Present Docket No."] = cap["Col_V_Present_Docket_No"]
            if (pd.isna(updated.at[idx, "Present Docket raise Date"]) or updated.at[idx, "Present Docket raise Date"] == "") and cap["Col_W_Present_Docket_raise_Date"]:
                updated.at[idx, "Present Docket raise Date"] = clean_date_str(cap["Col_W_Present_Docket_raise_Date"])
    return updated

def clear_site_active_fault_data(site_id, df_target):
    if df_target.empty or not site_id: return df_target
    updated = df_target.copy()
    clean_id = str(site_id).strip().upper()
    match_idx = updated[updated["SAIP ID"].astype(str).str.strip().str.upper() == clean_id].index
    if not match_idx.empty:
        i = match_idx[0]
        if "Fuel Sensor Status" in updated.columns: updated.at[i, "Fuel Sensor Status"] = "Ok"
        if "Docket no." in updated.columns: updated.at[i, "Docket no."] = ""
        if "Open Date" in updated.columns: updated.at[i, "Open Date"] = ""
        if "DG Automation Status" in updated.columns: updated.at[i, "DG Automation Status"] = "Automation Ok"
        if "Present Remarks" in updated.columns: updated.at[i, "Present Remarks"] = ""
        if "Bucket" in updated.columns: updated.at[i, "Bucket"] = None
        if "Present Docket No." in updated.columns: updated.at[i, "Present Docket No."] = ""
        if "Present Docket raise Date" in updated.columns: updated.at[i, "Present Docket raise Date"] = ""
        if "Aging (Day's)" in updated.columns: updated.at[i, "Aging (Day's)"] = 0
    return updated

def execute_tt_close_shift_to_y_ab(site_id, closure_remarks, closure_date_str, df_target):
    if df_target.empty or not site_id: return df_target
    updated = df_target.copy()
    clean_id = str(site_id).strip().upper()
    match_idx = updated[updated["SAIP ID"].astype(str).str.strip().str.upper() == clean_id].index
    if not match_idx.empty:
        i = match_idx[0]
        cur_docket = str(updated.at[i, "Present Docket No."]) if pd.notna(updated.at[i, "Present Docket No."]) else ""
        cur_raise_date = clean_date_str(updated.at[i, "Present Docket raise Date"]) if pd.notna(updated.at[i, "Present Docket raise Date"]) else ""
        cur_remarks = str(updated.at[i, "Present Remarks"]) if pd.notna(updated.at[i, "Present Remarks"]) else ""

        if "Timeline" in updated.columns: updated.at[i, "Timeline"] = "Closed / Resolved"
        if "Previous Remarks" in updated.columns: updated.at[i, "Previous Remarks"] = f"{cur_remarks} | Closed: {closure_remarks}".strip(" |")
        if "Previous Docket No." in updated.columns: updated.at[i, "Previous Docket No."] = cur_docket
        if "Previous Docket raise Date" in updated.columns: updated.at[i, "Previous Docket raise Date"] = cur_raise_date

        if "Last Closed date" in updated.columns: updated.at[i, "Last Closed date"] = closure_date_str
        if "Last Closed date.1" in updated.columns: updated.at[i, "Last Closed date.1"] = closure_date_str
        if "DG Automation Status" in updated.columns: updated.at[i, "DG Automation Status"] = "Automation Ok"
        if "Present Remarks" in updated.columns: updated.at[i, "Present Remarks"] = "Automation Restored / Closed"
        if "Bucket" in updated.columns: updated.at[i, "Bucket"] = None
        if "Present Docket No." in updated.columns: updated.at[i, "Present Docket No."] = ""
        if "Present Docket raise Date" in updated.columns: updated.at[i, "Present Docket raise Date"] = ""
        if "Aging (Day's)" in updated.columns: updated.at[i, "Aging (Day's)"] = 0
        if "Fuel Sensor Status" in updated.columns: updated.at[i, "Fuel Sensor Status"] = "Ok"
        if "Docket no." in updated.columns: updated.at[i, "Docket no."] = ""
        if "Open Date" in updated.columns: updated.at[i, "Open Date"] = ""
    return updated

# =========================================================
# 🔒 SECURE LOGIN AUTHENTICATION GATEWAY
# =========================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None

if not st.session_state.authenticated:
    _, col_login, _ = st.columns([1, 1.3, 1])
    with col_login:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <h2>⚡ Telecom NOC Portal</h2>
                <p>North East Circle | Role-Based Authentication Gateway</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("admin_login_form"):
            input_user = st.text_input("Username", placeholder="admin / trt / viewer")
            input_pass = st.text_input("Password", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("Authenticate & Enter NOC Portal", use_container_width=True, type="primary")

            if submit_login:
                user_record = verify_login(input_user.strip().lower(), input_pass)
                if user_record:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_record
                    st.session_state.username = input_user.strip().lower()
                    st.success(f"Access Granted as {user_record['role']}! Loading...")
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid Master Credentials")

        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; font-size: 12px; color: #475569;">
            <b>Access Credentials:</b><br>
            • <b>Operations Head:</b> <code>admin</code> / <code>admin@123</code><br>
            • <b>TRT Field Engineer:</b> <code>trt</code> / <code>trt@123</code><br>
            • <b>NOC Viewer (Read-only):</b> <code>viewer</code> / <code>viewer@123</code>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================================================
# 🛡️ AUTHENTICATED WORKSPACE & OPERATIONS
# =========================================================
user_data = st.session_state.user_info
admin_name = user_data["name"]
admin_role = user_data["role"]
user_perms = user_data["access"]

st.sidebar.markdown(f"### 🛡️ Enterprise NOC Hub")
st.sidebar.markdown(f"**Operator:** `{admin_name}`")
st.sidebar.markdown(f"**Role:** `{admin_role}`")
if st.sidebar.button("🚪 Log Out Session", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown("### 📂 Data Pipeline Synchronization")
uploaded_cm = st.sidebar.file_uploader("1. CM Tracker (Open Site)", type=["xlsx", "xls"])
uploaded_dg = st.sidebar.file_uploader("2. DG Automation Master Tracker", type=["xlsx", "xls"])
uploaded_cr = st.sidebar.file_uploader("3. Complaint Register (Optional)", type=["xlsx", "xls"])

cm_source = uploaded_cm if uploaded_cm is not None else DEFAULT_CM_TRACKER
dg_source = uploaded_dg if uploaded_dg is not None else DEFAULT_EXCEL
cr_source = uploaded_cr if uploaded_cr is not None else None

df_status_raw, df_fuel_raw, df_open_cm, df_cr_data = load_all_trackers(dg_source, cm_source, cr_source)

if "master_tracker_df" not in st.session_state or st.session_state.master_tracker_df.empty:
    st.session_state.master_tracker_df = df_status_raw.copy()

if "fuel_tracker_df" not in st.session_state:
    st.session_state.fuel_tracker_df = df_fuel_raw.copy()

df_status = st.session_state.master_tracker_df
df_fuel = st.session_state.fuel_tracker_df

if not df_open_cm.empty:
    st.sidebar.success(f"CM Tracker: {len(df_open_cm)} Open Incidents Synced")

if not df_status.empty and "Aging (Day's)" in df_status.columns:
    df_status['Aging_Num'] = pd.to_numeric(df_status["Aging (Day's)"], errors='coerce')
    bins = [-1, 0, 7, 15, 30, 60, 90, 100000]
    labels = ['0 Days', '1-7 Days', '8-15 Days', '16-30 Days', '31-60 Days', '61-90 Days', '>90 Days']
    df_status['Aging_Bracket'] = pd.cut(df_status['Aging_Num'], bins=bins, labels=labels)

page = st.sidebar.radio("NOC Operations Navigation:", [
    "📊 Executive Control Center",
    "🗺️ GPS Telecom Tower Live Map",
    "⚡ O to AB Automated Sync Engine",
    "⚙️ Fleet Analytics & Problem Buckets",
    "⛽ Fuel Sensor Telemetry",
    "⏳ Critical Aging & Escalations",
    "📲 WhatsApp & SMS Dispatcher",
    "📑 Daily MIS Report Generator",
    "✏️ In-Portal Master Tracker Editor",
    "🔍 AI Site Diagnostics"
])

# ---------------------------------------------------------
# 1. EXECUTIVE CONTROL CENTER
# ---------------------------------------------------------
if page == "📊 Executive Control Center":
    st.markdown("## ⚡ North East Circle - DG Operations Control Center")
    st.caption(f"System State: Operational | Active Operator: **{admin_name} ({admin_role})** | Refreshed: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

    if not df_status.empty:
        total_sites = len(df_status)
        auto_ok = len(df_status[df_status['DG Automation Status'] == 'Automation Ok'])
        manual_mode = len(df_status[df_status['DG Automation Status'] == 'Manual Mode'])

        k1, k2, k3 = st.columns(3)
        k1.metric("Network Base (Total Sites)", f"{total_sites:,}", "Monitored Fleet")
        k2.metric("Automation Rate", f"{round((auto_ok/total_sites)*100, 1)}%", f"{auto_ok} Sites Online")
        k3.metric("Manual Mode Alerts", manual_mode, f"-{round((manual_mode/total_sites)*100, 1)}%", delta_color="inverse")

        st.markdown("---")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.subheader("Circle JC Wise Automation Health")
            fig_bar = px.histogram(
                df_status, x="JC", color="DG Automation Status", barmode="group",
                color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#6366f1"]
            )
            fig_bar.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#ffffff")
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.subheader("DG Make Fleet Allocation")
            if "DG Make" in df_status.columns:
                fig_donut = px.pie(df_status, names="DG Make", hole=0.58, color_discrete_sequence=px.colors.qualitative.Safe)
                fig_donut.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="#ffffff")
                st.plotly_chart(fig_donut, use_container_width=True)

# ---------------------------------------------------------
# 2. GPS TELECOM TOWER LIVE MAP TRACKER
# ---------------------------------------------------------
elif page == "🗺️ GPS Telecom Tower Live Map":
    st.markdown("## 🗺️ North East Circle - GPS Telecom Tower Live Map")
    st.caption("Live geographical radar tracking towers across Assam, Meghalaya, Tripura, Mizoram, Nagaland, Manipur & Arunachal Pradesh.")

    if not df_status.empty:
        jc_map_filter = st.selectbox("Select Circle JC for Map Radar:", ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique()]))
        map_df = df_status.copy() if jc_map_filter == "All JCs" else df_status[df_status['JC'] == jc_map_filter].copy()

        NE_COORDS = {
            "Guwahati": (26.1445, 91.7362), "Shillong": (25.5788, 91.8933),
            "Silchar": (24.8170, 92.7960), "Dibrugarh": (27.4728, 94.9120),
            "Jorhat": (26.7509, 94.2037), "Agartala": (23.8315, 91.2868),
            "Aizawl": (23.7271, 92.7176), "Dimapur": (25.9094, 93.7266),
            "Kohima": (25.6751, 94.1086), "Imphal": (24.8170, 93.9368),
            "Itanagar": (27.0844, 93.6053), "Tezpur": (26.6528, 92.7926)
        }

        has_lat = "Latitude" in map_df.columns and "Longitude" in map_df.columns
        if not has_lat:
            np.random.seed(42)
            lats, lons = [], []
            for _, r in map_df.iterrows():
                jc = str(r.get("JC", "")).strip()
                center = NE_COORDS.get(jc, (26.2006, 92.9376))
                lats.append(center[0] + np.random.uniform(-0.15, 0.15))
                lons.append(center[1] + np.random.uniform(-0.15, 0.15))
            map_df["lat"] = lats
            map_df["lon"] = lons
        else:
            map_df["lat"] = pd.to_numeric(map_df["Latitude"], errors='coerce')
            map_df["lon"] = pd.to_numeric(map_df["Longitude"], errors='coerce')
            map_df = map_df.dropna(subset=["lat", "lon"])

        def get_color(row):
            st_val = str(row.get("DG Automation Status", ""))
            fs_val = str(row.get("Fuel Sensor Status", ""))
            if "Breakdown" in st_val or fs_val == "Fuel Sensor faulty": return "Red (Severe Fault)"
            if st_val == "Manual Mode": return "Amber (Manual Mode)"
            return "Green (Automation Ok)"

        map_df["Health_Flag"] = map_df.apply(get_color, axis=1)

        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat", lon="lon",
            color="Health_Flag",
            hover_name="SAIP ID",
            hover_data={
                "JC": True, "DG Automation Status": True, 
                "Bucket": True, "Present Docket No.": True,
                "lat": False, "lon": False
            },
            color_discrete_map={
                "Red (Severe Fault)": "#ef4444",
                "Amber (Manual Mode)": "#f59e0b",
                "Green (Automation Ok)": "#10b981"
            },
            zoom=6.5,
            height=600
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(15,23,42,0.85)", font=dict(color="#ffffff"))
        )
        st.plotly_chart(fig_map, use_container_width=True)

# ---------------------------------------------------------
# 3. O TO AB AUTOMATED SYNC ENGINE
# ---------------------------------------------------------
elif page == "⚡ O to AB Automated Sync Engine":
    st.markdown("## ⚡ Master Automation Tracker: Col O to AB Auto-Update Engine")
    st.caption("AI-driven pipeline mapping CM Tracker (`Open Site`) directly into Col O to AB of `Automation Status`.")

    if df_status.empty:
        st.warning("Please verify that 'DG Auto-Update Automation Tracker 26.xlsx' is present or uploaded.")
    else:
        st.markdown(f"""
        <div class="auto-docket-box">
            <b>Pipeline Diagnostic:</b> Master Tracker: <b>{len(df_status):,} sites</b> | CM Open Incidents: <b>{len(df_open_cm)} records detected</b>.<br>
            ⚡ <b>Live Integration Active:</b> All edits committed from the <i>In-Portal Master Tracker Editor</i> reflect here automatically in real-time.
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Execute Col O to AB Batch Synchronization", type="primary", use_container_width=True):
            with st.spinner("Processing telemetry reconciliation and populating Col O to AB..."):
                updated_df = df_status.copy()
                sync_count = 0
                for idx, row in updated_df.iterrows():
                    s_id = row.get("SAIP ID")
                    cap = ai_capture_o_to_ab(s_id, df_open_cm, df_status, df_cr_data)
                    if cap["source"] != "None":
                        sync_count += 1
                        updated_df.at[idx, "Fuel Sensor Status"] = cap["Col_O_Fuel_Sensor_Status"]
                        if cap["Col_P_Docket_no"]: updated_df.at[idx, "Docket no."] = cap["Col_P_Docket_no"]
                        if cap["Col_Q_Open_Date"]: updated_df.at[idx, "Open Date"] = clean_date_str(cap["Col_Q_Open_Date"])
                        if cap["Col_S_DG_Automation_Status"]: updated_df.at[idx, "DG Automation Status"] = cap["Col_S_DG_Automation_Status"]
                        if cap["Col_T_Present_Remarks"]: updated_df.at[idx, "Present Remarks"] = cap["Col_T_Present_Remarks"]
                        if cap["Col_U_Bucket"]: updated_df.at[idx, "Bucket"] = cap["Col_U_Bucket"]
                        if cap["Col_V_Present_Docket_No"]: updated_df.at[idx, "Present Docket No."] = cap["Col_V_Present_Docket_No"]
                        if cap["Col_W_Present_Docket_raise_Date"]: updated_df.at[idx, "Present Docket raise Date"] = clean_date_str(cap["Col_W_Present_Docket_raise_Date"])
                        if cap["Col_X_Aging_Days"]: updated_df.at[idx, "Aging (Day's)"] = cap["Col_X_Aging_Days"]
                        if cap["Col_Y_Timeline"]: updated_df.at[idx, "Timeline"] = cap["Col_Y_Timeline"]
                        if cap["Col_Z_Previous_Remarks"]: updated_df.at[idx, "Previous Remarks"] = cap["Col_Z_Previous_Remarks"]
                        if cap["Col_AA_Previous_Docket_No"]: updated_df.at[idx, "Previous Docket No."] = cap["Col_AA_Previous_Docket_No"]
                        if cap["Col_AB_Previous_Docket_raise_Date"]: updated_df.at[idx, "Previous Docket raise Date"] = clean_date_str(cap["Col_AB_Previous_Docket_raise_Date"])

                st.session_state.master_tracker_df = updated_df
                st.success(f"Batch Sync Completed! Reconciled {sync_count} sites matching CM Tracker entries.")

        display_cols = [
            'SAIP ID', 'Fuel Sensor Status', 'Docket no.', 'Open Date', 
            'DG Automation Status', 'Present Remarks', 'Bucket', 
            'Present Docket No.', 'Present Docket raise Date', "Aging (Day's)", 'Timeline',
            'Previous Remarks', 'Previous Docket No.', 'Previous Docket raise Date'
        ]
        valid_cols = [c for c in display_cols if c in df_status.columns]
        st.markdown("#### Live Master Tracker Pipeline Status (Col O to AB)")
        st.dataframe(df_status[valid_cols].head(50), use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_status.to_excel(writer, sheet_name="Automation Status", index=False)
            if not df_fuel.empty:
                df_fuel.to_excel(writer, sheet_name="Fuel Sensor faulty", index=False)
        st.download_button(
            label="📥 Download Master Updated Tracker (Col O to AB Synced .xlsx)",
            data=output.getvalue(),
            file_name=f"Updated_DG_Automation_Tracker_26_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ---------------------------------------------------------
# 4. FLEET ANALYTICS & PROBLEM BUCKETS
# ---------------------------------------------------------
elif page == "⚙️ Fleet Analytics & Problem Buckets":
    st.markdown("## ⚙️ Fleet Automation Classification & Root-Cause Analysis")
    st.caption("JC-wise breakdown of network automation health, problem buckets, and docket fulfillment statuses.")

    jc_options = ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique()])
    selected_fleet_jc = st.selectbox("Select JC Circle:", jc_options)

    filtered_status = df_status if selected_fleet_jc == "All JCs" else df_status[df_status['JC'] == selected_fleet_jc]
    valid_bucket = filtered_status[filtered_status['Bucket'].notna()]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"#### Status Summary ({selected_fleet_jc})")
        stat_summary = filtered_status['DG Automation Status'].value_counts(dropna=False).reset_index()
        stat_summary.columns = ['Status Category', 'Site Count']
        st.dataframe(stat_summary, use_container_width=True, hide_index=True)
    with col2:
        st.markdown(f"#### Bucket Distribution ({selected_fleet_jc})")
        if not valid_bucket.empty:
            b_summary = valid_bucket['Bucket'].value_counts().reset_index()
            b_summary.columns = ['Root-Cause Bucket', 'Incidents']
            fig_b = px.bar(b_summary, x="Root-Cause Bucket", y="Incidents", text="Incidents", color="Incidents", color_continuous_scale="Blues")
            fig_b.update_layout(height=320, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#ffffff", margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_b, use_container_width=True)
        else:
            st.info("No active problem bucket recorded for this selection.")

# ---------------------------------------------------------
# 5. FUEL SENSOR TELEMETRY
# ---------------------------------------------------------
elif page == "⛽ Fuel Sensor Telemetry":
    st.markdown("## ⛽ Fuel Sensor Fault Telemetry")
    st.caption("Active fuel sensor fault distribution cross-tabulated strictly by JC, DG Make, and KVA rating.")

    if not df_fuel.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Faulty Sensors", len(df_fuel))
        c2.metric("Most Affected JC", df_fuel['JC'].mode()[0] if 'JC' in df_fuel.columns else "N/A", f"{df_fuel['JC'].value_counts().max()} Sites")
        c3.metric("Primary Fault Make", df_fuel['DG MAKE'].mode()[0] if 'DG MAKE' in df_fuel.columns else "N/A")
        c4.metric("Primary Fault Rating", df_fuel['KVA'].mode()[0] if 'KVA' in df_fuel.columns else "N/A")

        st.markdown("---")
        ct_fuel_detailed = pd.crosstab([df_fuel['JC'], df_fuel['DG MAKE']], df_fuel['KVA'], margins=True, margins_name="Total")
        st.dataframe(ct_fuel_detailed, use_container_width=True)
    else:
        st.info("No active fuel sensor faults detected in the current tracker.")

# ---------------------------------------------------------
# 6. CRITICAL AGING & ESCALATIONS
# ---------------------------------------------------------
elif page == "⏳ Critical Aging & Escalations":
    st.markdown("## ⏳ Critical Aging Escalation Radar (>90 Days)")
    st.caption("Active unresolved telecom site alarms requiring urgent intervention.")

    aging_valid = df_status[df_status['Aging_Num'].notna()].copy()
    crit_df = aging_valid[aging_valid['Aging_Num'] > 90].copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Delayed Sites", len(aging_valid), "Active Incidents")
    m2.metric("Severe Delays (>90 Days)", len(crit_df), "Critical Escalations")
    m3.metric("Most Affected JC", crit_df['JC'].mode()[0] if not crit_df.empty else "N/A")
    m4.metric("Maximum Delay", f"{int(aging_valid['Aging_Num'].max())} Days")

    disp_cols = ['SAIP ID', 'JC', 'Bucket', 'DG Make', 'Present Docket No.', 'Aging_Num', 'Present Remarks', 'Supervisor Name', 'Contact No.']
    valid_disp_cols = [c for c in disp_cols if c in crit_df.columns]
    st.dataframe(crit_df[valid_disp_cols].sort_values(by='Aging_Num', ascending=False), use_container_width=True)

# ---------------------------------------------------------
# 7. WHATSAPP & SMS DISPATCHER (Aging > 7 Days & Fuel Sensor)
# ---------------------------------------------------------
elif page == "📲 WhatsApp & SMS Dispatcher":
    st.markdown("## 📲 WhatsApp & SMS Instant Escalation Dispatcher")
    st.caption("যিবোৰ ছাইটৰ বয়স ৭ দিনতকৈ বেছি হৈছে (Aging > 7 Days) বা ইন্ধন চেন্সৰ বিকল (Fuel Sensor faulty) হৈছে, সেইবোৰ ছাইট চিনাক্ত কৰি Field Supervisor/TRT-লৈ ১-ক্লিক সতৰ্কবাৰ্তা প্ৰেৰণ।")

    # Filter for Aging > 7 Days OR Fuel Sensor faulty
    target_escalations = df_status[(df_status['Aging_Num'] > 7) | (df_status['Fuel Sensor Status'] == 'Fuel Sensor faulty')].copy()
    
    if target_escalations.empty:
        st.success("কোনো সক্রিয় সতৰ্কবাৰ্তা নাই (No active escalations > 7 days or faulty fuel sensors).")
    else:
        st.markdown(f"**মুঠ `{len(target_escalations)}` টা ছাইটত সতৰ্কবাৰ্তা প্ৰেৰণৰ প্ৰয়োজন পোৱা গৈছে।**")
        esc_site = st.selectbox("Select Target Escalation Site:", target_escalations['SAIP ID'].tolist())
        target_row = target_escalations[target_escalations['SAIP ID'] == esc_site].iloc[0]

        supervisor = str(target_row.get("Supervisor Name", "Field Team"))
        contact = str(target_row.get("Contact No.", "")).replace(" ", "").replace("-", "")
        if not contact or contact.lower() == 'nan': contact = "91XXXXXXXXXX"

        msg_body = f"""🚨 *URGENT NOC ESCALATION - NE CIRCLE*
Site: *{esc_site}* (JC: {target_row.get('JC', 'N/A')})
Status: {target_row.get('DG Automation Status', 'N/A')}
Problem: *{target_row.get('Bucket', 'Hardware Fault')}*
Docket No: {target_row.get('Present Docket No.', 'N/A')}
Delay Aging: *{target_row.get("Aging (Day's)", 'N/A')} Days*
Supervisor: {supervisor}
Action: Immediate physical site restoration requested by Circle Ops."""

        encoded_msg = urllib.parse.quote(msg_body)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={contact}&text={encoded_msg}"
        sms_url = f"sms:{contact}?body={encoded_msg}"

        st.markdown("#### Message Preview")
        st.code(msg_body, language="markdown")

        c_w1, c_w2 = st.columns(2)
        with c_w1:
            st.link_button("📲 Send WhatsApp Alert via 1-Click", whatsapp_url, use_container_width=True, type="primary")
        with c_w2:
            st.link_button("📩 Send SMS Dispatch", sms_url, use_container_width=True)

# ---------------------------------------------------------
# 8. DAILY MIS REPORT GENERATOR
# ---------------------------------------------------------
elif page == "📑 Daily MIS Report Generator":
    st.markdown("## 📑 Daily Executive MIS Report Generator")
    st.caption("সমগ্ৰ Circle-ৰ Automation Rate, JC-wise Health, আৰু Aging Summary সম্বলিত কাষ্টম এক্সেল ৰিপোৰ্ট প্ৰস্তুত আৰু ১-ক্লিক ডাউনলোড।")

    if not df_status.empty:
        total_sites = len(df_status)
        auto_ok = len(df_status[df_status['DG Automation Status'] == 'Automation Ok'])
        manual_mode = len(df_status[df_status['DG Automation Status'] == 'Manual Mode'])
        rate = round((auto_ok/total_sites)*100, 2)

        st.markdown(f"""
        <div class="metric-card" style="color: #0f172a; margin-bottom: 20px;">
            <h3 style="color: #0f172a !important; margin:0;">NE Circle Telecom Automation Health Summary</h3>
            <p style="color: #475569; margin: 4px 0 0 0;">Report Date: <b>{datetime.now().strftime('%d %B %Y')}</b> | Executive Author: <b>{admin_name}</b></p>
            <hr style="margin: 10px 0;">
            • Total Monitored Sites: <b>{total_sites:,}</b><br>
            • Operational Automation Rate: <b>{rate}%</b> ({auto_ok:,} Sites)<br>
            • Manual Mode Alerts: <b>{manual_mode:,}</b><br>
            • Faulty Fuel Sensor Probes: <b>{len(df_fuel):,}</b>
        </div>
        """, unsafe_allow_html=True)

        mis_output = BytesIO()
        with pd.ExcelWriter(mis_output, engine='openpyxl') as writer:
            summary_table = pd.DataFrame({
                "KPI Metric": ["Total Circle Fleet", "Automation Ok Sites", "Manual Mode Alerts", "Automation Rate (%)", "Faulty Fuel Sensors"],
                "Value": [total_sites, auto_ok, manual_mode, f"{rate}%", len(df_fuel)]
            })
            summary_table.to_excel(writer, sheet_name="Executive Summary", index=False)
            
            jc_summary = pd.crosstab(df_status['JC'], df_status['DG Automation Status'], margins=True)
            jc_summary.to_excel(writer, sheet_name="JC Automation Matrix")

            if not df_status.empty:
                df_status.head(100).to_excel(writer, sheet_name="Top Monitored Sites", index=False)

        st.download_button(
            label="📥 Download Daily Executive MIS Excel Report",
            data=mis_output.getvalue(),
            file_name=f"Daily_MIS_NE_Circle_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

# ---------------------------------------------------------
# 9. IN-PORTAL MASTER TRACKER EDITOR (RBAC PROTECTED)
# ---------------------------------------------------------
elif page == "✏️ In-Portal Master Tracker Editor":
    st.markdown("## ✏️ In-Portal Master Tracker Live Editor")
    st.caption(f"Authenticated Role: **{admin_role}** | Modifying telemetry and resolving active tickets.")

    # 🔒 READ-ONLY ENFORCEMENT FOR VIEWER ACCOUNT
    if "read_only" in user_perms:
        st.warning("🔒 Viewer Account: আপোনাৰ একাউণ্ট কেৱল পৰ্যবেক্ষণৰ বাবে (Read-only)। ছাইটৰ ডেটা এডিট কৰা, ফল্ট ৰিছেট কৰা বা TT বন্ধ কৰাৰ অনুমতি নিষ্ক্ৰিয় কৰা হৈছে।")
        st.dataframe(df_status.head(50), use_container_width=True)
    else:
        edit_tab1, edit_tab2 = st.tabs([
            "📝 Single Site Quick Editor, TT Closure & Removal",
            "📊 Bulk Inline Grid Editor (Spreadsheet View)"
        ])

        with edit_tab1:
            st.subheader("Direct Site Modification, Fault Reset & Incident Resolution")
            search_edit_site = st.text_input("Enter SAIP ID to modify, reset, or close (e.g. I-NE-CMKD-ENB-9020):").strip().upper()
            
            if search_edit_site:
                match_idx = df_status[df_status['SAIP ID'].astype(str).str.strip().str.upper() == search_edit_site].index
                if match_idx.empty:
                    st.error(f"Site `{search_edit_site}` not found in the loaded tracker.")
                else:
                    row_idx = match_idx[0]
                    target_row = df_status.loc[row_idx]

                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.95); border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 18px; margin-bottom: 12px; color: #0f172a;">
                        <b>Target Site:</b> <code>{target_row['SAIP ID']}</code> | <b>JC:</b> {target_row.get('JC', 'N/A')} | <b>Current Status:</b> <code>{target_row.get('DG Automation Status', 'N/A')}</code> | <b>Bucket:</b> <code>{target_row.get('Bucket', 'None')}</code><br>
                        <b>Fuel Sensor:</b> <code>{target_row.get('Fuel Sensor Status', 'Ok')}</code> | <b>Present Docket:</b> <code>{target_row.get('Present Docket No.', 'None')}</code>
                    </div>
                    """, unsafe_allow_html=True)

                    allowed_actions = [
                        "📝 Modify Telemetry / Docket Fields",
                        "🧹 Remove Active Fault Data & Reset to Automation Ok",
                        "✅ Close TT / Incident (Auto-Shift Y to AB)"
                    ]
                    if "all" in user_perms:
                        allowed_actions.append("🗑️ Remove / Delete Site Record from Master Tracker")

                    action_mode = st.radio("Select Action for this Site:", allowed_actions, horizontal=True)

                    if action_mode == "📝 Modify Telemetry / Docket Fields":
                        with st.form("single_site_edit_form"):
                            e_col1, e_col2, e_col3 = st.columns(3)
                            with e_col1:
                                curr_status = str(target_row.get('DG Automation Status', 'Automation Ok'))
                                s_idx = STATUS_CHOICES.index(curr_status) if curr_status in STATUS_CHOICES else 0
                                new_dg_status = st.selectbox("DG Automation Status (Col S):", STATUS_CHOICES, index=s_idx)
                                curr_fs = str(target_row.get('Fuel Sensor Status', 'Ok'))
                                fs_choices = ["Ok", "Fuel Sensor faulty"]
                                fs_idx = fs_choices.index(curr_fs) if curr_fs in fs_choices else 0
                                new_fs_status = st.selectbox("Fuel Sensor Status (Col O):", fs_choices, index=fs_idx)
                                new_fs_docket = st.text_input("Fuel Sensor Docket (Col P):", value=str(target_row.get('Docket no.', '')) if pd.notna(target_row.get('Docket no.')) else "")
                                fs_date_default = to_date_obj(target_row.get('Open Date', ''))
                                new_fs_open_date = st.date_input("📅 Fuel Sensor Open Date (Col Q):", value=fs_date_default).strftime('%Y-%m-%d')

                            with e_col2:
                                curr_bucket = str(target_row.get('Bucket', 'None'))
                                b_choices = ["None"] + BUCKET_LIST
                                b_idx = b_choices.index(curr_bucket) if curr_bucket in b_choices else 0
                                new_bucket = st.selectbox("Problem Bucket (Col U):", b_choices, index=b_idx)
                                new_docket = st.text_input("Present Docket No (Col V):", value=str(target_row.get('Present Docket No.', '')) if pd.notna(target_row.get('Present Docket No.')) else "")

                            with e_col3:
                                raise_date_default = to_date_obj(target_row.get('Present Docket raise Date', ''))
                                new_raise_date = st.date_input("📅 Present Docket Raise Date (Col W):", value=raise_date_default).strftime('%Y-%m-%d')
                                new_aging = st.number_input("Aging Days (Col X):", value=int(target_row.get("Aging (Day's)", 0)) if pd.notna(target_row.get("Aging (Day's)")) else 0, step=1)

                            new_remarks = st.text_area("Present Remarks (Col T):", value=str(target_row.get('Present Remarks', '')) if pd.notna(target_row.get('Present Remarks')) else "")
                            save_changes = st.form_submit_button("💾 Save & Update Record in Master Tracker", use_container_width=True, type="primary")

                            if save_changes:
                                st.session_state.master_tracker_df.at[row_idx, 'DG Automation Status'] = new_dg_status
                                st.session_state.master_tracker_df.at[row_idx, 'Fuel Sensor Status'] = new_fs_status
                                st.session_state.master_tracker_df.at[row_idx, 'Docket no.'] = new_fs_docket
                                st.session_state.master_tracker_df.at[row_idx, 'Open Date'] = new_fs_open_date
                                st.session_state.master_tracker_df.at[row_idx, 'Bucket'] = None if new_bucket == "None" else new_bucket
                                st.session_state.master_tracker_df.at[row_idx, 'Present Docket No.'] = new_docket
                                st.session_state.master_tracker_df.at[row_idx, 'Present Docket raise Date'] = new_raise_date
                                st.session_state.master_tracker_df.at[row_idx, "Aging (Day's)"] = new_aging
                                st.session_state.master_tracker_df.at[row_idx, 'Present Remarks'] = new_remarks

                                st.session_state.master_tracker_df = auto_sync_edited_data_to_engine(
                                    st.session_state.master_tracker_df, df_open_cm, df_cr_data
                                )
                                st.success(f"Site `{search_edit_site}` updated & synced!")
                                st.rerun()

                    elif action_mode == "🧹 Remove Active Fault Data & Reset to Automation Ok":
                        if st.button("🧹 Clear All Active Fault Details & Set Automation Ok", type="primary", use_container_width=True):
                            st.session_state.master_tracker_df = clear_site_active_fault_data(
                                search_edit_site, st.session_state.master_tracker_df
                            )
                            st.success(f"Faults cleared for `{search_edit_site}` and restored to Automation Ok!")
                            st.rerun()

                    elif action_mode == "✅ Close TT / Incident (Auto-Shift Y to AB)":
                        with st.form("single_site_tt_close_form"):
                            c_c1, c_c2 = st.columns(2)
                            with c_c1:
                                str_closed_date = st.date_input("📅 Closure Date (Col R):", value=date.today()).strftime('%Y-%m-%d')
                            with c_c2:
                                res_remarks = st.text_input("Closure Remarks:", placeholder="OEM replacement done, restored")

                            if st.form_submit_button("✅ Close TT & Execute Shift to Col Y-AB", use_container_width=True, type="primary"):
                                st.session_state.master_tracker_df = execute_tt_close_shift_to_y_ab(
                                    search_edit_site, res_remarks, str_closed_date, st.session_state.master_tracker_df
                                )
                                st.success(f"TT Closed for {search_edit_site}!")
                                st.rerun()

                    elif action_mode == "🗑️ Remove / Delete Site Record from Master Tracker":
                        if st.button(f"🚨 Confirm Delete `{search_edit_site}` Record", type="primary", use_container_width=True):
                            st.session_state.master_tracker_df = st.session_state.master_tracker_df.drop(index=row_idx).reset_index(drop=True)
                            st.success(f"Site `{search_edit_site}` permanently deleted.")
                            st.rerun()

        with edit_tab2:
            st.subheader("Interactive Spreadsheet Grid")
            jc_filter = st.selectbox("Filter Grid by JC:", ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique()]), key="grid_jc_filter")
            grid_cols = ['SAIP ID', 'JC', 'Fuel Sensor Status', 'Docket no.', 'Open Date', 'DG Automation Status', 'Present Remarks', 'Bucket', 'Present Docket No.', 'Present Docket raise Date', "Aging (Day's)", 'Timeline']
            valid_grid_cols = [c for c in grid_cols if c in df_status.columns]
            raw_target_df = df_status[valid_grid_cols] if jc_filter == "All JCs" else df_status[df_status['JC'] == jc_filter][valid_grid_cols]
            target_grid_df = raw_target_df.copy()

            for date_c in ['Open Date', 'Present Docket raise Date']:
                if date_c in target_grid_df.columns:
                    target_grid_df[date_c] = pd.to_datetime(target_grid_df[date_c], errors='coerce').dt.date

            edited_data = st.data_editor(
                target_grid_df,
                column_config={
                    "Fuel Sensor Status": st.column_config.SelectboxColumn("Fuel Sensor Status", options=["Ok", "Fuel Sensor faulty"]),
                    "Open Date": st.column_config.DateColumn("📅 Open Date", format="YYYY-MM-DD"),
                    "DG Automation Status": st.column_config.SelectboxColumn("DG Automation Status", options=STATUS_CHOICES, required=True),
                    "Bucket": st.column_config.SelectboxColumn("Bucket", options=BUCKET_LIST),
                    "Present Docket raise Date": st.column_config.DateColumn("📅 Present Docket raise Date", format="YYYY-MM-DD")
                },
                disabled=["SAIP ID", "JC"],
                use_container_width=True,
                height=480
            )

            if st.button("💾 Commit Grid Edits to Master Tracker", use_container_width=True, type="primary"):
                for idx, edited_row in edited_data.iterrows():
                    orig_idx = df_status[df_status['SAIP ID'] == edited_row['SAIP ID']].index
                    if not orig_idx.empty:
                        i = orig_idx[0]
                        for col in valid_grid_cols:
                            if col not in ['SAIP ID', 'JC']:
                                val = edited_row[col]
                                if col in ['Open Date', 'Present Docket raise Date']: val = clean_date_str(val)
                                st.session_state.master_tracker_df.at[i, col] = val
                st.session_state.master_tracker_df = auto_sync_edited_data_to_engine(
                    st.session_state.master_tracker_df, df_open_cm, df_cr_data
                )
                st.success("All spreadsheet changes committed & synced!")
                st.rerun()

# ---------------------------------------------------------
# 10. AI SITE DIAGNOSTICS
# ---------------------------------------------------------
elif page == "🔍 AI Site Diagnostics":
    st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
    sq = st.text_input("Search Network Site:", placeholder="Enter SAIP ID (e.g. 9011, BARA, DNGI)...").strip().upper()
    if sq:
        matches = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)] if not df_status.empty else pd.DataFrame()
        if not matches.empty:
            site_row = matches.iloc[0]
            selected_site = site_row['SAIP ID']
            status_val = str(site_row.get('DG Automation Status', 'Unknown'))
            badge_class = "badge-ok" if status_val == "Automation Ok" else "badge-crit" if "Breakdown" in status_val else "badge-warn"

            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.95); border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a !important; text-shadow: none !important;">⚡ {selected_site}</h3>
                        <p style="margin: 4px 0 0 0; color: #64748b !important; font-size: 14px;">
                            Circle Territory: <b>{site_row.get('JC', 'N/A')}</b> | DG Make: <b>{site_row.get('DG Make', 'N/A')}</b> | Rating: <b>{site_row.get('DG Rating', 'N/A')}</b>
                        </p>
                    </div>
                    <div>
                        <span class="status-badge {badge_class}" style="font-size: 13px; padding: 6px 14px;">{status_val}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            k1, k2, k3 = st.columns(3)
            k1.metric("Active Bucket", f"{site_row.get('Bucket', 'None')}")
            k2.metric("Incident Aging", f"{int(site_row.get('Aging (Day\'s)', 0)) if pd.notna(site_row.get('Aging (Day\'s)')) else 0} Days")
            k3.metric("Fuel Telemetry", f"{site_row.get('Fuel Sensor Status', 'Ok')}")
