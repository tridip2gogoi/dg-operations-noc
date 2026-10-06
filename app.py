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
    .custom-header-banner { background-color: #0f172a !important; border: 2px solid #facc15 !important; border-radius: 8px !important; padding: 14px 20px !important; margin-top: 6px !important; margin-bottom: 8px !important; }
    .yellow-success-msg { background-color: #1e293b; color: #facc15 !important; border: 1px solid #facc15; padding: 10px 15px; border-radius: 6px; font-weight: 800; margin-top: 10px; margin-bottom: 10px; }
    .status-badge { padding: 4px 10px; border-radius: 9999px; font-weight: 800; font-size: 12px; text-transform: uppercase; display: inline-block; }
    .badge-ok { background-color: #0284c7; color: #ffffff; }
    .badge-crit { background-color: #dc2626; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PpvvP217epyaIYojWTe79UQCYZDCuCHf/export?format=xlsx"
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

@st.cache_data(ttl=60)
def load_google_sheet_tracker():
    df_status = pd.DataFrame()
    try:
        xls_dg = pd.ExcelFile(GOOGLE_SHEET_URL)
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
            df_status = df_status[~df_status['SAIP ID'].str.lower().isin(['', 'nan', 'none', 'total', '0', 'null'])]
        if 'DG Make' in df_status.columns:
            df_status = df_status[df_status['DG Make'].notna()]
            df_status['DG Make'] = df_status['DG Make'].astype(str).str.strip()
        if 'JC' in df_status.columns: df_status['JC'] = df_status['JC'].astype(str).str.strip()
        if 'State' in df_status.columns: df_status['State'] = df_status['State'].astype(str).str.strip()
        if 'Bucket' in df_status.columns:
            df_status['Bucket'] = df_status['Bucket'].astype(str).str.strip()
            df_status['Bucket'] = df_status['Bucket'].apply(lambda x: None if str(x).lower() in ['nan', 'none', '', 'nat'] else x)
    except Exception:
        if os.path.exists(DEFAULT_EXCEL):
            try: df_status = pd.read_excel(DEFAULT_EXCEL, sheet_name="Automation Status")
            except: pass
    return df_status

def load_ila_tracker():
    df_ila = pd.DataFrame()
    if DEFAULT_ILA and os.path.exists(DEFAULT_ILA):
        try:
            xls_ila = pd.ExcelFile(DEFAULT_ILA)
            ila_sheet = "IPMS Site Automation Status" if "IPMS Site Automation Status" in xls_ila.sheet_names else xls_ila.sheet_names[0]
            df_ila = pd.read_excel(xls_ila, sheet_name=ila_sheet)
        except: pass
    return df_ila

def save_master_to_disk():
    try:
        if "master_tracker_df" in st.session_state and not st.session_state.master_tracker_df.empty:
            with pd.ExcelWriter(DEFAULT_EXCEL, engine='openpyxl') as writer:
                st.session_state.master_tracker_df.to_excel(writer, sheet_name="Automation Status", index=False)
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

user_data = st.session_state.user_info
admin_name = user_data["name"]
admin_role = user_data["role"]
is_viewer = ("read_only" in user_data.get("access", ["all"]))

if "master_tracker_df" not in st.session_state or st.session_state.master_tracker_df.empty:
    st.session_state.master_tracker_df = load_google_sheet_tracker()
if "ila_tracker_df" not in st.session_state or st.session_state.ila_tracker_df.empty:
    st.session_state.ila_tracker_df = load_ila_tracker()

df_status = st.session_state.master_tracker_df
df_ila = st.session_state.ila_tracker_df

with st.container(border=True):
    top_c1, top_c2, top_c3 = st.columns([2, 1.2, 1.2])
    with top_c1: st.markdown(f"🛡️ **Operator:** `{admin_name}` | ☁️ **Source:** `Google Drive Live`")
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
        k3.metric("Manual Mode", man)
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
    
    if not df_status.empty and 'JC' in df_status.columns:
        jcs = ["All JCs"] + sorted([str(x) for x in df_status['JC'].dropna().unique() if str(x).strip().lower() not in ['', 'nan', 'none']])
        sel_jc = st.selectbox("Select JC Circle:", jcs)
        f_st = df_status if sel_jc == "All JCs" else df_status[df_status['JC'].astype(str).str.strip() == sel_jc]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container(border=True):
                st.markdown(f"<h4 style='color: #0f172a;'>Status Summary ({sel_jc})</h4>", unsafe_allow_html=True)
                if 'DG Automation Status' in f_st.columns:
                    st.dataframe(f_st['DG Automation Status'].value_counts().reset_index(), use_container_width=True, hide_index=True)
        with col2:
            with st.container(border=True):
                st.markdown(f"<h4 style='color: #0f172a;'>Bucket Distribution ({sel_jc})</h4>", unsafe_allow_html=True)
                if 'Bucket' in f_st.columns:
                    b_df = f_st[f_st['Bucket'].notna() & (f_st['Bucket'].astype(str).str.strip() != '')]
                    if not b_df.empty:
                        fig_b = px.bar(b_df['Bucket'].value_counts().reset_index(), x='Bucket', y='count', color='count', color_continuous_scale="Blues")
                        fig_b.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
                        st.plotly_chart(fig_b, use_container_width=True)

        st.markdown("---")
        t1, t2, t3, t4, t5 = st.tabs([
            "📊 JC-Wise Automation Status Matrix",
            "🗂️ JC-Wise Problem Bucket Matrix",
            "⚡ GCU Sites: JC vs DG Make & KVA",
            "🛠️ DG Breakdown & Manual",
            "📋 JC-Wise Bucket Summary"
        ])
        
        with t1:
            with st.container(border=True):
                st.markdown("<h4 style='color: #0f172a;'>JC vs DG Automation Status Cross-Tabulation</h4>", unsafe_allow_html=True)
                if 'JC' in df_status.columns and 'DG Automation Status' in df_status.columns:
                    st.dataframe(pd.crosstab(df_status['JC'], df_status['DG Automation Status'], margins=True, margins_name="Total"), use_container_width=True)
        with t2:
            with st.container(border=True):
                st.markdown("<h4 style='color: #0f172a;'>JC vs Root-Cause Bucket Cross-Tabulation</h4>", unsafe_allow_html=True)
                if 'JC' in df_status.columns and 'Bucket' in df_status.columns:
                    clean_bkt = df_status[df_status['DG Automation Status'].astype(str).str.strip().str.lower() != 'automation ok']
                    st.dataframe(pd.crosstab(clean_bkt['JC'], clean_bkt['Bucket'], margins=True, margins_name="Total"), use_container_width=True)
        with t3:
            with st.container(border=True):
                st.markdown("<h4 style='color: #0f172a;'>GCU Sites: JC vs DG Make & KVA Breakdown</h4>", unsafe_allow_html=True)
                if 'Bucket' in df_status.columns:
                    df_gcu = df_status[df_status['Bucket'].astype(str).str.strip().str.upper() == 'GCU']
                    if not df_gcu.empty and 'DG Make' in df_gcu.columns and 'DG Rating' in df_gcu.columns:
                        st.dataframe(pd.crosstab([df_gcu['JC'], df_gcu['DG Make']], df_gcu['DG Rating'], margins=True, margins_name="Total"), use_container_width=True)
        with t4:
            with st.container(border=True):
                st.markdown("<h4 style='color: #0f172a;'>DG Breakdown & Manual Records</h4>", unsafe_allow_html=True)
                st.dataframe(f_st[f_st['DG Automation Status'].astype(str).str.strip().str.lower() != 'automation ok'], use_container_width=True)
        with t5:
            with st.container(border=True):
                st.markdown("<h4 style='color: #0f172a;'>JC-Wise Bucket Summary</h4>", unsafe_allow_html=True)
                st.dataframe(f_st, use_container_width=True)

elif page == "⛽ Fuel Sensor Telemetry":
    st.markdown("## ⛽ Fuel Sensor Fault Telemetry")
    if not df_status.empty and 'Bucket' in df_status.columns:
        f_df = df_status[(df_status['Bucket'].astype(str).str.strip().str.upper() == 'FUEL SENSOR') | (df_status['Fuel Sensor Status'].astype(str).str.strip().str.upper() == 'FUEL SENSOR FAULTY')]
        st.dataframe(f_df, use_container_width=True)

elif page == "⏳ Daily Fault Summary":
    st.markdown("## ⏳ Daily Fault Summary & JC-Wise Breakdown")
    if not df_status.empty: st.dataframe(df_status, use_container_width=True)

elif page == "📈 ILA-AG1 Operations Tracker":
    st.markdown("## 📈 ILA-AG1 Operations Tracker & Telemetry")
    if not df_ila.empty: st.dataframe(df_ila, use_container_width=True)
    else: st.info("ILA Tracker not loaded.")

elif page == "✏️ In-Portal Master Tracker Editor":
    st.markdown("## ✏️ In-Portal Master Tracker Live Editor")
    edited_grid = st.data_editor(df_status, use_container_width=True, height=500, disabled=is_viewer)
    if not is_viewer and st.button("Save Grid Changes", type="primary"):
        st.session_state.master_tracker_df = edited_grid
        save_master_to_disk()
        st.success("Saved successfully!")
        st.rerun()

elif page == "🔍 AI Site Diagnostics":
    st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
    sq = st.text_input("Search Network Site (SAIP ID):", placeholder="Enter SAIP ID (e.g. 9011)...").strip().upper()
    if sq and not df_status.empty and 'SAIP ID' in df_status.columns:
        m = df_status[df_status['SAIP ID'].astype(str).str.contains(sq, case=False, na=False)]
        if not m.empty:
            r = m.iloc[0]
            st.markdown(f"### Site ID: {r.get('SAIP ID')} | Status: {r.get('DG Automation Status')}")
            diag_t1, diag_t2 = st.tabs(["Technical Specs", "Resolution History & FSR Google Drive Link"])
            with diag_t2:
                st.markdown(f"**Previous Remarks (Col Z):** {r.get('Previous Remarks', 'None')}")
                pdf_link = str(r.get('Col AC (FSR PDF link)', '')).strip()
                if pdf_link and pdf_link.lower() not in ['', 'nan', 'none', '0', '0.0']:
                    st.markdown(f"""
                    <div style="background: rgba(30,41,59,0.9); border: 1px solid #38bdf8; padding: 14px; border-radius: 8px;">
                        <b style="color: #38bdf8;">Col AC (FSR PDF Link / Google Drive):</b><br>
                        <span style="color: #ffffff; word-break: break-all;">{pdf_link}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if pdf_link.startswith(('http://', 'https://', 'www.')):
                        t_url = pdf_link if pdf_link.startswith('http') else f"https://{pdf_link}"
                        st.link_button("Open FSR PDF / Google Drive Link", t_url, use_container_width=True)
        else: st.error("Site not found.")
