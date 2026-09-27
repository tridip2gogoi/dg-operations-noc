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

# Custom Corporate NOC Styling with High Contrast Tabs, Radios & Clear White Cards
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Telecom Background with Dark Contrast Overlay */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.88)), 
                    url("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* ⚡ RADIO BUTTON VISIBILITY FIX */
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
        background: rgba(30, 41, 59, 0.75);
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-right: 8px;
    }

    /* ⚡ TABS ULTRA-HIGH CONTRAST VISIBILITY FIX */
    div[data-testid="stTabs"] button[role="tab"],
    button[data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.95) !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 20px !important;
        margin-right: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }
    div[data-testid="stTabs"] button[role="tab"] *,
    button[data-baseweb="tab"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0284c7 !important;
        border-bottom: 3px solid #38bdf8 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Headings */
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

    /* Metric Values */
    [data-testid="stMetricValue"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] * {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* Sidebar */
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

    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(226, 232, 240, 0.8);
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
    .closure-success-box {
        background-color: rgba(240, 253, 244, 0.98);
        border: 1px solid #86efac;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #166534 !important;
    }
    .closure-success-box * {
        color: #166534 !important;
    }

    /* Native container white card styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid #e2e8f0 !important;
        padding: 14px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span,
    div[data-testid="stVerticalBlockBorderWrapper"] label {
        color: #0f172a !important;
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

# --- HELPER: DATE FORMATTERS ---
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

# --- MULTI-ROLE CREDENTIALS ---
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

# --- DATA PIPELINE LOADER (EMPTY & NON-DG ROWS FILTERED) ---
@st.cache_data
def load_all_trackers(dg_file, cm_file, cr_file=None):
    df_status = pd.DataFrame()
    df_fuel = pd.DataFrame()
    df_open_cm = pd.DataFrame()
    df_cr_data = pd.DataFrame()
    
    if is_valid_source(dg_file):
        try:
            xls_dg = pd.ExcelFile(dg_file)
            sheet_target = "Automation Status" if "Automation Status" in xls_dg.sheet_names else xls_dg.sheet_names[0]
            df_status = pd.read_excel(xls_dg, sheet_name=sheet_target)
            
            # ⚡ ১. খালী ৰো আৰু অস্তিত্বহীন ছাইট আঁতৰোৱা (Eliminating Phantom Blank Rows)
            if 'SAIP ID' in df_status.columns:
                df_status = df_status[df_status['SAIP ID'].notna()]
                df_status['SAIP ID'] = df_status['SAIP ID'].astype(str).str.strip()
                df_status = df_status[~df_status['SAIP ID'].str.lower().isin(['', 'nan', 'none', 'total', '0', 'null'])]
            
            # ⚡ ২. কেৱল প্ৰকৃত ডিজি থকা ছাইট ৰখা (ৰিমুভ নাল/নন-ডিজি)
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

# --- AUTOMATIC AI COL O TO AB EXTRACTION ---
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

# --- AUTO-SYNC EDITED IN-PORTAL DATA DIRECTLY TO ENGINE ---
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

# --- CLEAR ACTIVE FAULT DATA ---
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

# --- AUTOMATIC TT CLOSURE RECONCILIATION: PRESENT SHIFT TO Y-AB ---
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

        # ⚡ কেৱল Viewer-ৰ বাবে দৃশ্যমান সহায়ক বক্স (Super Admin সম্পূৰ্ণ গোপন)
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
uploaded_cr = st.sidebar.file_uploader("3. Complaint Register (Optional)", type=["xlsx", "xls"])

detected_excel = DEFAULT_EXCEL
if not os.path.exists(DEFAULT_EXCEL):
    local_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
    for lf in local_files:
        if "CM" not in lf.upper():
            detected_excel = lf
            break

cm_source = uploaded_cm if uploaded_cm is not None else DEFAULT_CM_TRACKER
dg_source = uploaded_dg if uploaded_dg is not None else detected_excel
cr_source = uploaded_cr if uploaded_cr is not None else None

df_status_raw, df_fuel_raw, df_open_cm, df_cr_data = load_all_trackers(dg_source, cm_source, cr_source)

file_key = str(getattr(uploaded_dg, 'name', dg_source))
if "loaded_file_key" not in st.session_state or st.session_state.loaded_file_key != file_key:
    st.session_state.loaded_file_key = file_key
    st.session_state.master_tracker_df = df_status_raw.copy()
    st.session_state.fuel_tracker_df = df_fuel_raw.copy()

df_status = st.session_state.master_tracker_df
df_fuel = st.session_state.fuel_tracker_df

if not df_status.empty:
    st.sidebar.success(f"Master: {len(df_status)} Monitored Sites Active")
else:
    st.sidebar.warning("⚠️ No data loaded. Upload Master Tracker.")

if not df_open_cm.empty:
    st.sidebar.success(f"CM Tracker: {len(df_open_cm)} Open Incidents Synced")

# Preprocessing Numeric Aging and Intervals
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
    "✏️ In-Portal Master Tracker Editor",
    "🔍 AI Site Diagnostics"
])

# ---------------------------------------------------------
# 1. EXECUTIVE CONTROL CENTER (ACCURATE DG BASE COUNT)
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
        
        # ⚡ প্ৰথম গ্ৰাফ: Circle JC Wise Automation Health
        with c1:
            with st.container(border=True):
                st.markdown("<div style='margin: 0 0 10px 0; color: #0f172a; font-size: 18px; font-weight: 800;'>Circle JC Wise Automation Health</div>", unsafe_allow_html=True)
                if "JC" in df_status.columns and "DG Automation Status" in df_status.columns:
                    fig_bar = px.histogram(
                        df_status, x="JC", color="DG Automation Status", barmode="group",
                        color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#6366f1"]
                    )
                    fig_bar.update_layout(
                        height=350,
                        margin=dict(l=10, r=10, t=10, b=10),
                        plot_bgcolor="#ffffff",
                        paper_bgcolor="#ffffff",
                        font=dict(color="#0f172a", family="Inter, sans-serif"),
                        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title_font=dict(color="#0f172a")),
                        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title_font=dict(color="#0f172a")),
                        legend=dict(font=dict(color="#0f172a"), bgcolor="rgba(255,255,255,0.9)")
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

        # ⚡ দ্বিতীয় গ্ৰাফ: DG Make Fleet Allocation (No NULL values)
        with c2:
            with st.container(border=True):
                st.markdown("<div style='margin: 0 0 10px 0; color: #0f172a; font-size: 18px; font-weight: 800;'>DG Make Fleet Allocation</div>", unsafe_allow_html=True)
                if "DG Make" in df_status.columns:
                    valid_makes = df_status[df_status['DG Make'].notna() & (df_status['DG Make'].astype(str).str.strip() != '')]
                    fig_donut = px.pie(valid_makes, names="DG Make", hole=0.58, color_discrete_sequence=px.colors.qualitative.Safe)
                    fig_donut.update_layout(
                        height=350,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="#ffffff",
                        plot_bgcolor="#ffffff",
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
    
    # ⚡ কন্টেইনাৰ ১: Status Summary
    with col1:
        with st.container(border=True):
            st.markdown(f"<div style='color: #0f172a; font-size: 18px; font-weight: 800; margin-bottom: 10px;'>Status Summary ({selected_fleet_jc})</div>", unsafe_allow_html=True)
            stat_summary = filtered_status['DG Automation Status'].value_counts(dropna=False).reset_index()
            stat_summary.columns = ['Status Category', 'Site Count']
            st.dataframe(stat_summary, use_container_width=True, hide_index=True)

    # ⚡ কন্টেইনাৰ ২: Bucket Distribution
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
                    height=340,
                    margin=dict(l=10, r=10, t=10, b=10),
                    plot_bgcolor="#ffffff",
                    paper_bgcolor="#ffffff",
                    font=dict(color="#0f172a", family="Inter, sans-serif"),
                    xaxis=dict(
                        showgrid=True, gridcolor="#f1f5f9", 
                        tickfont=dict(color="#0f172a", size=11),
                        title=dict(font=dict(color="#0f172a", weight="bold"))
                    ),
                    yaxis=dict(
                        showgrid=True, gridcolor="#f1f5f9", 
                        tickfont=dict(color="#0f172a"),
                        title=dict(font=dict(color="#0f172a", weight="bold"))
                    ),
                    coloraxis_colorbar=dict(
                        title=dict(text="Incidents", font=dict(color="#0f172a")),
                        tickfont=dict(color="#0f172a")
                    )
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
        st.markdown("### JC vs DG Automation Status Cross-Tabulation")
        status_matrix = pd.crosstab(df_status['JC'], df_status['DG Automation Status'], margins=True, margins_name="Total")
        st.dataframe(status_matrix, use_container_width=True)

    with tab_m2:
        st.markdown("### JC vs Root-Cause Bucket Cross-Tabulation")
        all_valid_bkt = df_status[df_status['Bucket'].notna()]
        bucket_matrix = pd.crosstab(all_valid_bkt['JC'], all_valid_bkt['Bucket'], margins=True, margins_name="Total")
        st.dataframe(bucket_matrix, use_container_width=True)

    with tab_m3:
        st.markdown("### GCU Sites: JC vs DG Make & KVA Breakdown")
        df_gcu = df_status[df_status['Bucket'] == 'GCU'].copy()
        df_gcu['DG Make Clean'] = df_gcu['DG Make'].fillna('Unspecified')
        df_gcu['DG Rating Clean'] = df_gcu['DG Rating'].fillna('Unspecified') if 'DG Rating' in df_gcu.columns else 'Unspecified'
        ct_gcu_detailed = pd.crosstab([df_gcu['JC'], df_gcu['DG Make Clean']], df_gcu['DG Rating Clean'], margins=True, margins_name="Total")
        st.dataframe(ct_gcu_detailed, use_container_width=True)

    with tab_m4:
        st.markdown("### DG Breakdown & DG Manual: GCU, OEM Spare parts & DG Breakdown")
        target_statuses = ['DG Breakdown', 'Manual Mode']
        target_bkts = ['GCU', 'OEM Spare parts', 'DG Breakdown']
        df_sub = df_status[df_status['DG Automation Status'].isin(target_statuses) & df_status['Bucket'].isin(target_bkts)].copy()
        df_sub['Clean_Docket'] = df_sub['Present Docket No.'].fillna('').astype(str).str.strip()
        df_sub['Docket_Status'] = df_sub['Clean_Docket'].apply(lambda x: 'Docket Received' if x.lower() not in ['', 'nan', 'none', 'n/a', '0'] else 'Docket Pending')
        ct_sub_bkt = pd.crosstab([df_sub['DG Automation Status'], df_sub['Bucket']], df_sub['Docket_Status'], margins=True, margins_name="Total")
        st.dataframe(ct_sub_bkt, use_container_width=True)

# ---------------------------------------------------------
# 4. FUEL SENSOR TELEMETRY
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
        tab_f1, tab_f2 = st.tabs(["📊 Fuel Sensor Faulty Sites (JC vs DG Make & KVA)", "📋 Active Fault Site Registry"])
        with tab_f1:
            ct_fuel_detailed = pd.crosstab([df_fuel['JC'], df_fuel['DG MAKE']], df_fuel['KVA'], margins=True, margins_name="Total")
            st.dataframe(ct_fuel_detailed, use_container_width=True)
        with tab_f2:
            disp_fuel_cols = ['SITE ID', 'JC', 'DG MAKE', 'KVA', 'DOCKET NUMBER', 'COMPLAINT LOGGIN DATE', 'NATURE OF COMPLAINT', 'STATUS']
            valid_disp_fuel = [c for c in disp_fuel_cols if c in df_fuel.columns]
            st.dataframe(df_fuel[valid_disp_fuel], use_container_width=True)
    else:
        st.info("No active fuel sensor faults detected in the current tracker.")

# ---------------------------------------------------------
# 5. CRITICAL AGING ESCALATION MONITOR
# ---------------------------------------------------------
elif page == "⏳ Critical Aging Escalation Monitor":
    st.markdown("## ⏳ Critical Aging Escalation Radar & JC-Wise Breakdown")
    st.caption("Comprehensive analysis of all site delay intervals and problem buckets cross-tabulated across Circle JCs.")

    aging_valid = df_status[df_status['Aging_Num'].notna()].copy()
    crit_df = aging_valid[aging_valid['Aging_Num'] > 90].copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Delayed Sites", len(aging_valid), "Active Incidents")
    m2.metric("Severe Delays (>90 Days)", len(crit_df), "Critical Escalations")
    m3.metric("Most Affected JC", crit_df['JC'].mode()[0] if not crit_df.empty else "N/A", f"{crit_df['JC'].value_counts().max()} Sites")
    m4.metric("Maximum Recorded Delay", f"{int(aging_valid['Aging_Num'].max()) if not aging_valid.empty else 0} Days")

    st.markdown("---")
    if 'Aging_Bracket' in df_status.columns:
        st.subheader("📊 1. JC-Wise All Aging Brackets Matrix")
        jc_aging_full = pd.crosstab(df_status['JC'], df_status['Aging_Bracket'].dropna(), margins=True, margins_name="Total")
        st.dataframe(jc_aging_full, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 2. Critical Escalation Sites Registry (>90 Days)")
    all_crit_jcs = ["All"] + sorted([str(x) for x in crit_df['JC'].dropna().unique()])
    selected_jc = st.selectbox("Filter Registry by JC Circle:", all_crit_jcs)
    filtered_crit = crit_df if selected_jc == "All" else crit_df[crit_df['JC'] == selected_jc]
    disp_cols = ['SAIP ID', 'JC', 'Bucket', 'DG Make', 'Present Docket No.', 'Aging_Num', 'Present Remarks', 'Timeline', 'Supervisor Name']
    valid_disp_cols = [c for c in disp_cols if c in filtered_crit.columns]
    st.dataframe(filtered_crit[valid_disp_cols].sort_values(by='Aging_Num', ascending=False), use_container_width=True)

# ---------------------------------------------------------
# 6. IN-PORTAL MASTER TRACKER EDITOR (RBAC PROTECTED)
# ---------------------------------------------------------
elif page == "✏️ In-Portal Master Tracker Editor":
    st.markdown("## ✏️ In-Portal Master Tracker Live Editor")
    st.caption(f"Authenticated Role: **{admin_role}** | Modifying telemetry and resolving active tickets.")

    # 🔒 VIEWER একাউণ্টৰ বাবে সকলো এডিট বন্ধ (Read-only)
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
                        <b>Fuel Sensor:</b> <code>{target_row.get('Fuel Sensor Status', 'Ok')}</code> (Docket: <code>{target_row.get('Docket no.', 'None')}</code>) | <b>Present Docket (Col V):</b> <code>{target_row.get('Present Docket No.', 'None')}</code> | <b>Raise Date (Col W):</b> <code>{clean_date_str(target_row.get('Present Docket raise Date', ''))}</code>
                    </div>
                    """, unsafe_allow_html=True)

                    action_mode = st.radio(
                        "Select Action for this Site:",
                        [
                            "📝 Modify Telemetry / Docket Fields",
                            "🧹 Remove Active Fault Data & Reset to Automation Ok",
                            "✅ Close TT / Incident (Auto-Shift Y to AB)",
                            "🗑️ Remove / Delete Site Record from Master Tracker"
                        ],
                        horizontal=True
                    )

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
                                new_fs_docket = st.text_input("Fuel Sensor Docket no. (Col P):", value=str(target_row.get('Docket no.', '')) if pd.notna(target_row.get('Docket no.')) else "")
                                fs_date_default = to_date_obj(target_row.get('Open Date', ''))
                                new_fs_open_date_cal = st.date_input("📅 Fuel Sensor Open Date (Col Q):", value=fs_date_default)
                                new_fs_open_date = new_fs_open_date_cal.strftime('%Y-%m-%d') if new_fs_open_date_cal else ""

                            with e_col2:
                                curr_bucket = str(target_row.get('Bucket', 'None'))
                                b_choices = ["None"] + BUCKET_LIST
                                b_idx = b_choices.index(curr_bucket) if curr_bucket in b_choices else 0
                                new_bucket = st.selectbox("Problem Bucket (Col U):", b_choices, index=b_idx)
                                new_docket = st.text_input("Present Docket No (Col V):", value=str(target_row.get('Present Docket No.', '')) if pd.notna(target_row.get('Present Docket No.')) else "")

                            with e_col3:
                                raise_date_default = to_date_obj(target_row.get('Present Docket raise Date', ''))
                                new_raise_date_cal = st.date_input("📅 Present Docket Raise Date (Col W):", value=raise_date_default)
                                new_raise_date = new_raise_date_cal.strftime('%Y-%m-%d') if new_raise_date_cal else ""
                                new_aging = st.number_input("Aging Days (Col X):", value=int(target_row.get("Aging (Day's)", 0)) if pd.notna(target_row.get("Aging (Day's)")) else 0, step=1)

                            new_remarks = st.text_area("Present Remarks (Col T):", value=str(target_row.get('Present Remarks', '')) if pd.notna(target_row.get('Present Remarks')) else "")
                            new_timeline = st.text_input("Timeline (Col Y):", value=str(target_row.get('Timeline', '')) if pd.notna(target_row.get('Timeline')) else "")
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
                                st.session_state.master_tracker_df.at[row_idx, 'Timeline'] = new_timeline

                                st.session_state.master_tracker_df = auto_sync_edited_data_to_engine(
                                    st.session_state.master_tracker_df, df_open_cm, df_cr_data
                                )
                                st.success(f"Site `{search_edit_site}` updated & automatically synced to ⚡ O to AB Engine!")
                                st.rerun()

                    elif action_mode == "🧹 Remove Active Fault Data & Reset to Automation Ok":
                        if st.button("🧹 Clear All Active Fault Details & Set Automation Ok", type="primary", use_container_width=True):
                            st.session_state.master_tracker_df = clear_site_active_fault_data(
                                search_edit_site, st.session_state.master_tracker_df
                            )
                            st.success(f"Active fault fields cleared for `{search_edit_site}` and restored to 'Automation Ok'. Synced to Master Tracker!")
                            st.rerun()

                    elif action_mode == "✅ Close TT / Incident (Auto-Shift Y to AB)":
                        with st.form("single_site_tt_close_form"):
                            close_c1, close_c2 = st.columns(2)
                            with close_c1:
                                cal_closed_date = st.date_input("📅 Closure Date (Col R, Calendar):", value=date.today())
                                str_closed_date = cal_closed_date.strftime('%Y-%m-%d')
                            with close_c2:
                                resolution_remarks = st.text_input("Closure / Replacement Remarks:", placeholder="e.g. OEM parts replaced, automation restored")

                            btn_tt_close = st.form_submit_button("✅ Close TT & Execute Auto-Shift to Col Y-AB", use_container_width=True, type="primary")
                            if btn_tt_close:
                                st.session_state.master_tracker_df = execute_tt_close_shift_to_y_ab(
                                    site_id=search_edit_site,
                                    closure_remarks=resolution_remarks,
                                    closure_date_str=str_closed_date,
                                    df_target=st.session_state.master_tracker_df
                                )
                                st.success(f"TT Closed for {search_edit_site}!")
                                st.rerun()

                    else:
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

    st.markdown("---")
    export_output = BytesIO()
    with pd.ExcelWriter(export_output, engine='openpyxl') as writer:
        st.session_state.master_tracker_df.to_excel(writer, sheet_name="Automation Status", index=False)
        if not df_fuel.empty:
            df_fuel.to_excel(writer, sheet_name="Fuel Sensor faulty", index=False)
    
    st.download_button(
        label="📥 Download Master Tracker (.xlsx) with Committed Portal Edits",
        data=export_output.getvalue(),
        file_name=f"DG_Tracker_Edited_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ---------------------------------------------------------
# 7. AI SITE DIAGNOSTICS (PROFESSIONAL ENTERPRISE EDITION)
# ---------------------------------------------------------
elif page == "🔍 AI Site Diagnostics":
    st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
    st.caption("Circle-wide deep diagnostics, equipment specs, telemetry mapping, and field intervention radar.")

    # ⚡ ছাৰ্চ বাৰ আৰু কন্ট্ৰ'ল পেনেল বগা কাৰ্ডত
    with st.container(border=True):
        st.markdown("<div style='color: #0f172a; font-size: 17px; font-weight: 800; margin-bottom: 8px;'>🎯 Targeted Site Telemetry Search</div>", unsafe_allow_html=True)
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
        # ⚡ ডিফল্ট অৱস্থা: যদি কোনো ছাইট চাৰ্চ কৰা নাই
        with st.container(border=True):
            st.markdown("<div style='color: #0f172a; font-size: 17px; font-weight: 800; margin-bottom: 12px;'>⚡ Circle Network Overview & Diagnostics Radar</div>", unsafe_allow_html=True)
            tot_s = len(df_status) if not df_status.empty else 0
            auto_s = len(df_status[df_status['DG Automation Status'] == 'Automation Ok']) if not df_status.empty else 0
            man_s = len(df_status[df_status['DG Automation Status'] == 'Manual Mode']) if not df_status.empty else 0
            bd_s = len(df_status[df_status['DG Automation Status'] == 'DG Breakdown']) if not df_status.empty else 0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Circle Base", f"{tot_s:,}")
            c2.metric("Automation Healthy", f"{auto_s:,}", f"{round((auto_s/tot_s)*100, 1) if tot_s else 0}%")
            c3.metric("Manual Mode Alerts", f"{man_s:,}", delta_color="inverse")
            c4.metric("Active Breakdowns", f"{bd_s:,}", delta_color="inverse")
            
            st.markdown("<hr style='margin: 14px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("<div style='color: #475569; font-size: 13px; font-weight: 600;'>💡 Type an SAIP ID in the search box above to access full hardware parameters, fuel probe telemetry, and automatic AI root-cause analysis.</div>", unsafe_allow_html=True)

    else:
        matches = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)] if not df_status.empty else pd.DataFrame()

        if matches.empty:
            st.error(f"❌ No network records found matching `{sq}` in the Master Automation Tracker.")
        else:
            if len(matches) > 1:
                with st.container(border=True):
                    st.markdown(f"<div style='color: #0f172a; font-size: 15px; font-weight: 700; margin-bottom: 6px;'>Multiple ({len(matches)}) Sites Found:</div>", unsafe_allow_html=True)
                    selected_site = st.selectbox("Select Target SAIP ID:", matches['SAIP ID'].tolist(), label_visibility="collapsed")
                    site_row = matches[matches['SAIP ID'] == selected_site].iloc[0]
            else:
                site_row = matches.iloc[0]
                selected_site = site_row['SAIP ID']

            cap_data = ai_capture_o_to_ab(selected_site, df_open_cm, df_status, df_cr_data)
            status_val = str(site_row.get('DG Automation Status', 'Automation Ok'))
            badge_class = "badge-ok" if status_val == "Automation Ok" else "badge-crit" if "Breakdown" in status_val else "badge-warn"

            # ⚡ ছাইটৰ হেডাৰ কাৰ্ড
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px 24px; margin-top: 14px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h2 style="margin: 0; color: #0f172a !important; font-weight: 800; font-size: 24px; text-shadow: none !important;">⚡ {selected_site}</h2>
                        <div style="margin-top: 4px; color: #475569 !important; font-size: 14px; font-weight: 600;">
                            Circle Territory: <b style="color: #0284c7;">{site_row.get('JC', 'N/A')}</b> | State: <b>{site_row.get('State', 'N/A')}</b> | Site Type: <b>{site_row.get('Site Type', 'N/A')}</b> | 5G Facility: <b>{site_row.get('5G facality', 'N/A')}</b>
                        </div>
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="status-badge {badge_class}">{status_val}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ⚡ KPI মেট্ৰিক কাৰ্ড
            with st.container(border=True):
                k1, k2, k3, k4 = st.columns(4)
                aging_val = site_row.get("Aging (Day's)", 0)
                fs_val = str(site_row.get("Fuel Sensor Status", "Ok"))
                k1.metric("DG Manufacturer", f"{site_row.get('DG Make', 'N/A')}", f"{site_row.get('DG Rating', 'N/A')}")
                k2.metric("Active Problem Bucket", f"{site_row.get('Bucket', 'None')}", "Root-Cause")
                k3.metric("Incident Aging", f"{int(aging_val) if pd.notna(aging_val) else 0} Days", "Delay Bracket")
                k4.metric("Fuel Telemetry", fs_val, "Sensor Health", delta_color="normal" if fs_val == "Ok" else "inverse")

            # ⚡ AI ৰুট-কজ ডায়গ্ৰাম আৰু একশ্যন
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

            # ⚡ ৩-টেব সমন্বিত বিশ্লেষণ
            diag_t1, diag_t2, diag_t3 = st.tabs([
                "📋 Technical Asset Specifications",
                "⚡ Active Dockets & Pipeline Reconciliation",
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
                        st.markdown(f"**Last Closed Date:** `{clean_date_str(site_row.get('Last Closed date', 'N/A'))}`")

            with diag_t2:
                with st.container(border=True):
                    st.markdown("<div style='color: #0f172a; font-weight: 700; margin-bottom: 8px;'>Live Master Tracker vs CM Open Docket Comparison</div>", unsafe_allow_html=True)
                    rec_table = pd.DataFrame({
                        "Field": [
                            "Col O: Fuel Sensor Status", "Col P: Docket No", "Col Q: Open Date",
                            "Col S: DG Automation Status", "Col T: Present Remarks", "Col U: Problem Bucket",
                            "Col V: Present Docket No", "Col W: Present Docket Raise Date",
                            "Col X: Aging (Days)", "Col Y: Timeline"
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
                        ],
                        "CM Tracker (Open Incidents)": [
                            cap_data.get("Col_O_Fuel_Sensor_Status", ""),
                            cap_data.get("Col_P_Docket_no", ""),
                            clean_date_str(cap_data.get("Col_Q_Open_Date", "")),
                            cap_data.get("Col_S_DG_Automation_Status", ""),
                            cap_data.get("Col_T_Present_Remarks", ""),
                            cap_data.get("Col_U_Bucket", ""),
                            cap_data.get("Col_V_Present_Docket_No", ""),
                            clean_date_str(cap_data.get("Col_W_Present_Docket_raise_Date", "")),
                            str(cap_data.get("Col_X_Aging_Days", "")),
                            cap_data.get("Col_Y_Timeline", "")
                        ]
                    })
                    st.dataframe(rec_table, use_container_width=True, hide_index=True)

            with diag_t3:
                with st.container(border=True):
                    h1, h2, h3 = st.columns(3)
                    h1.metric("Previous Docket No (Col AA)", str(site_row.get('Previous Docket No.', 'None')))
                    h2.metric("Previous Raise Date (Col AB)", clean_date_str(site_row.get('Previous Docket raise Date', 'None')))
                    h3.metric("Last Closure Date (Col R)", clean_date_str(site_row.get('Last Closed date', 'None')))
                    st.markdown("<hr style='margin: 10px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
                    st.markdown(f"**Previous Resolution Remarks (Col Z):**")
                    st.info(site_row.get('Previous Remarks', 'No previous historical remarks recorded.'))
