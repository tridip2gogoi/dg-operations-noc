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

# Custom Corporate NOC Styling with High Contrast White Cards & 100% Visible White Tabs
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

    .stTextInput label, .stSelectbox label, .stDateInput label {
        color: #ffffff !important;
        font-weight: 700 !important;
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

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid #e2e8f0 !important;
        padding: 14px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span,
    div[data-testid="stVerticalBlockBorderWrapper"] label,
    div[data-testid="stVerticalBlockBorderWrapper"] h1,
    div[data-testid="stVerticalBlockBorderWrapper"] h2,
    div[data-testid="stVerticalBlockBorderWrapper"] h3,
    div[data-testid="stVerticalBlockBorderWrapper"] h4 {
        color: #0f172a !important;
        text-shadow: none !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"] * {
        color: #0f172a !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricLabel"] * {
        color: #64748b !important;
    }

    .status-badge {
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-ok { background-color: #dcfce7; color: #15803d !important; border: 1px solid #bbf7d0; }
    .badge-warn { background-color: #fef9c3; color: #854d0e !important; border: 1px solid #fef08a; }
    .badge-crit { background-color: #fee2e2; color: #b91c1c !important; border: 1px solid #fecaca; }
</style>
""", unsafe_allow_html=True)

DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio.xlsx"

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
            else:
                df_open_cm = pd.read_excel(xls_cm, sheet_name=0)
            
            if not df_open_cm.empty and 'COMPLAINT LOGGIN DATE' in df_open_cm.columns:
                df_open_cm['COMPLAINT LOGGIN DATE'] = df_open_cm['COMPLAINT LOGGIN DATE'].apply(clean_date_str)
        except Exception as e:
            st.warning(f"Note on CM tracker: {e}")

    if ila_file and is_valid_source(ila_file):
        try:
            xls_ila = pd.ExcelFile(ila_file)
            df_ila = pd.read_excel(xls_ila, sheet_name=xls_ila.sheet_names[0])
        except Exception as e:
            st.warning(f"Note on ILA-AG1 tracker: {e}")

    return df_status, df_fuel, df_open_cm, df_ila, df_cr_data

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

            is_fuel = "fuel" in new_complaint.lower() or "fuel" in new_bucket.lower()
            if is_fuel:
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
    if df_target.empty:
        return df_target
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
    if df_target.empty or not site_id:
        return df_target
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
    if df_target.empty or not site_id:
        return df_target
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
ila_source = uploaded_ila if uploaded_ila is not None else None

df_status_raw, df_fuel_raw, df_open_cm, df_ila_raw, df_cr_data = load_all_trackers(dg_source, cm_source, ila_source)

file_key = str(getattr(uploaded_dg, 'name', dg_source))
if "loaded_file_key" not in st.session_state or st.session_state.loaded_file_key != file_key:
    st.session_state.loaded_file_key = file_key
    st.session_state.master_tracker_df = df_status_raw.copy()
    st.session_state.fuel_tracker_df = df_fuel_raw.copy()
    st.session_state.ila_tracker_df = df_ila_raw.copy()

df_status = st.session_state.master_tracker_df
df_fuel = st.session_state.fuel_tracker_df
df_ila = st.session_state.ila_tracker_df

if not df_status.empty:
    st.sidebar.success(f"Master: {len(df_status)} Monitored Sites Active")
else:
    st.sidebar.warning("⚠️ No data loaded. Upload Master Tracker.")

if not df_open_cm.empty:
    st.sidebar.success(f"CM Tracker: {len(df_open_cm)} Open Incidents Synced")

if not df_ila.empty:
    st.sidebar.success(f"ILA-AG1: {len(df_ila)} Records Loaded")

if not df_status.empty and "Aging (Day's)" in df_status.columns:
    df_status['Aging_Num'] = pd.to_numeric(df_status["Aging (Day's)"], errors='coerce')
    bins = [-1, 0, 7, 15, 30, 60, 90, 100000]
    labels = ['0 Days', '1-7 Days', '8-15 Days', '16-30 Days', '31-60 Days', '61-90 Days', '>90 Days']
    df_status['Aging_Bracket'] = pd.cut(df_status['Aging_Num'], bins=bins, labels=labels)

page = st.sidebar.radio("NOC Operations Navigation:", [
    "📊 Executive Control Center",
    "⚡ O to AB Automated Sync Engine",
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
                st.markdown("<div style='margin: 0 0 10px 0; color: #0f172a; font-size: 18px; font-weight: 800;'>Circle JC Wise Automation Health</div>", unsafe_allow_html=True)
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
                st.markdown("<div style='margin: 0 0 10px 0; color: #0f172a; font-size: 18px; font-weight: 800;'>DG Make Fleet Allocation</div>", unsafe_allow_html=True)
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
# 2. O TO AB AUTOMATED SYNC ENGINE
# ---------------------------------------------------------
elif page == "⚡ O to AB Automated Sync Engine":
    st.markdown("## ⚡ Master Automation Tracker: Col O to AB Auto-Update Engine")
    st.caption("AI-driven pipeline mapping CM Tracker (`Open Site`) directly into Col O to AB of `Automation Status`.")

    if df_status.empty:
        st.warning("Please verify that the DG Master Tracker is uploaded.")
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
            file_name=f"Updated_DG_Automation_Tracker_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ---------------------------------------------------------
# 3. FLEET ANALYTICS & ROOT-CAUSE
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
        with st.container(border=True):
            st.markdown(f"<div style='color: #0f172a; font-size: 18px; font-weight: 800; margin-bottom: 10px;'>Status Summary ({selected_fleet_jc})</div>", unsafe_allow_html=True)
            stat_summary = filtered_status['DG Automation Status'].value_counts(dropna=False).reset_index()
            stat_summary.columns = ['Status Category', 'Site Count']
            st.dataframe(stat_summary, use_container_width=True, hide_index=True)

    with col2:
        with st.container(border=True):
            st.markdown(f"<div style='color: #0f172a; font-size: 18px; font-weight: 800; margin-bottom: 10px;'>Bucket Distribution ({selected_fleet_jc})</div>", unsafe_allow_html=True)
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
            st.markdown("<h4 style='margin-bottom:10px;'>JC vs DG Automation Status Cross-Tabulation</h4>", unsafe_allow_html=True)
            status_matrix = pd.crosstab(df_status['JC'], df_status['DG Automation Status'], margins=True, margins_name="Total")
            st.dataframe(status_matrix, use_container_width=True)

    with tab_m2:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px;'>JC vs Root-Cause Bucket Cross-Tabulation</h4>", unsafe_allow_html=True)
            all_valid_bkt = df_status[df_status['Bucket'].notna()]
            bucket_matrix = pd.crosstab(all_valid_bkt['JC'], all_valid_bkt['Bucket'], margins=True, margins_name="Total")
            st.dataframe(bucket_matrix, use_container_width=True)

    with tab_m3:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px;'>GCU Sites: JC vs DG Make & KVA Breakdown</h4>", unsafe_allow_html=True)
            df_gcu = df_status[df_status['Bucket'] == 'GCU'].copy()
            df_gcu['DG Make Clean'] = df_gcu['DG Make'].fillna('Unspecified')
            df_gcu['DG Rating Clean'] = df_gcu['DG Rating'].fillna('Unspecified') if 'DG Rating' in df_gcu.columns else 'Unspecified'
            ct_gcu_detailed = pd.crosstab([df_gcu['JC'], df_gcu['DG Make Clean']], df_gcu['DG Rating Clean'], margins=True, margins_name="Total")
            st.dataframe(ct_gcu_detailed, use_container_width=True)

    with tab_m4:
        with st.container(border=True):
            st.markdown("<h4 style='margin-bottom:10px;'>JC-Wise: DG Breakdown & Manual (GCU, OEM, Breakdown)</h4>", unsafe_allow_html=True)
            target_statuses = ['DG Breakdown', 'Manual Mode']
            target_bkts = ['GCU', 'OEM Spare parts', 'DG Breakdown']
            df_sub = df_status[df_status['DG Automation Status'].isin(target_statuses) & df_status['Bucket'].isin(target_bkts)].copy()
            df_sub['Clean_Docket'] = df_sub['Present Docket No.'].fillna('').astype(str).str.strip()
            df_sub['Docket_Status'] = df_sub['Clean_Docket'].apply(lambda x: 'Docket Received' if x.lower() not in ['', 'nan', 'none', 'n/a', '0'] else 'Docket Pending')
            if 'JC' in df_sub.columns:
                ct_sub_bkt = pd.crosstab([df_sub['JC'], df_sub['DG Automation Status'], df_sub['Bucket']], df_sub['Docket_Status'], margins=True, margins_name="Total")
                st.dataframe(ct_sub_bkt, use_container_width=True)
            else:
                st.warning("JC column not found in dataset.")

# ---------------------------------------------------------
# 4. FUEL SENSOR TELEMETRY
# ---------------------------------------------------------
elif page == "⛽ Fuel Sensor Telemetry":
    st.markdown("## ⛽ Fuel Sensor Fault Telemetry")
    if not df_fuel.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Faulty Sensors", len(df_fuel))
        c2.metric("Most Affected JC", df_fuel['JC'].mode()[0] if 'JC' in df_fuel.columns else "N/A")
        c3.metric("Primary Fault Make", df_fuel['DG MAKE'].mode()[0] if 'DG MAKE' in df_fuel.columns else "N/A")
        c4.metric("Primary Fault Rating", df_fuel['KVA'].mode()[0] if 'KVA' in df_fuel.columns else "N/A")

        with st.container(border=True):
            st.dataframe(df_fuel, use_container_width=True)
    else:
        st.info("No active fuel sensor faults detected.")

# ---------------------------------------------------------
# 5. CRITICAL AGING ESCALATIONS
# ---------------------------------------------------------
elif page == "⏳ Critical Aging Escalation Monitor":
    st.markdown("## ⏳ Critical Aging Escalation Radar & JC-Wise Breakdown")
    aging_valid = df_status[df_status['Aging_Num'].notna()].copy()
    crit_df = aging_valid[aging_valid['Aging_Num'] > 90].copy()

    m1, m2 = st.columns(2)
    m1.metric("Total Delayed Sites", len(aging_valid))
    m2.metric("Severe Delays (>90 Days)", len(crit_df))
    if not crit_df.empty:
        with st.container(border=True):
            st.dataframe(crit_df.sort_values(by='Aging_Num', ascending=False), use_container_width=True)

# ---------------------------------------------------------
# 6. ILA-AG1 OPERATIONS TRACKER (NEW MODULE)
# ---------------------------------------------------------
elif page == "📈 ILA-AG1 Operations Tracker":
    st.markdown("## 📈 ILA-AG1 Operations Tracker & Telemetry")
    st.caption("Integrated tracking and analysis of ILA-AG1 operational logs.")

    if not df_ila.empty:
        with st.container(border=True):
            st.markdown(f"### ILA-AG1 Registry Summary ({len(df_ila):,} Records)")
            st.dataframe(df_ila, use_container_width=True)

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
    else:
        st.info("📂 Please upload the **ILA-AG1 Tracker** file from the sidebar upload section to initialize this module.")

# ---------------------------------------------------------
# 7. IN-PORTAL MASTER TRACKER EDITOR
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
            "📊 Bulk Inline Grid Editor (Spreadsheet View)"
        ])

        with edit_tab1:
            with st.container(border=True):
                search_edit_site = st.text_input("Enter SAIP ID to modify or resolve:").strip().upper()
                if search_edit_site:
                    match_idx = df_status[df_status['SAIP ID'].astype(str).str.strip().str.upper() == search_edit_site].index
                    if match_idx.empty:
                        st.error(f"Site `{search_edit_site}` not found.")
                    else:
                        row_idx = match_idx[0]
                        target_row = df_status.loc[row_idx]
                        st.write(f"Found site: {target_row['SAIP ID']} | Status: {target_row.get('DG Automation Status')}")

                        if st.button("✅ Reset to Automation Ok", type="primary"):
                            st.session_state.master_tracker_df = clear_site_active_fault_data(search_edit_site, st.session_state.master_tracker_df)
                            st.success(f"Site {search_edit_site} reset successfully!")
                            st.rerun()

        with edit_tab2:
            with st.container(border=True):
                st.dataframe(df_status.head(100), use_container_width=True)

# ---------------------------------------------------------
# 8. AI SITE DIAGNOSTICS
# ---------------------------------------------------------
elif page == "🔍 AI Site Diagnostics":
    st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
    with st.container(border=True):
        sq = st.text_input("Enter SAIP ID to Diagnose:", placeholder="e.g. 9011, BARA, DNGI...").strip().upper()
    if sq and not df_status.empty and 'SAIP ID' in df_status.columns:
        match = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)]
        if not match.empty:
            r = match.iloc[0]
            with st.container(border=True):
                st.markdown(f"### ⚡ Site: {r['SAIP ID']} | Status: {r.get('DG Automation Status', 'N/A')}")
                k1, k2, k3 = st.columns(3)
                k1.metric("DG Make", f"{r.get('DG Make', 'N/A')}")
                k2.metric("Bucket", f"{r.get('Bucket', 'None')}")
                k3.metric("Aging", f"{r.get('Aging (Day\'s)', 0)} Days")
