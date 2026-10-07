import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timezone, timedelta
import os
import hashlib
from io import BytesIO
import re
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1uwOZ9HRC833CfC-hO8Aj1davBQ8qDyXa2f7L0-uu7QQ/export?format=xlsx"
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1uwOZ9HRC833CfC-hO8Aj1davBQ8qDyXa2f7L0-uu7QQ/gviz/tq?tqx=out:csv"

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
    h1, h2, h3, h4, h5, h6 { color: #facc15 !important; font-weight: 800 !important; }
    .previous-remarks-box { background-color: rgba(15, 23, 42, 0.85) !important; border: 1px solid #facc15 !important; border-radius: 8px !important; padding: 10px 14px !important; color: #ffffff !important; font-size: 14px !important; font-weight: 600 !important; }
    .custom-header-banner { background-color: #0f172a !important; border: 2px solid #facc15 !important; border-radius: 8px !important; padding: 14px 20px !important; margin-top: 6px !important; margin-bottom: 8px !important; }
    .yellow-success-msg { background-color: #1e293b; color: #facc15 !important; border: 1px solid #facc15; padding: 10px 15px; border-radius: 6px; font-weight: 800; margin-top: 10px; margin-bottom: 10px; }
    .status-badge { padding: 4px 10px; border-radius: 9999px; font-weight: 800; font-size: 12px; text-transform: uppercase; display: inline-block; }
    .badge-ok { background-color: #10b981; color: #ffffff; }
    .badge-warn { background-color: #f59e0b; color: #ffffff; }
    .badge-crit { background-color: #dc2626; color: #ffffff; }

    div[data-testid="stTabs"] button p { color: #facc15 !important; font-weight: 800 !important; font-size: 14px !important; }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] { background-color: #facc15 !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] p { color: #ffffff !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom-color: #facc15 !important; }
    div[data-testid="stTabs"] button:hover p { color: #fef08a !important; }

    .stApp p, .stApp span, .stApp div, .stApp label, .stMarkdownContainer p, .element-container p { color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, .stMarkdownContainer h1, .stMarkdownContainer h2, .stMarkdownContainer h3, .stMarkdownContainer h4 { color: #facc15 !important; }
</style>
""", unsafe_allow_html=True)

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/export?format=xlsx"
GOOGLE_SHEET_PUB = "https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/pub?output=xlsx"
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/gviz/tq?tqx=out:csv"
DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio.xlsx"

DEFAULT_ILA = None
if os.path.exists('.'):
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

def extract_link(val):
    if pd.isna(val) or val is None: return ""
    s = str(val).strip()
    if s.lower() in ['', 'nan', 'none', '0', '0.0', 'nat', 'null'] or '00:00:00' in s: return ""
    if 'HYPERLINK' in s.upper():
        m = re.search(r'HYPERLINK\s*\(\s*["']([^"']+)["']', s, re.I)
        if m:
            url = m.group(1).strip()
            return url if url.startswith('http') else f"https://{url}"
        url_match = re.search(r'(https?://[^\s",']+)', s)
        if url_match: return url_match.group(1).strip()
    if 'http://' in s or 'https://' in s:
        for part in s.split():
            if part.startswith('http://') or part.startswith('https://'):
                return part.strip('\'"')
    if 'drive.google.com' in s:
        dm = re.search(r'(drive\.google\.com[^\s",']+)', s)
        if dm:
            d_url = dm.group(1).strip()
            return "https://" + d_url if not d_url.startswith('http') else d_url
    digits = s.replace('.0', '').replace('-', '').replace(' ', '')
    if digits.isdigit() and len(digits) == 10 and digits[0] in ['6', '7', '8', '9']:
        return ""
    return s

@st.cache_data(ttl=5)
def load_google_sheet_tracker():
    if 'persistent_master_df' in st.session_state and st.session_state.persistent_master_df is not None and not st.session_state.persistent_master_df.empty:
        st.session_state['data_source_mode'] = "Uploaded Excel File"
        return st.session_state.persistent_master_df

    df_status = pd.DataFrame()
    source_status = "Google Sheet Live"
    err_msg = ""
    success = False

    skip_live = st.session_state.get('sidebar_master_upload', None) is not None or os.environ.get('SKIP_GSHEET', 'false') == 'true'
    
    if not skip_live:
        try:
            csv_url = f"https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/gviz/tq?tqx=out:csv&cb={datetime.now().timestamp()}"
            df_status = pd.read_csv(csv_url)
            if df_status is not None and not df_status.empty:
                success = True
        except Exception as e1:
            err_msg = f"CSV Live Error: {str(e1)}"

        if not success:
            try:
                xls_dg = pd.ExcelFile("https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/pub?output=xlsx")
                sheet_target = "Automation Status" if "Automation Status" in xls_dg.sheet_names else xls_dg.sheet_names[0]
                df_status = pd.read_excel(xls_dg, sheet_name=sheet_target)
                if df_status is not None and not df_status.empty:
                    success = True
            except Exception as e2:
                err_msg += f" | Pub Error: {str(e2)}"

    if not success:
        source_status = "Local File (Backup)"
        if os.path.exists(DEFAULT_EXCEL):
            try:
                xls_local = pd.ExcelFile(DEFAULT_EXCEL)
                s_name = "Automation Status" if "Automation Status" in xls_local.sheet_names else xls_local.sheet_names[0]
                df_status = pd.read_excel(xls_local, sheet_name=s_name)
                if df_status is not None and not df_status.empty:
                    success = True
            except Exception as e3:
                err_msg += f" | Local Error: {str(e3)}"

    if df_status is None or df_status.empty:
        df_status = pd.DataFrame()
    else:
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
                    st.session_state.ila_tracker_df.to_excel(writer, sheet_name="IPMS Site Automation Status", index=False)
    except: pass

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
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True, type="primary"):
                rec = verify_login(u.strip().lower(), p)
                if rec:
                    st.session_state.authenticated = True
                    st.session_state.user_info = rec
                    st.rerun()
                else: st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 📂 Excel / Master Tracker Local Upload Manager in Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Portal Data Manager")
    st.markdown("Upload your Master Tracker (`.xlsx`) to instantly view data and bypass any live sheet sync errors.")
    up_file = st.file_uploader("Upload Master Tracker (.xlsx)", type=["xlsx", "xls"], key="sidebar_master_upload")
    if up_file is not None:
        try:
            df_up = pd.read_excel(up_file, sheet_name=0)
            for col in df_up.columns: df_up[col] = df_up[col].astype(object)
            st.session_state['persistent_master_df'] = df_up
            st.session_state.master_tracker_df = df_up
            st.session_state['data_source_mode'] = "Uploaded Excel File"
            st.success("Master Tracker uploaded successfully!")
            st.rerun()
        except Exception as e_up:
            st.error(f"Upload error: {e_up}")
    
    if 'persistent_master_df' in st.session_state and st.session_state['persistent_master_df'] is not None:
        if st.button("🗑️ Clear Uploaded Excel", use_container_width=True):
            st.session_state['persistent_master_df'] = None
            if "master_tracker_df" in st.session_state: del st.session_state.master_tracker_df
            st.cache_data.clear()
            st.success("Cleared!")
            st.rerun()
    st.markdown("---")

user_data = st.session_state.user_info
admin_name = user_data["name"]
admin_role = user_data["role"]
is_viewer = ("read_only" in user_data.get("access", ["all"]))

if "master_tracker_df" not in st.session_state or st.session_state.master_tracker_df is None or getattr(st.session_state.master_tracker_df, 'empty', True):
    res_df = load_google_sheet_tracker()
    st.session_state.master_tracker_df = res_df if res_df is not None else pd.DataFrame()

if "ila_tracker_df" not in st.session_state or st.session_state.ila_tracker_df is None or getattr(st.session_state.ila_tracker_df, 'empty', True):
    res_ila = load_ila_tracker()
    st.session_state.ila_tracker_df = res_ila if res_ila is not None else pd.DataFrame()

df_status = st.session_state.master_tracker_df
df_ila = st.session_state.ila_tracker_df

with st.container(border=True):
    top_c1, top_c2, top_c3 = st.columns([2, 1.2, 1.2])
    with top_c1: 
        curr_mode = st.session_state.get('data_source_mode', 'Google Sheet Live')
        mode_badge = f"`{curr_mode}`" if "Live" in curr_mode else f"📁 `{curr_mode}`"
        st.markdown(f"🛡️ **Operator:** `{admin_name}` | ☁️ **Source:** {mode_badge}")
    with top_c2:
        if st.button("🔄 Force Refresh & Sync", type="primary", use_container_width=True):
            st.cache_data.clear()
            if "master_tracker_df" in st.session_state: del st.session_state.master_tracker_df
            st.success("Synced!")
            st.rerun()
    with top_c3:
        if not df_status.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_status.to_excel(writer, sheet_name="Automation Status", index=False)
                if not df_ila.empty: df_ila.to_excel(writer, sheet_name="IPMS Site Automation Status", index=False)
            st.download_button(
                label="📥 Download Report (.xlsx)",
                data=output.getvalue(),
                file_name=f"NE_Circle_Master_Operations_Report_{datetime.now(IST).strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

page = st.radio("Select View:", [
    "📊 Executive Control Center",
    "⚙️ Fleet Analytics & Problem Buckets",
    "⛽ Fuel Sensor Telemetry",
    "⏳ Daily Fault Summary",
    "📈 ILA-AG1 Operations Tracker",
    "✏️ In-Portal Master Tracker Editor",
    "🔍 AI Site Diagnostics"
], horizontal=True, label_visibility="collapsed")

st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

if page == "📊 Executive Control Center":
    st.markdown("## ⚡ North East Circle - DG Operations Control Center")
    if not df_status.empty:
        tot = len(df_status)
        ok = len(df_status[df_status['DG Automation Status'].astype(str).str.strip() == 'Automation Ok']) if 'DG Automation Status' in df_status.columns else 0
        man = len(df_status[df_status['DG Automation Status'].astype(str).str.strip() == 'Manual Mode']) if 'DG Automation Status' in df_status.columns else 0
        bd = len(df_status[df_status['DG Automation Status'].astype(str).str.strip().str.lower() == 'dg breakdown']) if 'DG Automation Status' in df_status.columns else 0
        ber = len(df_status[df_status['DG Automation Status'].astype(str).str.strip().str.lower() == 'dg ber']) if 'DG Automation Status' in df_status.columns else 0
        ovr = len(df_status[df_status['DG Automation Status'].astype(str).str.strip().str.lower() == 'dg overload']) if 'DG Automation Status' in df_status.columns else 0

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Total Sites", f"{tot:,}")
        k2.metric("Automation Rate", f"{round((ok/tot)*100, 1)}%" if tot else "0%")
        k3.metric("Manual Mode", manual_mode if 'manual_mode' in locals() else man)
        k4.metric("DG Breakdown", bd)
        k5.metric("DG BER", ber)
        k6.metric("DG Overload", ovr)

        st.markdown("---")
        if 'State' in df_status.columns:
            state_options = ["All States"] + sorted([str(x) for x in df_status['State'].dropna().unique() if str(x).strip().lower() not in ['', 'nan', 'none']])
            selected_state = st.selectbox("🌐 Filter Circle by State:", state_options)
            state_filtered_df = df_status if selected_state == "All States" else df_status[df_status['State'].astype(str).str.strip() == selected_state]
            
            c1, c2 = st.columns([3, 2])
            with c1:
                with st.container(border=True):
                    st.markdown("<h4 style='margin:0 0 10px 0; color: #facc15;'>JC / State Wise Automation Health</h4>", unsafe_allow_html=True)
                    if "JC" in state_filtered_df.columns and "DG Automation Status" in state_filtered_df.columns:
                        fig_bar = px.histogram(state_filtered_df, x="JC", color="DG Automation Status", barmode="group", color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#6366f1"])
                        fig_bar.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
                        st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                with st.container(border=True):
                    st.markdown("<h4 style='margin:0 0 10px 0; color: #facc15;'>DG Make Fleet Allocation</h4>", unsafe_allow_html=True)
                    if "DG Make" in state_filtered_df.columns:
                        valid_makes = state_filtered_df[state_filtered_df['DG Make'].notna() & (state_filtered_df['DG Make'].astype(str).str.strip() != '')]
                        fig_donut = px.pie(valid_makes, names="DG Make", hole=0.58, color_discrete_sequence=px.colors.qualitative.Safe)
                        fig_donut.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
                        st.plotly_chart(fig_donut, use_container_width=True)

elif page == "⚙️ Fleet Analytics & Problem Buckets":
    st.markdown("## ⚙️ Fleet Automation Classification & Root-Cause Analysis")
    st.caption("JC-wise breakdown of network automation health, problem buckets, and docket fulfillment statuses.")
    
    if not df_status.empty:
        jc_options = ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique() if str(x).strip().lower() not in ['', 'nan', 'none']]) if 'JC' in df_status.columns else ["All JCs"]
        selected_fleet_jc = st.selectbox("Select JC Circle:", jc_options)
        
        filtered_status = df_status if selected_fleet_jc == "All JCs" or 'JC' not in df_status.columns else df_status[df_status['JC'].astype(str).str.strip() == selected_fleet_jc]
        
        if 'DG Automation Status' in filtered_status.columns:
            valid_bucket_base = filtered_status[filtered_status['DG Automation Status'].astype(str).str.strip().str.lower
