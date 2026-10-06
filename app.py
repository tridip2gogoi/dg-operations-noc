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
    div[data-testid="stRadio"] div[role="radiogroup"] label {
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
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8) !important;
    }

    .stMarkdown p, .stMarkdown span, .stCaption {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] * { color: #ffffff !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] * { color: #fde047 !important; font-weight: 600 !important; }

    .auto-docket-box {
        background-color: rgba(239, 246, 255, 0.98);
        border: 1px solid #93c5fd;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #0f172a !important;
    }
    .auto-docket-box * { color: #0f172a !important; }

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
    }
    .yellow-alert-box * { color: #ffffff !important; }

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

# --- GOOGLE SHEET LIVE EXPORT URL ---
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/export?format=xlsx"
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

@st.cache_data(ttl=60)
def load_google_sheet_tracker():
    df_status = pd.DataFrame()
    try:
        xls_dg = pd.ExcelFile(GOOGLE_SHEET_URL)
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
        if os.path.exists(DEFAULT_EXCEL):
            try:
                df_status = pd.read_excel(DEFAULT_EXCEL, sheet_name="Automation Status")
            except:
                pass
    return df_status

def load_ila_tracker(ila_file=None):
    df_ila = pd.DataFrame()
    target_ila = ila_file
    if not target_ila and DEFAULT_ILA:
        target_ila = DEFAULT_ILA
    if target_ila and is_valid_source(target_ila):
        try:
            xls_ila = pd.ExcelFile(target_ila)
            ila_sheet = "IPMS Site Automation Status" if "IPMS Site Automation Status" in xls_ila.sheet_names else xls_ila.sheet_names[0]
            df_ila = pd.read_excel(xls_ila, sheet_name=ila_sheet)
            for col in df_ila.columns:
                df_ila[col] = df_ila[col].astype(object)
            if 'Sap ID' in df_ila.columns:
                df_ila = df_ila[df_ila['Sap ID'].notna()]
                df_ila['Sap ID'] = df_ila['Sap ID'].astype(str).str.strip()
        except:
            pass
    return df_ila

def load_cm_tracker():
    df_cm = pd.DataFrame()
    if os.path.exists(DEFAULT_CM_TRACKER):
        try:
            xls_cm = pd.ExcelFile(DEFAULT_CM_TRACKER)
            cm_sheet = "Open Site" if "Open Site" in xls_cm.sheet_names else xls_cm.sheet_names[0]
            df_cm = pd.read_excel(xls_cm, sheet_name=cm_sheet)
        except:
            pass
    return df_cm

def save_master_to_disk():
    try:
        target_file = DEFAULT_EXCEL
        if "master_tracker_df" in st.session_state and not st.session_state.master_tracker_df.empty:
            with pd.ExcelWriter(target_file, engine='openpyxl') as writer:
                st.session_state.master_tracker_df.to_excel(writer, sheet_name="Automation Status", index=False)
                if "ila_tracker_df" in st.session_state and not st.session_state.ila_tracker_df.empty:
                    st.session_state.ila_tracker_df.to_excel(writer, sheet_name="IPMS Site Automation Status", index=False)
    except:
        pass

def ai_capture_o_to_ab(site_id, df_open_cm, df_status):
    clean_id = str(site_id).strip().upper() if site_id else ""
    res = {
        "JC": "", "Col_O_Fuel_Sensor_Status": "Ok", "Col_P_Docket_no": "",
        "Col_Q_Open_Date": "", "Col_S_DG_Automation_Status": "Automation Ok",
        "Col_T_Present_Remarks": "", "Col_U_Bucket": "", "Col_V_Present_Docket_No": "",
        "Col_W_Present_Docket_raise_Date": "", "Col_X_Aging_Days": 0, "Col_Y_Timeline": "",
        "Col_Z_Previous_Remarks": "", "Col_AA_Previous_Docket_No": "", "Col_AB_Previous_Docket_raise_Date": "",
        "Col_AC_FSR_PDF_Link": "", "source": "None"
    }
    if not clean_id: return res
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
    if df_target.empty or not site_id: return df_target
    updated = df_target.copy()
    for col in updated.columns: updated[col] = updated[col].astype(object)
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
        target_closed_col = 'Last Closed date'
        for col in updated.columns:
            if 'last closed' in str(col).lower():
                target_closed_col = col
                break
        updated.at[i, target_closed_col] = str(today_date_str)
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

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- AUTHENTICATED WORKSPACE ---
user_data = st.session_state.user_info
admin_name = user_data["name"]
admin_role = user_data["role"]
user_perms = user_data.get("access", ["all"])
is_viewer = ("read_only" in user_perms)

# --- TOP CONTROL BAR FOR REFRESH & LIVE SYNC ---
with st.container(border=True):
    top_c1, top_c2, top_c3 = st.columns([2, 1.2, 1])
    with top_c1:
        st.markdown(f"🛡️ **Operator:** `{admin_name}` | **Role:** `{admin_role}` | ☁️ **Source:** `Google Drive Live`")
    with top_c2:
        st.markdown(f"🕒 **IST:** `{datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p')}`")
    with top_c3:
        if st.button("🔄 Force Refresh & Sync", type="primary", use_container_width=True):
            st.cache_data.clear()
            if "master_tracker_df" in st.session_state:
                del st.session_state.master_tracker_df
            st.success("Synced successfully!")
            st.rerun()

if "master_tracker_df" not in st.session_state or st.session_state.master_tracker_df.empty:
    st.session_state.master_tracker_df = load_google_sheet_tracker()
if "ila_tracker_df" not in st.session_state or st.session_state.ila_tracker_df.empty:
    st.session_state.ila_tracker_df = load_ila_tracker()
if "open_cm_df" not in st.session_state:
    st.session_state.open_cm_df = load_cm_tracker()

df_status = st.session_state.master_tracker_df
df_ila = st.session_state.ila_tracker_df
df_open_cm = st.session_state.open_cm_df

# --- TOP HORIZONTAL NAVIGATION MENU ---
page = st.radio(
    "Select Operation View:", 
    [
        "📊 Executive Control Center",
        "⚙️ Fleet Analytics & Problem Buckets",
        "⛽ Fuel Sensor Telemetry",
        "⏳ Daily Fault Summary",
        "📈 ILA-AG1 Operations Tracker",
        "✏️ In-Portal Master Tracker Editor",
        "🔍 AI Site Diagnostics"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. EXECUTIVE CONTROL CENTER
# ---------------------------------------------------------
if page == "📊 Executive Control Center":
    st.markdown("## ⚡ North East Circle - DG Operations Control Center")
    if not df_status.empty:
        total_sites = len(df_status)
        auto_ok = len(df_status[df_status['DG Automation Status'].astype(str).str.strip() == 'Automation Ok']) if 'DG Automation Status' in df_status.columns else 0
        manual_mode = len(df_status[df_status['DG Automation Status'].astype(str).str.strip() == 'Manual Mode']) if 'DG Automation Status' in df_status.columns else 0
        dg_breakdown_count = len(df_status[df_status['DG Automation Status'].astype(str).str.strip().str.lower() == 'dg breakdown']) if 'DG Automation Status' in df_status.columns else 0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Sites", f"{total_sites:,}")
        k2.metric("Automation Rate", f"{round((auto_ok/total_sites)*100, 1)}%" if total_sites else "0%")
        k3.metric("Manual Mode", manual_mode)
        k4.metric("DG Breakdown", dg_breakdown_count)

        st.markdown("---")
        if 'State' in df_status.columns:
            state_options = ["All States"] + sorted([str(x) for x in df_status['State'].dropna().unique() if str(x).strip().lower() not in ['', 'nan', 'none']])
            selected_state = st.selectbox("🌐 Filter Circle by State:", state_options)
            state_filtered_df = df_status if selected_state == "All States" else df_status[df_status['State'].astype(str).str.strip() == selected_state]
            st.dataframe(state_filtered_df, use_container_width=True)

# ---------------------------------------------------------
# 2. FLEET ANALYTICS & PROBLEM BUCKETS
# ---------------------------------------------------------
elif page == "⚙️ Fleet Analytics & Problem Buckets":
    st.markdown("## ⚙️ Fleet Automation Classification & Root-Cause Analysis")
    if not df_status.empty:
        if 'JC' in df_status.columns:
            jcs = ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique() if str(x).strip().lower() not in ['', 'nan', 'none']])
            sel_jc = st.selectbox("Select JC Circle:", jcs)
            f_st = df_status if sel_jc == "All JCs" else df_status[df_status['JC'].astype(str).str.strip() == sel_jc]
            st.dataframe(f_st, use_container_width=True)

# ---------------------------------------------------------
# 3. FUEL SENSOR TELEMETRY
# ---------------------------------------------------------
elif page == "⛽ Fuel Sensor Telemetry":
    st.markdown("## ⛽ Fuel Sensor Fault Telemetry")
    if not df_status.empty and 'Bucket' in df_status.columns:
        f_df = df_status[(df_status['Bucket'].astype(str).str.strip().str.upper() == 'FUEL SENSOR') | (df_status['Fuel Sensor Status'].astype(str).str.strip().str.upper() == 'FUEL SENSOR FAULTY')]
        st.dataframe(f_df, use_container_width=True)

# ---------------------------------------------------------
# 4. DAILY FAULT SUMMARY
# ---------------------------------------------------------
elif page == "⏳ Daily Fault Summary":
    st.markdown("## ⏳ Daily Fault Summary & JC-Wise Breakdown")
    if not df_status.empty:
        st.dataframe(df_status, use_container_width=True)

# ---------------------------------------------------------
# 5. ILA-AG1 OPERATIONS TRACKER
# ---------------------------------------------------------
elif page == "📈 ILA-AG1 Operations Tracker":
    st.markdown("## 📈 ILA-AG1 Operations Tracker & Telemetry")
    if not df_ila.empty:
        st.dataframe(df_ila, use_container_width=True)
    else:
        st.info("ILA Tracker not loaded.")

# ---------------------------------------------------------
# 6. IN-PORTAL MASTER TRACKER EDITOR
# ---------------------------------------------------------
elif page == "✏️ In-Portal Master Tracker Editor":
    st.markdown("## ✏️ In-Portal Master Tracker Live Editor")
    if not df_status.empty:
        st.dataframe(df_status, use_container_width=True)

# ---------------------------------------------------------
# 7. AI SITE DIAGNOSTICS & FSR GOOGLE DRIVE LINK VIEWER
# ---------------------------------------------------------
elif page == "🔍 AI Site Diagnostics":
    st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
    sq = st.text_input("Search Network Site (SAIP ID):", placeholder="Enter SAIP ID (e.g. 9011)...").strip().upper()
    
    if sq and not df_status.empty and 'SAIP ID' in df_status.columns:
        matches = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)]
        if matches.empty:
            st.error(f"❌ No network records found matching `{sq}`.")
        else:
            site_row = matches.iloc[0]
            selected_site = site_row['SAIP ID']
            status_val = str(site_row.get('DG Automation Status', 'Automation Ok'))
            
            st.markdown(f"""
            <div class="custom-header-banner">
                <h2>⚡ <span style="color: #facc15;">{selected_site}</span></h2>
                <p>JC Circle: <b>{site_row.get('JC', 'N/A')}</b> | State: <b>{site_row.get('State', 'N/A')}</b> | Status: <b>{status_val}</b></p>
            </div>
            """, unsafe_allow_html=True)

            diag_t1, diag_t2 = st.tabs(["📋 Technical & Telemetry", "⏳ Resolution History & FSR Google Drive Link"])

            with diag_t1:
                with st.container(border=True):
                    st.markdown(f"**DG Make:** `{site_row.get('DG Make', 'N/A')}`")
                    st.markdown(f"**DG Rating:** `{site_row.get('DG Rating', 'N/A')}`")
                    st.markdown(f"**Problem Bucket:** `{site_row.get('Bucket', 'None')}`")
                    st.markdown(f"**Present Remarks:** `{site_row.get('Present Remarks', 'None')}`")

            with diag_t2:
                with st.container(border=True):
                    st.markdown(f"**Previous Docket No (Col AA):** `{site_row.get('Previous Docket No.', 'None')}`")
                    st.markdown(f"**Previous Remarks (Col Z):**")
                    st.markdown(f'<div class="previous-remarks-box">{site_row.get("Previous Remarks", "No previous remarks.")}</div>', unsafe_allow_html=True)
                    
                    # --- GOOGLE DRIVE FSR PDF LINK VIEWER ---
                    pdf_link_val = str(site_row.get('Col AC (FSR PDF link)', '')).strip()
                    if pdf_link_val and pdf_link_val.lower() not in ['', 'nan', 'none', '0', '0.0']:
                        st.markdown(f"""
                        <div style="margin-top: 12px; background-color: rgba(30, 41, 59, 0.9); border: 1px solid #38bdf8; padding: 14px; border-radius: 8px;">
                            <b style="color: #38bdf8; font-size: 15px;">📄 Col AC (FSR PDF Link / Google Drive):</b><br>
                            <span style="color: #ffffff; font-size: 14px; word-break: break-all;">{pdf_link_val}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if pdf_link_val.startswith(('http://', 'https://', 'www.')):
                            target_url = pdf_link_val if pdf_link_val.startswith('http') else f"https://{pdf_link_val}"
                            st.link_button("🌐 Open FSR PDF / Google Drive Link", target_url, use_container_width=True)
                        else:
                            st.info(f"Col AC Record: {pdf_link_val}")
                    else:
                        st.info("No FSR PDF or Google Drive link attached in Col AC for this site.")
