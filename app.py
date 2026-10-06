import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timezone, timedelta
import os
import hashlib
from io import BytesIO

# --- TIMEZONE CONFIGURATION FOR IST (UTC+5:30) ---
IST = timezone(timedelta(hours=5, minutes=30))
current_ist_time = datetime.now(IST)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NE Circle Telecom DG Ops Center | Enterprise NOC",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# Custom Corporate Professional NOC Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}

    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.90)), 
                    url("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0.5rem !important;
    }

    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary {
        color: #facc15 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] div[role="radiogroup"] label,
    div[data-testid="stRadio"] div[role="radiogroup"] label div p,
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #facc15 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: rgba(30, 41, 59, 0.85);
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid rgba(250, 204, 21, 0.4);
        margin-right: 6px;
    }

    div[data-testid="stTabs"] button p, div[data-testid="stTabs"] button span {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 14px !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p, 
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #ffffff !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: rgba(202, 138, 4, 0.85) !important;
        border-radius: 6px 6px 0 0;
    }

    label, [data-testid="stWidgetLabel"] p, [data-testid="stForm"] label p {
        color: #facc15 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
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
        color: #fde047 !important;
        font-weight: 600 !important;
    }

    .auto-docket-box {
        background-color: rgba(239, 246, 255, 0.98);
        border: 1px solid #93c5fd;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #0f172a !important;
    }
    .auto-docket-box * {
        color: #0f172a !important;
    }

    .previous-remarks-box {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid #facc15 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    .custom-header-banner {
        background-color: #0f172a !important;
        border: 2px solid #facc15 !important;
        border-radius: 8px !important;
        padding: 14px 20px !important;
        margin-top: 6px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 6px 15px -5px rgba(250, 204, 21, 0.3) !important;
    }

    .yellow-alert-box {
        background: linear-gradient(135deg, #f59e0b, #d97706) !important;
        color: #ffffff !important;
        border: 1px solid #fef3c7 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }
    .yellow-alert-box * {
        color: #ffffff !important;
    }

    .yellow-success-msg {
        background-color: #1e293b;
        color: #facc15 !important;
        border: 1px solid #facc15;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .status-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .badge-ok { background-color: #0284c7 !important; color: #ffffff !important; border: 1px solid #38bdf8; }
    .badge-warn { background-color: #ca8a04 !important; color: #ffffff !important; border: 1px solid #facc15; }
    .badge-crit { background-color: #dc2626 !important; color: #ffffff !important; border: 1px solid #f87171; }
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

USER_CREDENTIALS = {
    "tridip2.gogoi": {
        "password_hash": hashlib.sha256("Gogoi@6095".encode()).hexdigest(),
        "role": "Super Admin / Operations Head",
        "name": "Tridip Gogoi (Operations Head)",
        "access": ["all"]
    },
    "ptpl": {
        "password_hash": hashlib.sha256("Rintu@2026".encode()).hexdigest(),
        "role": "NOC Viewer / Executive",
        "name": "PTPL Operations Desk",
        "access": ["read_only"]
    },
    "sukanta.biswas": {
        "password_hash": hashlib.sha256("Biswas@2027".encode()).hexdigest(),
        "role": "NOC Viewer / Executive",
        "name": "Sukanta Biswas",
        "access": ["read_only"]
    },
    "state": {
        "password_hash": hashlib.sha256("NIPL@2026".encode()).hexdigest(),
        "role": "NOC Viewer / Executive",
        "name": "State Operations Desk",
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

def load_all_trackers(dg_file, cm_file, ila_file=None):
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
            
            for col in df_status.columns:
                df_status[col] = df_status[col].astype(object)
            
            ac_col_name = None
            for idx, col in enumerate(df_status.columns):
                c_str = str(col).strip().upper()
                if 'AC' in c_str or 'PDF' in c_str or idx == 28:
                    ac_col_name = col
                    break
            
            if ac_col_name:
                df_status['Col AC (FSR PDF link)'] = df_status[ac_col_name].apply(lambda x: "" if pd.isna(x) else str(x).strip())
            else:
                if 'Col AC (FSR PDF link)' not in df_status.columns:
                    df_status['Col AC (FSR PDF link)'] = ""

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
            if 'State' in df_status.columns:
                df_status['State'] = df_status['State'].astype(str).str.strip()
            if 'Bucket' in df_status.columns:
                df_status['Bucket'] = df_status['Bucket'].astype(str).str.strip()
                df_status['Bucket'] = df_status['Bucket'].apply(lambda x: None if str(x).lower() in ['nan', 'none', '', 'nat'] else x)
            if 'DG Automation Status' in df_status.columns:
                df_status['DG Automation Status'] = df_status['DG Automation Status'].astype(str).str.strip()
            
            for d_col in ['Open Date', 'Present Docket raise Date', 'Previous Docket raise Date', 'Last Closed date', 'Last Closed date.1']:
                if d_col in df_status.columns:
                    df_status[d_col] = df_status[d_col].apply(clean_date_str).astype(str)
            
            aging_col_target = None
            for col in df_status.columns:
                if 'aging' in col.lower() or 'ageing' in col.lower():
                    aging_col_target = col
                    break
            
            if aging_col_target:
                df_status['Aging_Num'] = pd.to_numeric(df_status[aging_col_target], errors='coerce').fillna(0)
            else:
                df_status['Aging_Num'] = 0
        except Exception as e:
            pass

    if is_valid_source(cm_file):
        try:
            xls_cm = pd.ExcelFile(cm_file)
            target_cm_sheet = "Open Site" if "Open Site" in xls_cm.sheet_names else xls_cm.sheet_names[0]
            df_open_cm = pd.read_excel(xls_cm, sheet_name=target_cm_sheet)
        except Exception as e:
            pass

    if ila_file and is_valid_source(ila_file):
        try:
            xls_ila = pd.ExcelFile(ila_file)
            ila_sheet_target = "IPMS Site Automation Status" if "IPMS Site Automation Status" in xls_ila.sheet_names else xls_ila.sheet_names[0]
            df_ila = pd.read_excel(xls_ila, sheet_name=ila_sheet_target)
            for col in df_ila.columns:
                df_ila[col] = df_ila[col].astype(object)
            if 'Sap ID' in df_ila.columns:
                df_ila = df_ila[df_ila['Sap ID'].notna()]
                df_ila['Sap ID'] = df_ila['Sap ID'].astype(str).str.strip()
        except Exception as e:
            pass

    return df_status, df_fuel, df_open_cm, df_ila, df_cr_data

def save_master_to_disk():
    try:
        target_file = DEFAULT_EXCEL
        if not os.path.exists(target_file):
            local_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
            if local_files:
                target_file = local_files[0]
        
        if "master_tracker_df" in st.session_state and not st.session_state.master_tracker_df.empty:
            with pd.ExcelWriter(target_file, engine='openpyxl') as writer:
                st.session_state.master_tracker_df.to_excel(writer, sheet_name="Automation Status", index=False)
                if "fuel_tracker_df" in st.session_state and not st.session_state.fuel_tracker_df.empty:
                    st.session_state.fuel_tracker_df.to_excel(writer, sheet_name="Fuel Sensor faulty", index=False)
                if "ila_tracker_df" in st.session_state and not st.session_state.ila_tracker_df.empty:
                    st.session_state.ila_tracker_df.to_excel(writer, sheet_name="IPMS Site Automation Status", index=False)
    except Exception as ex:
        pass

def ai_capture_o_to_ab(site_id, df_open_cm, df_status, df_cr_data=None):
    clean_id = str(site_id).strip().upper() if site_id else ""
    res = {
        "JC": "", "Col_O_Fuel_Sensor_Status": "Ok", "Col_P_Docket_no": "",
        "Col_Q_Open_Date": "", "Col_S_DG_Automation_Status": "Automation Ok",
        "Col_T_Present_Remarks": "", "Col_U_Bucket": "", "Col_V_Present_Docket_No": "",
        "Col_W_Present_Docket_raise_Date": "", "Col_X_Aging_Days": 0, "Col_Y_Timeline": "",
        "Col_Z_Previous_Remarks": "", "Col_AA_Previous_Docket_No": "", "Col_AB_Previous_Docket_raise_Date": "",
        "Col_AC_FSR_PDF_Link": "", "source": "None"
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
            res["Col_AC_FSR_PDF_Link"] = str(prev_row.get("Col AC (FSR PDF link)", prev_row.get("FSR PDF Link", ""))).strip()
            res["source"] = "DG Master Tracker"

    for k, v in res.items():
        if str(v).lower() == 'nan' or str(v) == 'nat':
            res[k] = ""
    return res

def archive_current_fault_to_previous(row_idx, df_target, custom_fsr_remarks="", fsr_pdf_name=""):
    r = df_target.loc[row_idx]
    pres_doc = str(r.get('Present Docket No.', '')).strip()
    pres_date = str(r.get('Present Docket raise Date', '')).strip()
    pres_rem = str(r.get('Present Remarks', '')).strip()
    
    final_remarks = custom_fsr_remarks.strip() if custom_fsr_remarks.strip() else pres_rem
    if fsr_pdf_name:
        final_remarks += f" [FSR PDF: {fsr_pdf_name}]"
        df_target.at[row_idx, 'Col AC (FSR PDF link)'] = f"Uploaded: {fsr_pdf_name}"

    if pres_doc and pres_doc.lower() not in ['', 'nan', 'none']:
        df_target.at[row_idx, 'Previous Docket No.'] = str(pres_doc)
        df_target.at[row_idx, 'Previous Docket raise Date'] = str(pres_date)
        df_target.at[row_idx, 'Previous Remarks'] = str(final_remarks)
    elif final_remarks and final_remarks.lower() not in ['', 'nan', 'none']:
        df_target.at[row_idx, 'Previous Remarks'] = str(final_remarks)
    return df_target

def clear_site_active_fault_data(site_id, df_target, custom_fsr_remarks="", fsr_pdf_name=""):
    if df_target.empty or not site_id:
        return df_target
    updated = df_target.copy()
    for col in updated.columns:
        updated[col] = updated[col].astype(object)
    
    clean_id = str(site_id).strip().upper()
    match_idx = updated[updated["SAIP ID"].astype(str).str.strip().str.upper() == clean_id].index
    if not match_idx.empty:
        i = match_idx[0]
        updated = archive_current_fault_to_previous(i, updated, custom_fsr_remarks, fsr_pdf_name)
        if "DG Automation Status" in updated.columns: updated.at[i, "DG Automation Status"] = "Automation Ok"
        if "Present Remarks" in updated.columns: updated.at[i, "Present Remarks"] = ""
        if "Bucket" in updated.columns: updated.at[i, "Bucket"] = None
        if "Present Docket No." in updated.columns: updated.at[i, "Present Docket No."] = ""
        if "Present Docket raise Date" in updated.columns: updated.at[i, "Present Docket raise Date"] = ""
        if "Aging (Day's)" in updated.columns: updated.at[i, "Aging (Day's)"] = 0
        if "Aging_Num" in updated.columns: updated.at[i, "Aging_Num"] = 0
        
        today_date_str = datetime.now(IST).strftime('%Y-%m-%d')
        target_closed_col = None
        for col in updated.columns:
            if 'last closed' in str(col).lower():
                target_closed_col = col
                break
        if target_closed_col:
            updated.at[i, target_closed_col] = str(today_date_str)
        else:
            updated.at[i, 'Last Closed date'] = str(today_date_str)

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
                <h2 style="color: #0f172a; font-weight:
