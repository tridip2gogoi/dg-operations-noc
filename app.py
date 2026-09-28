import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import hashlib
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NE Circle Telecom DG Ops Center | Enterprise NOC",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom Corporate Professional NOC Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.90)), 
                    url("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] div[role="radiogroup"] label,
    div[data-testid="stRadio"] div[role="radiogroup"] label div p,
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: rgba(30, 41, 59, 0.85);
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        margin-right: 8px;
    }

    div[data-testid="stTabs"] {
        background: rgba(15, 23, 42, 0.75);
        padding: 10px 10px 0px 10px;
        border-radius: 12px 12px 0 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    div[data-testid="stTabs"] button[role="tab"] {
        background-color: rgba(30, 41, 59, 0.9) !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 22px !important;
        margin-right: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[role="tab"] span,
    div[data-testid="stTabs"] button[role="tab"] div {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: #0284c7 !important;
        border-bottom: 3px solid #38bdf8 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] span,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] div {
        color: #ffffff !important;
        font-weight: 900 !important;
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

    .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label, .stNumberInput label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    [data-testid="stFileUploadDropzone"] * {
        color: #0f172a !important;
    }

    .auto-docket-box {
        background-color: rgba(239, 246, 255, 0.98);
        border: 1px solid #93c5fd;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #0f172a !important;
    }
    .auto-docket-box * {
        color: #0f172a !important;
    }

    .previous-remarks-box {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    .previous-remarks-box p, .previous-remarks-box span, .previous-remarks-box div {
        color: #ffffff !important;
    }

    .custom-header-banner {
        background-color: #0f172a !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
        padding: 22px 26px !important;
        margin-top: 14px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.6) !important;
        color: #ffffff !important;
    }
    .custom-header-banner * {
        color: #ffffff !important;
        text-shadow: none !important;
    }

    /* PROFESSIONAL BADGES */
    .status-badge {
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .badge-ok { 
        background-color: #0284c7 !important; 
        color: #ffffff !important; 
        border: 1px solid #38bdf8; 
    }
    .badge-warn { 
        background-color: #ca8a04 !important; 
        color: #ffffff !important; 
        border: 1px solid #facc15; 
    }
    .badge-crit { 
        background-color: #dc2626 !important; 
        color: #ffffff !important; 
        border: 1px solid #f87171; 
    }
</style>
""", unsafe_allow_html=True)

DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio.xlsx"

DEFAULT_ILA = None
for f in os.listdir('.'):
    if "ILA" in f.upper() and f.endswith(('.xlsx', '.xls')) and not f.startswith('~$'):
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
    except Exception:
        return val_str.split(' ')[0] if ' ' in val_str else val_str

def to_date_obj(val, fallback=None):
    if pd.isna(val) or val is None or str(val).strip().lower() in ['', 'nat', 'nan', 'none', '0']:
        return None
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return fallback

USER_CREDENTIALS = {
    "admin": {
        "password_hash": hashlib.sha256("admin@123".encode()).hexdigest(),
        "role": "Super Admin / Operations Head",
        "name": "Circle Operations Head",
        "access": ["all"]
    },
    "viewer": {
        "password_hash": hashlib.sha256("viewer@123".encode()).hexdigest(),
        "role": "NOC Viewer / Executive",
        "name": "Circle Audit Desk",
        "access": ["read_only"]
    }
}

def verify_login(username, password):
    if username in USER_CREDENTIALS:
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        if hashed_pwd == USER_CREDENTIALS[username]["password_hash"]:
            return USER_CREDENTIALS[username]
    return None

def is_valid_source(src):
    if hasattr(src, 'read'): return True
    if isinstance(src, str) and os.path.exists(src): return True
    return False

@st.cache_data
def load_all_trackers(dg_file, cm_file, ila_file=None, cr_file=None):
    df_status = pd.DataFrame()
    df_fuel = pd.DataFrame()
    df_open_cm = pd.DataFrame()
    df_ila = pd.DataFrame()
    df_cr_data = pd.DataFrame()
    
    if is_valid_source(dg_file):
        try:
            xls_dg = pd.ExcelFile(dg_file)
            sheet_target = "Automation Status" if "Automation Status" in xls_dg.sheet_names else xls_dg.sheet_names[0]
            df_status = pd.read_excel(xls_dg, sheet_name=sheet_target)
            
            if 'Last Closed date' in df_status.columns:
                df_status = df_status.drop(columns=['Last Closed date'])
            if 'Last Closed date.1' in df_status.columns:
                df_status = df_status.drop(columns=['Last Closed date.1'])
            
            if 'SAIP ID' in df_status.columns:
                df_status = df_status[df_status['SAIP ID'].notna()]
                df_status['SAIP ID'] = df_status['SAIP ID'].astype(str).str.strip()
                df_status = df_status[~df_status['SAIP ID'].str.lower().isin(['', 'nan', 'none', 'total', '0', 'null'])]
            
            if 'DG Make' in df_status.columns:
                df_status = df_status[df_status['DG Make'].notna()]
                df_status['DG Make'] = df_status['DG Make'].astype(str).str.strip()
                df_status = df_status[~df_status['DG Make'].str.lower().isin(['', 'nan', 'none', 'null', 'no dg', 'non dg'])]
            
            if 'JC' in df_status.columns:
                df_status['JC'] = df_status['JC'].astype(str).str.strip()
            
            for d_col in ['Open Date', 'Present Docket raise Date', 'Previous Docket raise Date']:
                if d_col in df_status.columns:
                    df_status[d_col] = df_status[d_col].apply(clean_date_str)
            
            aging_col_target = None
            for col in df_status.columns:
                if 'aging' in col.lower() or 'ageing' in col.lower():
                    aging_col_target = col
                    break
            
            if aging_col_target:
                df_status['Aging_Num'] = pd.to_numeric(df_status[aging_col_target], errors='coerce').fillna(0)
            else:
                df_status['Aging_Num'] = 0
                    
            if "Fuel Sensor faulty" in xls_dg.sheet_names:
                df_fuel = pd.read_excel(xls_dg, sheet_name="Fuel Sensor faulty")
                if 'COMPLAINT LOGGIN DATE' in df_fuel.columns:
                    df_fuel['COMPLAINT LOGGIN DATE'] = df_fuel['COMPLAINT LOGGIN DATE'].apply(clean_date_str)
        except Exception as e:
            st.error(f"Error loading DG tracker: {e}")

    if is_valid_source(cm_file):
        try:
            xls_cm = pd.ExcelFile(cm_file)
            target_cm_sheet = "Open Site" if "Open Site" in xls_cm.sheet_names else xls_cm.sheet_names[0]
            df_open_cm = pd.read_excel(xls_cm, sheet_name=target_cm_sheet)
        except Exception as e:
            st.warning(f"Note on CM tracker: {e}")

    if ila_file and is_valid_source(ila_file):
        try:
            xls_ila = pd.ExcelFile(ila_file)
            df_ila = pd.read_excel(xls_ila, sheet_name=xls_ila.sheet_names[0])
            if 'Sap ID' in df_ila.columns:
                df_ila = df_ila[df_ila['Sap ID'].notna()]
                df_ila['Sap ID'] = df_ila['Sap ID'].astype(str).str.strip()
        except Exception as e:
            st.warning(f"Note on ILA-AG1 tracker: {e}")

    return df_status, df_fuel, df_open_cm, df_ila, df_cr_data

def ai_capture_o_to_ab(site_id, df_open_cm, df_status, df_cr_data=None):
    clean_id = str(site_id).strip().upper() if site_id else ""
    res = {
        "JC": "", "Col_O_Fuel_Sensor_Status": "Ok", "Col_P_Docket_no": "",
        "Col_Q_Open_Date": "", "Col_S_DG_Automation_Status": "Automation Ok",
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

    if not df_open_cm.empty:
        cols = {c.lower(): c for c in df_open_cm.columns}
        site_col = cols.get('site id') or cols.get('site_id') or cols.get('sap id') or cols.get('saip id')
        docket_col = cols.get('docket number') or cols.get('docket no') or cols.get('docket')
        complaint_col = cols.get('nature of complaint') or cols.get('complaint') or cols.get('remarks')
        bucket_col = cols.get('bucket') or cols.get('root cause')
        timeline_col = cols.get('timeline')
        aging_col = cols.get('ageing') or cols.get('aging')
        date_col = cols.get('complaint loggin date') or cols.get('open date') or cols.get('date')

        if site_col:
            cm_match = df_open_cm[df_open_cm[site_col].astype(str).str.strip().str.upper() == clean_id]
            if not cm_match.empty:
                cm_row = cm_match.iloc[0]
                new_docket = str(cm_row.get(docket_col, "")).strip() if docket_col else ""
                new_complaint = str(cm_row.get(complaint_col, "")).strip() if complaint_col else ""
                new_bucket = str(cm_row.get(bucket_col, "")).strip() if bucket_col else ""
                new_aging = cm_row.get(aging_col, 0) if aging_col else 0
                date_str = clean_date_str(cm_row.get(date_col, "")) if date_col else ""

                if new_docket and new_docket.lower() != 'nan':
                    res["Col_V_Present_Docket_No"] = new_docket
                if date_str:
                    res["Col_W_Present_Docket_raise_Date"] = date_str
                    res["Col_Q_Open_Date"] = date_str
                if new_complaint and new_complaint.lower() != 'nan':
                    res["Col_T_Present_Remarks"] = new_complaint
                if new_bucket and new_bucket.lower() != 'nan':
                    res["Col_U_Bucket"] = new_bucket
                
                if "FUEL" in new_complaint.upper() or "FUEL" in new_bucket.upper():
                    res["Col_O_Fuel_Sensor_Status"] = "Fuel Sensor faulty"
                    res["Col_P_Docket_no"] = new_docket

                try:
                    res["Col_X_Aging_Days"] = float(new_aging) if pd.notna(new_aging) else 0
                except:
                    res["Col_X_Aging_Days"] = 0

                res["source"] = "CM Tracker (Open Site Auto-Scan)"

    for k, v in res.items():
        if str(v).lower() == 'nan' or str(v) == 'nat':
            res[k] = ""
    return res

def archive_current_fault_to_previous(row_idx, df_target):
    r = df_target.loc[row_idx]
    pres_doc = str(r.get('Present Docket No.', '')).strip()
    pres_date = str(r.get('Present Docket raise Date', '')).strip()
    pres_rem = str(r.get('Present Remarks', '')).strip()
    
    if pres_doc and pres_doc.lower() not in ['', 'nan', 'none']:
        df_target.at[row_idx, 'Previous Docket No.'] = pres_doc
        df_target.at[row_idx, 'Previous Docket raise Date'] = pres_date
        df_target.at[row_idx, 'Previous Remarks'] = pres_rem
    return df_target

def clear_site_active_fault_data(site_id, df_target):
    if df_target.empty or not site_id:
        return df_target
    updated = df_target.copy()
    clean_id = str(site_id).strip().upper()
    match_idx = updated[updated["SAIP ID"].astype(str).str.strip().str.upper() == clean_id].index
    if not match_idx.empty:
        i = match_idx[0]
        updated = archive_current_fault_to_previous(i, updated)
        if "Fuel Sensor Status" in updated.columns: updated.at[i, "Fuel Sensor Status"] = "Ok"
        if "Docket no." in updated.columns: updated.at[i, "Docket no."] = ""
        if "Open Date" in updated.columns: updated.at[i, "Open Date"] = ""
        if "DG Automation Status" in updated.columns: updated.at[i, "DG Automation Status"] = "Automation Ok"
        if "Present Remarks" in updated.columns: updated.at[i, "Present Remarks"] = ""
        if "Bucket" in updated.columns: updated.at[i, "Bucket"] = None
        if "Present Docket No." in updated.columns: updated.at[i, "Present Docket No."] = ""
        if "Present Docket raise Date" in updated.columns: updated.at[i, "Present Docket raise Date"] = ""
        if "Aging (Day's)" in updated.columns: updated.at[i, "Aging (Day's)"] = 0
        if "Aging_Num" in updated.columns: updated.at[i, "Aging_Num"] = 0
    return updated

# --- AUTHENTICATION GATEWAY ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None

if not st.session_state.authenticated:
    _, col1, _ = st.columns([1, 1.2, 1])
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.96); padding: 2.2rem 2rem; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); border: 1px solid rgba(226, 232, 240, 0.8); margin: 3.5rem auto;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #0f172a; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.25rem;">⚡ DG NOC Portal</h2>
                <p style="color: #64748b; font-size: 0.9rem;">North East Circle Operations Gateway</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("admin_login_form"):
            input_user = st.text_input("Username", placeholder="Enter username")
            input_pass = st.text_input("Password", type="password", placeholder="••••••••")
            login_btn = st.form_submit_button("Authenticate & Access Dashboard", use_container_width=True, type="primary")

            if login_btn:
                user_record = verify_login(input_user.strip().lower(), input_pass)
                if user_record:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_record
                    st.session_state.username = input_user.strip().lower()
                    st.success("Access Granted! Loading Console...")
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid Credentials")

        st.markdown("""
        <div style="background: rgba(241, 245, 249, 0.95); border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px 14px; margin-top: 14px; font-size: 13px; color: #334155; text-align: center;">
            👁️ <b>NOC Viewer (Read-only) Access:</b><br>
            Username: <code style="color: #0369a1; font-weight: 600;">viewer</code> | Password: <code style="color: #0369a1; font-weight: 600;">viewer@123</code>
        </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# --- AUTHENTICATED WORKSPACE ---
user_data = st.session_state.user_info
admin_name = user_data["name"]
admin_role = user_data["role"]
user_perms = user_data.get("access", ["all"])

st.sidebar.markdown(f"### 🛡️ Enterprise NOC Hub")
st.sidebar.markdown(f"**Operator:** `{admin_name}`")
st.sidebar.markdown(f"**Role:** `{admin_role}`")
if st.sidebar.button("Log Out Session", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

st.sidebar.markdown("---")

# Data Pipeline Uploads
st.sidebar.markdown("### 📂 Data Pipeline Synchronization")
uploaded_cm = st.sidebar.file_uploader("1. CM Tracker (Open Site)", type=["xlsx", "xls"])
uploaded_dg = st.sidebar.file_uploader("2. DG Automation Master Tracker", type=["xlsx", "xls"])
uploaded_ila = st.sidebar.file_uploader("3. ILA-AG1 Tracker", type=["xlsx", "xls"])

detected_excel = DEFAULT_EXCEL
if not os.path.exists(DEFAULT_EXCEL):
    local_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
    for lf in local_files:
        if "CM" not in lf.upper() and "ILA" not in lf.upper():
            detected_excel = lf
            break

cm_source = uploaded_cm if uploaded_cm is not None else DEFAULT_CM_TRACKER
dg_source = uploaded_dg if uploaded_dg is not None else detected_excel
ila_source = uploaded_ila if uploaded_ila is not None else DEFAULT_ILA

# ⚡ LOADER SPINNER FOR SMOOTH DATA SYNCHRONIZATION
with st.spinner("🔄 Synchronizing and loading enterprise trackers..."):
    df_status_raw, df_fuel_raw, df_open_cm, df_ila_raw, df_cr_data = load_all_trackers(dg_source, cm_source, ila_source)

# ⚡ PERSISTENT SESSION STATE INITIALIZATION
if "master_tracker_df" not in st.session_state:
    st.session_state.master_tracker_df = pd.DataFrame()
if "fuel_tracker_df" not in st.session_state:
    st.session_state.fuel_tracker_df = pd.DataFrame()
if "ila_tracker_df" not in st.session_state:
    st.session_state.ila_tracker_df = pd.DataFrame()

if st.session_state.master_tracker_df.empty and not df_status_raw.empty:
    st.session_state.master_tracker_df = df_status_raw.copy()
if st.session_state.fuel_tracker_df.empty and not df_fuel_raw.empty:
    st.session_state.fuel_tracker_df = df_fuel_raw.copy()
if st.session_state.ila_tracker_df.empty and not df_ila_raw.empty:
    st.session_state.ila_tracker_df = df_ila_raw.copy()

if uploaded_dg is not None and not df_status_raw.empty:
    st.session_state.master_tracker_df = df_status_raw.copy()
if uploaded_ila is not None and not df_ila_raw.empty:
    st.session_state.ila_tracker_df = df_ila_raw.copy()

df_status = st.session_state.master_tracker_df
df_fuel = st.session_state.fuel_tracker_df
df_ila = st.session_state.ila_tracker_df

if not df_status.empty:
    st.sidebar.success(f"Master: {len(df_status)} Monitored Sites Active")
else:
    st.sidebar.warning("⚠️ No data loaded. Upload Master Tracker.")

if not df_ila.empty:
    st.sidebar.success(f"ILA-AG1: {len(df_ila)} Records Loaded")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Complete Data Download")
if not df_status.empty:
    full_output = BytesIO()
    with pd.ExcelWriter(full_output, engine='openpyxl') as writer:
        df_status.to_excel(writer, sheet_name="Automation Status", index=False)
        if not df_fuel.empty:
            df_fuel.to_excel(writer, sheet_name="Fuel Sensor faulty", index=False)
        if not df_ila.empty:
            df_ila.to_excel(writer, sheet_name="ILA-AG1 Tracker", index=False)
    st.sidebar.download_button(
        label="📥 Download Complete Trackers (.xlsx)",
        data=full_output.getvalue(),
        file_name=f"NE_Circle_Complete_NOC_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

page = st.sidebar.radio("NOC Operations Navigation:", [
    "📊 Executive Control Center",
    "⚙️ Fleet Analytics & Problem Buckets",
    "⛽ Fuel Sensor Telemetry",
    "⏳ Critical Aging Escalation Monitor",
    "📈 ILA-AG1 Operations Tracker",
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
        auto_ok = len(df_status[df_status['DG Automation Status'].astype(str).str.strip() == 'Automation Ok']) if 'DG Automation Status' in df_status.columns else 0
        manual_mode = len(df_status[df_status['DG Automation Status'].astype(str).str.strip() == 'Manual Mode']) if 'DG Automation Status' in df_status.columns else 0

        k1, k2, k3 = st.columns(3)
        k1.metric("Network Base (Total Sites)", f"{total_sites:,}", "Active Monitored Fleet")
        k2.metric("Automation Rate", f"{round((auto_ok/total_sites)*100, 1)}%" if total_sites else "0%", f"{auto_ok:,} Sites Online")
        k3.metric("Manual Mode Alerts", manual_mode, f"-{round((manual_mode/total_sites)*100, 1)}%" if total_sites else "0%", delta_color="inverse")

        st.markdown("---")
        c1, c2 = st.columns([3, 2])
        
        with c1:
            with st.container(border=True):
                st.markdown("<h4 style='margin:0 0 10px 0; color: #0f172a;'>Circle JC Wise Automation Health</h4>", unsafe_allow_html=True)
                if "JC" in df_status.columns and "DG Automation Status" in df_status.columns:
                    fig_bar = px.histogram(
                        df_status, x="JC", color="DG Automation Status", barmode="group",
                        color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#6366f1"]
                    )
                    fig_bar.update_layout(
                        height=350, margin=dict(l=10, r=10, t=10, b=10),
                        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                        font=dict(color="#0f172a", family="Inter, sans-serif"),
                        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title_font=dict(color="#0f172a")),
                        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title_font=dict(color="#0f172a")),
                        legend=dict(font=dict(color="#0f172a"), bgcolor="rgba(255,255,255,0.9)")
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            with st.container(border=True):
                st.markdown("<h4 style='margin:0 0 10px 0; color: #0f172a;'>DG Make Fleet Allocation</h4>", unsafe_allow_html=True)
                if "DG Make" in df_status.columns:
                    valid_makes = df_status[df_status['DG Make'].notna() & (df_status['DG Make'].astype(str).str.strip() != '')]
                    fig_donut = px.pie(valid_makes, names="DG Make", hole=0.58, color_discrete_sequence=px.colors.qualitative.Safe)
                    fig_donut.update_layout(
                        height=350, margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                        font=dict(color="#0f172a", family="Inter, sans-serif"),
                        legend=dict(font=dict(color="#0f172a"))
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No data loaded. Please upload the Master Tracker from the sidebar.")

# ---------------------------------------------------------
# 2. FLEET ANALYTICS & ROOT-CAUSE
# ---------------------------------------------------------
elif page == "⚙️ Fleet Analytics & Problem Buckets":
    st.markdown("## ⚙️ Fleet Automation Classification & Root-Cause Analysis")
    st.caption("JC-wise breakdown of network automation health, problem buckets, and docket fulfillment statuses.")

    jc_options = ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique()]) if 'JC' in df_status.columns else ["All JCs"]
    selected_fleet_jc = st.selectbox("Select JC Circle:", jc_options)

    filtered_status = df_status if selected_fleet_jc == "All JCs" or 'JC' not in df_status.columns else df_status[df_status['JC'] == selected_fleet_jc]
    valid_bucket = filtered_status[filtered_status['Bucket'].notna()] if 'Bucket' in filtered_status.columns else pd.DataFrame()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin:0 0 10px 0; color: #0f172a;'>Status Summary ({selected_fleet_jc})</h4>", unsafe_allow_html=True)
            if 'DG Automation Status' in filtered_status.columns:
                stat_summary = filtered_status['DG Automation Status'].value_counts(dropna=False).reset_index()
                stat_summary.columns = ['Status Category', 'Site Count']
                st.dataframe(stat_summary, use_container_width=True, hide_index=True)

    with col2:
        with st.container(border=True):
            st.markdown(f"<h4 style='margin:0 0 10px 0; color: #0f172a;'>Bucket Distribution ({selected_fleet_jc})</h4>", unsafe_allow_html=True)
            if not valid_bucket.empty:
                b_summary = valid_bucket['Bucket'].value_counts().reset_index()
                b_summary.columns = ['Root-Cause Bucket', 'Incidents']
                fig_b = px.bar(
                    b_summary, x="Root-Cause Bucket", y="Incidents", text="Incidents",
                    color="Incidents", color_continuous_scale="Blues"
                )
                fig_b.update_layout(
                    height=340, margin=dict(l=10, r=10, t=10, b=10),
                    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                    font=dict(color="#0f172a", family="Inter, sans-serif"),
                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#0f172a", size=11)),
                    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#0f172a"))
                )
                fig_b.update_traces(textposition='outside', textfont=dict(color="#0f172a", weight="bold"))
                st.plotly_chart(fig_b, use_container_width=True)
            else:
                st.info("No active problem bucket recorded for this selection.")

    st.markdown("---")
    tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs([
        "📊 JC-Wise Automation Status Matrix",
        "🗂️ JC-Wise Problem Bucket Matrix",
        "⚡ GCU Sites: JC vs DG Make & KVA",
        "🛠️ DG Breakdown & Manual (GCU, OEM, Breakdown)"
    ])

    with tab_m1:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px; color: #0f172a;'>JC vs DG Automation Status Cross-Tabulation</h4>", unsafe_allow_html=True)
            if 'JC' in df_status.columns and 'DG Automation Status' in df_status.columns:
                status_matrix = pd.crosstab(df_status['JC'], df_status['DG Automation Status'], margins=True, margins_name="Total")
                st.dataframe(status_matrix, use_container_width=True)

    with tab_m2:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px; color: #0f172a;'>JC vs Root-Cause Bucket Cross-Tabulation</h4>", unsafe_allow_html=True)
            if 'JC' in df_status.columns and 'Bucket' in df_status.columns:
                all_valid_bkt = df_status[df_status['Bucket'].notna()]
                bucket_matrix = pd.crosstab(all_valid_bkt['JC'], all_valid_bkt['Bucket'], margins=True, margins_name="Total")
                st.dataframe(bucket_matrix, use_container_width=True)

    with tab_m3:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px; color: #0f172a;'>GCU Sites: JC vs DG Make & KVA Breakdown</h4>", unsafe_allow_html=True)
            if 'Bucket' in df_status.columns:
                df_gcu = df_status[df_status['Bucket'] == 'GCU'].copy()
                df_gcu['DG Make Clean'] = df_gcu['DG Make'].fillna('Unspecified') if 'DG Make' in df_gcu.columns else 'Unspecified'
                df_gcu['DG Rating Clean'] = df_gcu['DG Rating'].fillna('Unspecified') if 'DG Rating' in df_gcu.columns else 'Unspecified'
                ct_gcu_detailed = pd.crosstab([df_gcu['JC'], df_gcu['DG Make Clean']], df_gcu['DG Rating Clean'], margins=True, margins_name="Total")
                st.dataframe(ct_gcu_detailed, use_container_width=True)

    with tab_m4:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px; color: #0f172a;'>JC-Wise: DG Breakdown & Manual (GCU, OEM, Breakdown)</h4>", unsafe_allow_html=True)
            target_statuses = ['DG Breakdown', 'Manual Mode']
            target_bkts = ['GCU', 'OEM Spare parts', 'DG Breakdown']
            df_sub = df_status[df_status['DG Automation Status'].isin(target_statuses) & df_status['Bucket'].isin(target_bkts)].copy()
            df_sub['Clean_Docket'] = df_sub['Present Docket No.'].fillna('').astype(str).str.strip() if 'Present Docket No.' in df_status.columns else ''
            df_sub['Docket_Status'] = df_sub['Clean_Docket'].apply(lambda x: 'Docket Received' if x.lower() not in ['', 'nan', 'none', 'n/a', '0'] else 'Docket Pending')
            if 'JC' in df_sub.columns:
                ct_sub_bkt = pd.crosstab([df_sub['JC'], df_sub['DG Automation Status'], df_sub['Bucket']], df_sub['Docket_Status'], margins=True, margins_name="Total")
                st.dataframe(ct_sub_bkt, use_container_width=True)
            else:
                st.warning("JC column not found in dataset.")

# ---------------------------------------------------------
# 3. FUEL SENSOR TELEMETRY
# ---------------------------------------------------------
elif page == "⛽ Fuel Sensor Telemetry":
    st.markdown("## ⛽ Fuel Sensor Fault Telemetry")
    st.caption("Active fuel sensor fault distribution cross-tabulated strictly by JC, DG Make, and KVA rating.")

    if not df_fuel.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Faulty Sensors", len(df_fuel))
        c2.metric("Most Affected JC", df_fuel['JC'].mode()[0] if 'JC' in df_fuel.columns else "N/A", f"{df_fuel['JC'].value_counts().max()} Sites" if 'JC' in df_fuel.columns else "")
        c3.metric("Primary Fault Make", df_fuel['DG MAKE'].mode()[0] if 'DG MAKE' in df_fuel.columns else "N/A")
        c4.metric("Primary Fault Rating", df_fuel['KVA'].mode()[0] if 'KVA' in df_fuel.columns else "N/A")

        st.markdown("---")
        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 10px 0; color: #0f172a;'>📊 JC-Wise Faulty Sensors Breakdown</h4>", unsafe_allow_html=True)
            if 'JC' in df_fuel.columns and 'DG MAKE' in df_fuel.columns:
                jc_fault_matrix = pd.crosstab(df_fuel['JC'], df_fuel['DG MAKE'], margins=True, margins_name="Total")
                st.dataframe(jc_fault_matrix, use_container_width=True)

        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 10px 0; color: #0f172a;'>⚡ DG Make Wise & KVA Rating Fault Telemetry</h4>", unsafe_allow_html=True)
            if 'DG MAKE' in df_fuel.columns and 'KVA' in df_fuel.columns:
                make_kva_matrix = pd.crosstab(df_fuel['DG MAKE'], df_fuel['KVA'], margins=True, margins_name="Total")
                st.dataframe(make_kva_matrix, use_container_width=True)

        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 10px 0; color: #0f172a;'>📋 Active Fault Site Registry</h4>", unsafe_allow_html=True)
            disp_fuel_cols = ['SITE ID', 'JC', 'DG MAKE', 'KVA', 'DOCKET NUMBER', 'COMPLAINT LOGGIN DATE', 'NATURE OF COMPLAINT', 'STATUS']
            valid_disp_fuel = [c for c in disp_fuel_cols if c in df_fuel.columns]
            st.dataframe(df_fuel[valid_disp_fuel], use_container_width=True)
    else:
        st.info("No active fuel sensor faults detected.")

# ---------------------------------------------------------
# 4. CRITICAL AGING ESCALATIONS
# ---------------------------------------------------------
elif page == "⏳ Critical Aging Escalation Monitor":
    st.markdown("## ⏳ Critical Aging Escalation Radar & JC-Wise Breakdown")
    aging_valid = df_status[df_status['Aging_Num'] > 0].copy() if 'Aging_Num' in df_status.columns else pd.DataFrame()
    crit_df = aging_valid[aging_valid['Aging_Num'] > 90].copy() if not aging_valid.empty else pd.DataFrame()

    m1, m2 = st.columns(2)
    m1.metric("Total Delayed Sites", len(aging_valid))
    m2.metric("Severe Delays (>90 Days)", len(crit_df))
    if not aging_valid.empty:
        with st.container(border=True):
            st.dataframe(aging_valid.sort_values(by='Aging_Num', ascending=False), use_container_width=True)
    else:
        st.info("No delayed sites found exceeding threshold.")

# ---------------------------------------------------------
# 5. ILA-AG1 OPERATIONS TRACKER
# ---------------------------------------------------------
elif page == "📈 ILA-AG1 Operations Tracker":
    st.markdown("## 📈 ILA-AG1 Operations Tracker & Telemetry")
    st.caption("Integrated tracking, editing, fault clearance, removal, and new case entries for ILA-AG1 operational logs.")

    if df_ila.empty:
        st.info("📂 Please upload the **ILA-AG1 Tracker** file from the sidebar upload section to initialize this module.")
    else:
        ila_tab1, ila_tab2, ila_tab3 = st.tabs([
            "📊 Registry & Spreadsheet Grid",
            "📝 Single Site Quick Editor, Clear & Removal",
            "➕ New Case / Site Entry"
        ])

        with ila_tab1:
            with st.container(border=True):
                st.markdown(f"<h3 style='margin:0 0 10px 0; color: #0f172a;'>ILA-AG1 Registry Summary ({len(df_ila):,} Records)</h3>", unsafe_allow_html=True)
                edited_ila_data = st.data_editor(df_ila, use_container_width=True, height=450)
                
                if st.button("💾 Save Grid Changes to ILA Tracker", type="primary", use_container_width=True):
                    st.session_state.ila_tracker_df = edited_ila_data.copy()
                    st.success("ILA-AG1 grid updates saved successfully!")
                    st.rerun()

                ila_output = BytesIO()
                with pd.ExcelWriter(ila_output, engine='openpyxl') as writer:
                    df_ila.to_excel(writer, sheet_name="ILA-AG1 Data", index=False)
                st.download_button(
                    label="📥 Download Processed ILA-AG1 Report (.xlsx)",
                    data=ila_output.getvalue(),
                    file_name=f"ILA_AG1_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        with ila_tab2:
            with st.container(border=True):
                st.markdown("<h3 style='margin:0 0 10px 0; color: #0f172a;'>Single Site Quick Editor, Fault Clearance & Record Removal</h3>", unsafe_allow_html=True)
                target_sap_id = st.text_input("Enter Sap ID to Modify / Clear / Remove:").strip().upper()
                
                if target_sap_id and 'Sap ID' in df_ila.columns:
                    match_ila_idx = df_ila[df_ila['Sap ID'].astype(str).str.strip().str.upper() == target_sap_id].index
                    if match_ila_idx.empty:
                        st.error(f"Sap ID `{target_sap_id}` not found in ILA-AG1 tracker.")
                    else:
                        i_idx = match_ila_idx[0]
                        i_row = df_ila.loc[i_idx]
                        st.info(f"Selected Record: **{i_row.get('Sap ID')}** | Facality: **{i_row.get('Facality', 'N/A')}** | JC: **{i_row.get('JC', 'N/A')}**")

                        ila_action = st.radio(
                            "Select Action:",
                            ["📝 Edit Record Fields", "🧹 Clear Fault Status & Reset", "🗑️ Remove / Delete Record"],
                            horizontal=True
                        )

                        if ila_action == "📝 Edit Record Fields":
                            with st.form("ila_edit_form"):
                                e1, e2 = st.columns(2)
                                with e1:
                                    new_fac = st.text_input("Facality:", value=str(i_row.get('Facality', '')) if pd.notna(i_row.get('Facality')) else "")
                                    new_jc = st.text_input("JC:", value=str(i_row.get('JC', '')) if pd.notna(i_row.get('JC')) else "")
                                    new_state = st.text_input("State:", value=str(i_row.get('State', '')) if pd.notna(i_row.get('State')) else "")
                                    new_sup = st.text_input("Supervisors:", value=str(i_row.get('Supervisors', '')) if pd.notna(i_row.get('Supervisors')) else "")
                                with e2:
                                    new_status = st.text_input("DG Automation Status:", value=str(i_row.get('DG Automation Status', '')) if pd.notna(i_row.get('DG Automation Status')) else "")
                                    new_rem = st.text_input("Present Remarks:", value=str(i_row.get('Present Remarks', '')) if pd.notna(i_row.get('Present Remarks')) else "")
                                    new_bkt = st.text_input("Bucket:", value=str(i_row.get('Bucket', '')) if pd.notna(i_row.get('Bucket')) else "")
                                    new_docket = st.text_input("Docket No:", value=str(i_row.get('Docket No.', '')) if pd.notna(i_row.get('Docket No.')) else "")

                                submit_ila_edit = st.form_submit_button("💾 Update ILA Record", type="primary", use_container_width=True)
                                if submit_ila_edit:
                                    st.session_state.ila_tracker_df.at[i_idx, 'Facality'] = new_fac
                                    st.session_state.ila_tracker_df.at[i_idx, 'JC'] = new_jc
                                    st.session_state.ila_tracker_df.at[i_idx, 'State'] = new_state
                                    st.session_state.ila_tracker_df.at[i_idx, 'Supervisors'] = new_sup
                                    st.session_state.ila_tracker_df.at[i_idx, 'DG Automation Status'] = new_status
                                    st.session_state.ila_tracker_df.at[i_idx, 'Present Remarks'] = new_rem
                                    st.session_state.ila_tracker_df.at[i_idx, 'Bucket'] = new_bkt
                                    st.session_state.ila_tracker_df.at[i_idx, 'Docket No.'] = new_docket
                                    st.success(f"Record `{target_sap_id}` updated successfully!")
                                    st.rerun()

                        elif ila_action == "🧹 Clear Fault Status & Reset":
                            if st.button("🧹 Clear & Reset Status to OK", type="primary", use_container_width=True):
                                st.session_state.ila_tracker_df.at[i_idx, 'DG Automation Status'] = "Automation Ok"
                                st.session_state.ila_tracker_df.at[i_idx, 'Present Remarks'] = "OK"
                                st.session_state.ila_tracker_df.at[i_idx, 'Bucket'] = None
                                st.session_state.ila_tracker_df.at[i_idx, 'Docket No.'] = None
                                st.success(f"Fault cleared for `{target_sap_id}`!")
                                st.rerun()

                        else:
                            if st.button(f"🚨 Confirm Delete Record `{target_sap_id}`", type="primary", use_container_width=True):
                                st.session_state.ila_tracker_df = st.session_state.ila_tracker_df.drop(index=i_idx).reset_index(drop=True)
                                st.success(f"Record `{target_sap_id}` deleted successfully!")
                                st.rerun()

        with ila_tab3:
            with st.container(border=True):
                st.markdown("<h3 style='margin:0 0 10px 0; color: #0f172a;'>Add New Case / Site Entry</h3>", unsafe_allow_html=True)
                with st.form("new_ila_case_form"):
                    nc1, nc2 = st.columns(2)
                    with nc1:
                        new_sap = st.text_input("Sap ID (Required):").strip().upper()
                        new_fac_c = st.text_input("Facality:")
                        new_jc_c = st.text_input("JC:")
                        new_state_c = st.text_input("State:")
                        new_sup_c = st.text_input("Supervisors:")
                    with nc2:
                        new_make_c = st.text_input("DG Make:")
                        new_rate_c = st.text_input("DG Rating:")
                        new_stat_c = st.selectbox("DG Automation Status:", STATUS_CHOICES)
                        new_rem_c = st.text_input("Present Remarks:")
                        new_bkt_c = st.selectbox("Bucket:", ["None"] + BUCKET_LIST)

                    submit_new_case = st.form_submit_button("➕ Add New Case Entry", type="primary", use_container_width=True)
                    if submit_new_case:
                        if not new_sap:
                            st.error("Sap ID is required.")
                        else:
                            new_row_data = {
                                'Sap ID': new_sap,
                                'Facality': new_fac_c,
                                'JC': new_jc_c,
                                'State': new_state_c,
                                'Supervisors': new_sup_c,
                                'DG Make': new_make_c,
                                'DG Rating': new_rate_c,
                                'DG Automation Status': new_stat_c,
                                'Present Remarks': new_rem_c,
                                'Bucket': None if new_bkt_c == "None" else new_bkt_c
                            }
                            new_df_row = pd.DataFrame([new_row_data])
                            st.session_state.ila_tracker_df = pd.concat([st.session_state.ila_tracker_df, new_df_row], ignore_index=True)
                            st.success(f"New case `{new_sap}` added successfully!")
                            st.rerun()

# ---------------------------------------------------------
# 6. IN-PORTAL MASTER TRACKER EDITOR (FULL MASTER EDITING & SPREADSHEET GRID)
# ---------------------------------------------------------
elif page == "✏️ In-Portal Master Tracker Editor":
    st.markdown("## ✏️ In-Portal Master Tracker Live Editor")
    if "read_only" in user_perms:
        st.warning("🔒 Viewer Account: Read-only access enabled.")
        with st.container(border=True):
            st.dataframe(df_status.head(50), use_container_width=True)
    else:
        edit_tab1, edit_tab2 = st.tabs([
            "📝 Single Site Quick Editor, TT Closure & Removal",
            "📊 Full Master Tracker Spreadsheet Inline Grid Editor"
        ])

        with edit_tab1:
            with st.container(border=True):
                st.markdown("<h3 style='margin:0 0 10px 0; color: #0f172a;'>Single Site Quick Editor, TT Closure & Removal</h3>", unsafe_allow_html=True)
                search_edit_site = st.text_input("Enter SAIP ID to modify, close TT, or remove:").strip().upper()
                
                if search_edit_site and not df_status.empty and 'SAIP ID' in df_status.columns:
                    match_idx = df_status[df_status['SAIP ID'].astype(str).str.strip().str.upper() == search_edit_site].index
                    if match_idx.empty:
                        st.error(f"Site `{search_edit_site}` not found in Master Tracker.")
                    else:
                        row_idx = match_idx[0]
                        s_row = df_status.loc[row_idx]
                        
                        auto_scanned_data = ai_capture_o_to_ab(search_edit_site, df_open_cm, df_status, None)
                        
                        default_stat = s_row.get('DG Automation Status', 'Automation Ok')
                        if auto_scanned_data["source"] != "None" and default_stat == "Automation Ok":
                            default_stat = auto_scanned_data["Col_S_DG_Automation_Status"]

                        default_bkt = s_row.get('Bucket')
                        if not default_bkt or pd.isna(default_bkt):
                            default_bkt = auto_scanned_data["Col_U_Bucket"]

                        default_docket = str(s_row.get('Present Docket No.', ''))
                        if (not default_docket or default_docket.lower() in ['', 'nan', 'none']) and auto_scanned_data["Col_V_Present_Docket_No"]:
                            default_docket = auto_scanned_data["Col_V_Present_Docket_No"]

                        default_rem = str(s_row.get('Present Remarks', ''))
                        if (not default_rem or default_rem.lower() in ['', 'nan', 'none']) and auto_scanned_data["Col_T_Present_Remarks"]:
                            default_rem = auto_scanned_data["Col_T_Present_Remarks"]

                        default_fuel_status = str(s_row.get('Fuel Sensor Status', 'Ok'))
                        if auto_scanned_data["Col_O_Fuel_Sensor_Status"] and auto_scanned_data["Col_O_Fuel_Sensor_Status"] != "Ok":
                            default_fuel_status = auto_scanned_data["Col_O_Fuel_Sensor_Status"]

                        default_fuel_docket = str(s_row.get('Docket no.', ''))
                        if (not default_fuel_docket or default_fuel_docket.lower() in ['', 'nan', 'none']) and auto_scanned_data["Col_P_Docket_no"]:
                            default_fuel_docket = auto_scanned_data["Col_P_Docket_no"]

                        st.success(f"Site Found: **{s_row.get('SAIP ID')}** | Auto-Scanned Source: **{auto_scanned_data['source']}**")

                        with st.form("single_site_inline_edit_form"):
                            se1, se2 = st.columns(2)
                            with se1:
                                edit_stat = st.selectbox("DG Automation Status:", STATUS_CHOICES, index=STATUS_CHOICES.index(default_stat) if default_stat in STATUS_CHOICES else 0)
                                edit_bkt = st.selectbox("Problem Bucket:", ["None"] + BUCKET_LIST, index=BUCKET_LIST.index(default_bkt) + 1 if default_bkt in BUCKET_LIST else 0)
                                
                                edit_fuel_status = st.selectbox("Fuel Sensor Status (Col O):", FUEL_STATUS_CHOICES, index=FUEL_STATUS_CHOICES.index(default_fuel_status) if default_fuel_status in FUEL_STATUS_CHOICES else 0)
                                
                                # ⚡ FUEL SENSOR DOCKET NO (Col P) - APPEARS DYNAMICALLY IF FUEL SENSOR FAULTY
                                edit_fuel_docket = ""
                                if edit_fuel_status == "Fuel Sensor faulty":
                                    edit_fuel_docket = st.text_input("Fuel Sensor Docket No (Col P):", value=default_fuel_docket if default_fuel_docket.lower() != 'nan' else "")

                                edit_docket = st.text_input("Present Docket No (Col V):", value=default_docket if default_docket.lower() != 'nan' else "")
                                
                                raw_open_date_val = s_row.get('Open Date')
                                if not raw_open_date_val or pd.isna(raw_open_date_val) or str(raw_open_date_val).lower() in ['nan', 'none', '']:
                                    raw_open_date_val = auto_scanned_data["Col_Q_Open_Date"]
                                
                                open_date_str_val = clean_date_str(raw_open_date_val)
                                edit_open_date_str = st.text_input("Open Date (Col Q) [Optional]:", value=open_date_str_val)

                                raw_date_val = s_row.get('Present Docket raise Date')
                                if not raw_date_val or pd.isna(raw_date_val) or str(raw_date_val).lower() in ['nan', 'none', '']:
                                    raw_date_val = auto_scanned_data["Col_W_Present_Docket_raise_Date"]
                                
                                faulty_date_str_val = clean_date_str(raw_date_val)
                                edit_faulty_date_str = st.text_input("Present Docket raise Date (Faulty Date - Col W) [Optional]:", value=faulty_date_str_val)

                            with se2:
                                edit_rem = st.text_area("Present Remarks / Complaint:", value=default_rem if default_rem.lower() != 'nan' else "")

                            submit_single_edit = st.form_submit_button("💾 Save Site Updates & Auto-Calculate Aging", type="primary", use_container_width=True)
                            if submit_single_edit:
                                old_docket = str(s_row.get('Present Docket No.', '')).strip()
                                if edit_docket and old_docket and old_docket.lower() not in ['', 'nan', 'none'] and old_docket != edit_docket:
                                    st.session_state.master_tracker_df = archive_current_fault_to_previous(row_idx, st.session_state.master_tracker_df)

                                calc_aging = 0
                                if edit_faulty_date_str.strip():
                                    try:
                                        parsed_faulty_date = pd.to_datetime(edit_faulty_date_str.strip()).date()
                                        current_eval_date = date(2026, 9, 28)
                                        calc_aging = (current_eval_date - parsed_faulty_date).days
                                        if calc_aging < 0:
                                            calc_aging = 0
                                    except:
                                        calc_aging = int(s_row.get("Aging (Day's)", 0)) if pd.notna(s_row.get("Aging (Day's)")) else 0

                                st.session_state.master_tracker_df.at[row_idx, 'DG Automation Status'] = edit_stat
                                st.session_state.master_tracker_df.at[row_idx, 'Bucket'] = None if edit_bkt == "None" else edit_bkt
                                st.session_state.master_tracker_df.at[row_idx, 'Fuel Sensor Status'] = edit_fuel_status
                                st.session_state.master_tracker_df.at[row_idx, 'Docket no.'] = edit_fuel_docket if edit_fuel_status == "Fuel Sensor faulty" else ""
                                st.session_state.master_tracker_df.at[row_idx, 'Present Docket No.'] = edit_docket
                                st.session_state.master_tracker_df.at[row_idx, 'Open Date'] = edit_open_date_str.strip()
                                st.session_state.master_tracker_df.at[row_idx, 'Present Docket raise Date'] = edit_faulty_date_str.strip()
                                st.session_state.master_tracker_df.at[row_idx, 'Present Remarks'] = edit_rem
                                st.session_state.master_tracker_df.at[row_idx, "Aging (Day's)"] = calc_aging
                                st.session_state.master_tracker_df.at[row_idx, "Aging_Num"] = calc_aging
                                st.success(f"Site `{search_edit_site}` updated successfully! Auto-Calculated Aging: **{calc_aging} Days**")
                                st.rerun()

                        st.markdown("<hr style='margin: 15px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)
                        st.markdown("<h4 style='color: #0f172a; margin-bottom: 10px;'>⚡ TT Closure & Record Removal Operations</h4>", unsafe_allow_html=True)
                        
                        col_bt1, col_bt2 = st.columns(2)
                        with col_bt1:
                            if st.button("✅ Close TT & Reset to Automation Ok", type="primary", use_container_width=True):
                                st.session_state.master_tracker_df = clear_site_active_fault_data(search_edit_site, st.session_state.master_tracker_df)
                                st.success(f"TT closed and site `{search_edit_site}` reset to Automation Ok successfully! Previous fault archived.")
                                st.rerun()
                        with col_bt2:
                            if st.button(f"🚨 Permanently Remove Site `{search_edit_site}`", type="secondary", use_container_width=True):
                                st.session_state.master_tracker_df = st.session_state.master_tracker_df.drop(index=row_idx).reset_index(drop=True)
                                st.success(f"Site `{search_edit_site}` removed from Master Tracker successfully!")
                                st.rerun()

        with edit_tab2:
            with st.container(border=True):
                st.markdown("<h3 style='margin:0 0 10px 0; color: #0f172a;'>📊 Full Master Tracker Spreadsheet Inline Grid Editor</h3>", unsafe_allow_html=True)
                st.caption("Use the search box below to filter rows by SAIP ID, JC, State, or any keyword before editing.")
                
                search_grid_query = st.text_input("🔍 Filter Master Grid Rows (by SAIP ID, JC, State, Supervisor etc.):", "").strip().upper()
                
                filtered_grid_df = st.session_state.master_tracker_df.copy()
                if search_grid_query:
                    mask = filtered_grid_df.astype(str).apply(lambda col: col.str.contains(search_grid_query, case=False, na=False)).any(axis=1)
                    filtered_grid_df = filtered_grid_df[mask]
                    st.info(f"Showing {len(filtered_grid_df):,} matching rows out of {len(st.session_state.master_tracker_df):,} total sites.")

                edited_full_master = st.data_editor(
                    filtered_grid_df, 
                    use_container_width=True, 
                    height=500, 
                    num_rows="dynamic"
                )
                
                if st.button("💾 Commit & Save Full Master Grid Changes", type="primary", use_container_width=True):
                    if search_grid_query:
                        full_df = st.session_state.master_tracker_df.copy()
                        full_df.update(edited_full_master)
                        st.session_state.master_tracker_df = full_df
                    else:
                        st.session_state.master_tracker_df = edited_full_master.copy()
                    
                    if "Aging (Day's)" in st.session_state.master_tracker_df.columns:
                        st.session_state.master_tracker_df['Aging_Num'] = pd.to_numeric(st.session_state.master_tracker_df["Aging (Day's)"], errors='coerce').fillna(0)

                    st.success("Full Master Tracker dataset updated and saved successfully across all modules!")
                    st.rerun()

# ---------------------------------------------------------
# 7. AI SITE DIAGNOSTICS (PROFESSIONAL ENTERPRISE EDITION)
# ---------------------------------------------------------
elif page == "🔍 AI Site Diagnostics":
    st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
    st.caption("Circle-wide deep diagnostics, equipment specs, telemetry mapping, and field intervention radar.")

    with st.container(border=True):
        st.markdown("<h4 style='margin:0 0 10px 0; color: #0f172a;'>🎯 Targeted Site Telemetry Search</h4>", unsafe_allow_html=True)
        s_col1, s_col2 = st.columns([3.5, 1])
        with s_col1:
            sq = st.text_input(
                "Search Network Site:",
                placeholder="Enter SAIP ID (e.g. 9011, BARA, DNGI, 9020, G003)...",
                label_visibility="collapsed"
            ).strip().upper()
        with s_col2:
            clear_btn = st.button("🔄 Reset Search", use_container_width=True)
            if clear_btn:
                sq = ""

    if not sq:
        with st.container(border=True):
            st.markdown("<h3 style='margin:0 0 12px 0; color: #0f172a;'>⚡ Circle Network Overview & Diagnostics Radar</h3>", unsafe_allow_html=True)
            tot_s = len(df_status) if not df_status.empty else 0
            auto_s = len(df_status[df_status['DG Automation Status'] == 'Automation Ok']) if not df_status.empty else 0
            manual_mode = len(df_status[df_status['DG Automation Status'] == 'Manual Mode']) if not df_status.empty else 0
            bd_s = len(df_status[df_status['DG Automation Status'] == 'DG Breakdown']) if not df_status.empty else 0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Circle Base", f"{tot_s:,}")
            c2.metric("Automation Healthy", f"{auto_s:,}", f"{round((auto_s/tot_s)*100, 1) if tot_s else 0}%")
            c3.metric("Manual Mode Alerts", manual_mode, f"-{round((manual_mode/tot_s)*100, 1) if tot_s else 0}%", delta_color="inverse")
            c4.metric("Active Breakdowns", bd_s, f"-{round((bd_s/tot_s)*100, 1) if tot_s else 0}%", delta_color="inverse")
            
            st.markdown("<hr style='margin: 14px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 14px; font-weight: 600; color: #475569;'>💡 Type an SAIP ID in the search box above to access full hardware parameters, fuel probe telemetry, and automatic AI root-cause analysis.</p>", unsafe_allow_html=True)

    else:
        matches = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)] if not df_status.empty else pd.DataFrame()

        if matches.empty:
            st.error(f"❌ No network records found matching `{sq}` in the Master Automation Tracker.")
        else:
            if len(matches) > 1:
                with st.container(border=True):
                    st.markdown("<p style='font-size: 15px; font-weight: 700; margin-bottom: 6px; color: #0f172a;'>Multiple Sites Found:</p>", unsafe_allow_html=True)
                    selected_site = st.selectbox("Select Target SAIP ID:", matches['SAIP ID'].tolist(), label_visibility="collapsed")
                    site_row = matches[matches['SAIP ID'] == selected_site].iloc[0]
            else:
                site_row = matches.iloc[0]
                selected_site = site_row['SAIP ID']

            status_val = str(site_row.get('DG Automation Status', 'Automation Ok'))
            badge_class = "badge-ok" if status_val == "Automation Ok" else "badge-crit" if "Breakdown" in status_val else "badge-warn"

            jc_str = str(site_row.get('JC', 'N/A'))
            state_str = str(site_row.get('State', 'N/A'))
            st_type = str(site_row.get('Site Type', 'N/A'))
            fac_5g = str(site_row.get('5G facality', 'N/A'))

            st.markdown(f"""
            <div class="custom-header-banner">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h2 style="margin: 0 !important; color: #ffffff !important; font-weight: 900 !important; font-size: 26px !important; text-shadow: none !important;">⚡ <span style="color: #ffffff !important;">{selected_site}</span></h2>
                        <div style="margin-top: 8px !important; color: #ffffff !important; font-size: 15px !important; font-weight: 700 !important; letter-spacing: 0.02em;">
                            Territory: <span style="color: #38bdf8 !important; font-weight: 800 !important;">{jc_str}</span> | State: <span style="color: #ffffff !important; font-weight: 800 !important;">{state_str}</span> | Site Type: <span style="color: #ffffff !important; font-weight: 800 !important;">{st_type}</span> | 5G Facility: <span style="color: #ffffff !important; font-weight: 800 !important;">{fac_5g}</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <span class="status-badge {badge_class}">{status_val}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                k1, k2, k3, k4 = st.columns(4)
                aging_val = site_row.get("Aging (Day's)", 0)
                fs_val = str(site_row.get("Fuel Sensor Status", "Ok"))
                k1.metric("DG Manufacturer", f"{site_row.get('DG Make', 'N/A')}", f"{site_row.get('DG Rating', 'N/A')}")
                k2.metric("Active Problem Bucket", f"{site_row.get('Bucket', 'None')}", "Root-Cause")
                k3.metric("Incident Aging", f"{int(aging_val) if pd.notna(aging_val) else 0} Days", "Delay Bracket")
                k4.metric("Fuel Telemetry", fs_val, "Sensor Health", delta_color="normal" if fs_val == "Ok" else "inverse")

            bucket_val = str(site_row.get('Bucket', '')).strip()
            rem_val = str(site_row.get('Present Remarks', 'No active remarks logged.')).strip()

            if status_val == "Automation Ok":
                ai_inference = "✅ **Site Automation Normal:** Telemetry signals indicate the DG automation loop is active with no blocking dockets."
                sop_action = "Routine preventive maintenance only. Verify monthly battery health."
            elif "Breakdown" in status_val or bucket_val == "DG Breakdown":
                ai_inference = f"🚨 **Critical Breakdown Alarm:** Engine inoperative. Reported defect: `{rem_val}`."
                sop_action = "Immediate SE dispatch required. Escalate to DG OEM vendor for emergency field restoration."
            elif bucket_val == "GCU":
                ai_inference = f"⚡ **GCU / Controller Fault Detected:** Controller signal offline or improper pulse. Logged remarks: `{rem_val}`."
                sop_action = "Inspect RS485 communication bus and replace controller unit if unrecoverable."
            elif bucket_val == "Fuel Sensor":
                ai_inference = f"⛽ **Fuel Telemetry Signal Loss:** Fuel probe data corrupted or missing. Reported: `{rem_val}`."
                sop_action = "Dispatch fuel sensor combo calibration kit; inspect sensor wiring harness."
            elif bucket_val == "OEM Spare parts":
                ai_inference = f"🛠️ **Component Replacement Required:** Waiting on OEM hardware parts. Defect: `{rem_val}`."
                sop_action = "Track supply chain docket with OEM vendor. Expedite parts dispatch to Circle TRT."
            else:
                ai_inference = f"⚠️ **Attention Required:** Manual mode active. Problem classified under `{bucket_val}`."
                sop_action = "Verify site access and contact the local supervisor for direct diagnosis."

            st.markdown(f"""
            <div class="auto-docket-box" style="margin-top: 14px;">
                <b style="color: #1e3a8a;">🧠 AI Diagnostic Inference:</b> {ai_inference}<br>
                <b style="color: #1e3a8a;">🎯 Recommended Operational Action (SOP):</b> {sop_action}
            </div>
            """, unsafe_allow_html=True)

            diag_t1, diag_t2, diag_t3 = st.tabs([
                "📋 Technical Asset Specifications",
                "⚡ Master Tracker (Live) Telemetry",
                "⏳ Resolution History & Previous Dockets (Col Y to AB)"
            ])

            with diag_t1:
                with st.container(border=True):
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        st.markdown(f"**DG Make:** `{site_row.get('DG Make', 'N/A')}`")
                        st.markdown(f"**DG Rating:** `{site_row.get('DG Rating', 'N/A')}`")
                        st.markdown(f"**OEM Vendor:** `{site_row.get('OEM Vendor', 'N/A')}`")
                        st.markdown(f"**EB Grid Connection:** `{site_row.get('EB/Non EB', 'N/A')}`")
                        st.markdown(f"**Battery Backup (Min):** `{site_row.get('F.Battery Backup (Min)', 'N/A')}`")
                    with c_s2:
                        st.markdown(f"**Supervisor Name:** `{site_row.get('Supervisor Name', 'N/A')}`")
                        st.markdown(f"**TRT Personnel:** `{site_row.get('TRT Name', 'N/A')}`")
                        st.markdown(f"**Contact Number:** `{site_row.get('Contact No.', 'N/A')}`")
                        st.markdown(f"**Dependent Sites:** `{site_row.get('Dependent Site', 'None')}`")

            with diag_t2:
                with st.container(border=True):
                    st.markdown("<p style='color: #0f172a; font-weight: 700; margin-bottom: 8px;'>Master Tracker Live Telemetry (Col O to AB)</p>", unsafe_allow_html=True)
                    master_telemetry_df = pd.DataFrame({
                        "Field": [
                            "Col O: Fuel Sensor Status", "Col P: Docket no.", "Col Q: Open Date",
                            "Col S: DG Automation Status", "Col T: Present Remarks",
                            "Col U: Bucket", "Col V: Present Docket No.", "Col W: Present Docket raise Date",
                            "Col X: Aging (Day's)", "Col Y: Timeline"
                        ],
                        "Master Tracker (Live)": [
                            str(site_row.get("Fuel Sensor Status", "")),
                            str(site_row.get("Docket no.", "")),
                            clean_date_str(site_row.get("Open Date", "")),
                            str(site_row.get("DG Automation Status", "")),
                            str(site_row.get("Present Remarks", "")),
                            str(site_row.get("Bucket", "")),
                            str(site_row.get("Present Docket No.", "")),
                            clean_date_str(site_row.get("Present Docket raise Date", "")),
                            str(site_row.get("Aging (Day's)", "")),
                            str(site_row.get("Timeline", ""))
                        ]
                    })
                    st.dataframe(master_telemetry_df, use_container_width=True, hide_index=True)

            with diag_t3:
                with st.container(border=True):
                    h1, h2 = st.columns(2)
                    h1.metric("Previous Docket No (Col AA)", str(site_row.get('Previous Docket No.', 'None')))
                    h2.metric("Previous Raise Date (Col AB)", clean_date_str(site_row.get('Previous Docket raise Date', 'None')))
                    st.markdown("<hr style='margin: 10px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)
                    st.markdown(f"**Previous Resolution Remarks (Col Z):**")
                    prev_rem_text = str(site_row.get('Previous Remarks', 'No previous historical remarks recorded.'))
                    st.markdown(f"""
                    <div class="previous-remarks-box">
                        {prev_rem_text}
                    </div>
                    """, unsafe_allow_html=True)
