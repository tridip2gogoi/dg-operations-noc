from datetime import date, datetime, timedelta, timezone
from io import BytesIO
import hashlib
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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

DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"

DEFAULT_ILA = None
if os.path.exists("."):
  for f in os.listdir("."):
    if (
        "ILA" in f.upper()
        and f.endswith((".xlsx", ".xls"))
        and not f.startswith("~$")
    ):
      DEFAULT_ILA = f
      break

BUCKET_LIST = [
    "GCU",
    "Fuel Sensor",
    "DG Breakdown",
    "DG battery",
    "IPMS",
    "OEM Spare parts",
    "New DG Req",
    "AMF Req",
    "Owner issue",
    "Access issue",
    "Theft case",
    "Jio Support",
    "Other Issue",
]
STATUS_CHOICES = [
    "Automation Ok",
    "Manual Mode",
    "DG Breakdown",
    "DG BER",
    "DG Overload",
    "Access issue",
]
FUEL_STATUS_CHOICES = ["Ok", "Fuel Sensor faulty"]


def clean_date_str(val):
  if pd.isna(val) or val is None:
    return ""
  val_str = str(val).strip()
  if val_str.lower() in ["nat", "nan", "none", "", "0"]:
    return ""
  try:
    dt = pd.to_datetime(val)
    return dt.strftime("%Y-%m-%d")
  except:
    return val_str.split(" ")[0] if " " in val_str else val_str


PASSWORD_CREDENTIALS = {
    hashlib.sha256("Gogoi@6095".encode()).hexdigest(): {
        "role": "Super Admin",
        "name": "Tridip Gogoi",
        "is_admin": True,
    },
    hashlib.sha256("Rintu@2026".encode()).hexdigest(): {
        "role": "NOC Viewer",
        "name": "PTPL Operations Desk",
        "is_admin": False,
    },
}


def verify_login(password):
  p_hash = hashlib.sha256(password.encode()).hexdigest()
  if p_hash in PASSWORD_CREDENTIALS:
    return PASSWORD_CREDENTIALS[p_hash]
  return None


def process_dataframe(df_status):
  for col in df_status.columns:
    df_status[col] = df_status[col].astype(object)

  try:
    if len(df_status.columns) > 28:
      col_ac_name = df_status.columns[28]
      df_status["Col AC (FSR CM link)"] = df_status[col_ac_name].apply(
          lambda x: "" if pd.isna(x) else str(x).strip()
      )
    else:
      df_status["Col AC (FSR CM link)"] = ""
  except:
    df_status["Col AC (FSR CM link)"] = ""

  try:
    if len(df_status.columns) > 29:
      col_ad_name = df_status.columns[29]
      df_status["Col AD (FSR PM link)"] = df_status[col_ad_name].apply(
          lambda x: "" if pd.isna(x) else str(x).strip()
      )
    else:
      df_status["Col AD (FSR PM link)"] = ""
  except:
    df_status["Col AD (FSR PM link)"] = ""

  if "SAIP ID" in df_status.columns:
    df_status = df_status[df_status["SAIP ID"].notna()]
    df_status["SAIP ID"] = df_status["SAIP ID"].astype(str).str.strip()
    df_status = df_status[
        ~df_status["SAIP ID"].str.lower().isin(
            ["", "nan", "none", "total", "0", "null"]
        )
    ]
  if "DG Make" in df_status.columns:
    df_status = df_status[df_status["DG Make"].notna()]
    df_status["DG Make"] = df_status["DG Make"].astype(str).str.strip()
  if "JC" in df_status.columns:
    df_status["JC"] = df_status["JC"].astype(str).str.strip()
  if "State" in df_status.columns:
    df_status["State"] = df_status["State"].astype(str).str.strip()
  if "Bucket" in df_status.columns:
    df_status["Bucket"] = df_status["Bucket"].astype(str).str.strip()
    df_status["Bucket"] = df_status["Bucket"].apply(
        lambda x: None if str(x).lower() in ["nan", "none", "", "nat"] else x
    )
  return df_status


def load_excel_tracker(uploaded_file=None):
  df_status = pd.DataFrame()
  try:
    if uploaded_file is not None:
      with open(DEFAULT_EXCEL, "wb") as f:
        f.write(uploaded_file.getbuffer())
      df_status = pd.read_excel(uploaded_file, sheet_name="Automation Status")
    elif os.path.exists(DEFAULT_EXCEL):
      df_status = pd.read_excel(DEFAULT_EXCEL, sheet_name="Automation Status")
    else:
      return df_status
    df_status = process_dataframe(df_status)
  except Exception as e:
    st.error(f"Excel Load Error: {e}")
  return df_status


def load_ila_tracker(uploaded_file=None):
  df_ila = pd.DataFrame()
  try:
    xl_file = None
    if uploaded_file is not None:
      xl_file = pd.ExcelFile(uploaded_file)
    elif os.path.exists(DEFAULT_EXCEL):
      xl_file = pd.ExcelFile(DEFAULT_EXCEL)

    if xl_file:
      target_sheet = None
      for sheet in xl_file.sheet_names:
        if "ipms site automation status" in sheet.lower():
          target_sheet = sheet
          break
      if not target_sheet and len(xl_file.sheet_names) > 1:
        target_sheet = xl_file.sheet_names[1]
      elif not target_sheet:
        target_sheet = xl_file.sheet_names[0]

      df_ila = pd.read_excel(xl_file, sheet_name=target_sheet)
      for col in df_ila.columns:
        df_ila[col] = df_ila[col].astype(object)
      if "Sap ID" in df_ila.columns:
        df_ila = df_ila[df_ila["Sap ID"].notna()]
        df_ila["Sap ID"] = df_ila["Sap ID"].astype(str).str.strip()
  except Exception as e:
    pass
  return df_ila


if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
  st.session_state.user_info = None

if not st.session_state.authenticated:
  _, col1, _ = st.columns([1, 1.2, 1])
  with col1:
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.96); padding: 2.2rem 2rem; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); border: 1px solid rgba(226, 232, 240, 0.8); margin: 3.5rem auto;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #0f172a; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.25rem;">⚡ DG NOC Portal</h2>
                <p style="color: #64748b; font-size: 0.9rem;">North East Circle Operations Gateway</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login"):
      p = st.text_input("Enter Password", type="password")
      if st.form_submit_button("Login", use_container_width=True, type="primary"):
        rec = verify_login(p)
        if rec:
          st.session_state.authenticated = True
          st.session_state.user_info = rec
          st.rerun()
        else:
          st.error("Invalid Password")
    st.markdown("</div>", unsafe_allow_html=True)
  st.stop()

user_data = st.session_state.user_info
admin_name = user_data["name"]
admin_role = user_data["role"]
is_admin = user_data.get("is_admin", False)

if (
    "master_tracker_df" not in st.session_state
    or st.session_state.master_tracker_df.empty
):
  st.session_state.master_tracker_df = load_excel_tracker()

if (
    "ila_tracker_df" not in st.session_state
    or st.session_state.ila_tracker_df.empty
):
  st.session_state.ila_tracker_df = load_ila_tracker()

# Admin-ৰ বাবে আপলোড আৰু ক্লিয়াৰ অপচন
if is_admin:
  with st.container(border=True):
    col_up1, col_up2 = st.columns([3, 1])
    with col_up1:
      uploaded_file = st.file_uploader(
          "📤 Upload Master Tracker (.xlsx) [Admin Only]",
          type=["xlsx", "xls"],
      )
      if uploaded_file is not None:
        st.session_state.master_tracker_df = load_excel_tracker(uploaded_file)
        st.session_state.ila_tracker_df = load_ila_tracker(uploaded_file)
        st.success(
            "✅ Tracker & IPMS Automation Status updated and saved to server!"
        )
    with col_up2:
      st.markdown("<br>", unsafe_allow_html=True)
      if st.button("🗑️ Clear File", use_container_width=True):
        if os.path.exists(DEFAULT_EXCEL):
          st.session_state.master_tracker_df = load_excel_tracker(DEFAULT_EXCEL)
          st.session_state.ila_tracker_df = load_ila_tracker(DEFAULT_EXCEL)
        else:
          st.session_state.master_tracker_df = pd.DataFrame()
          st.session_state.ila_tracker_df = pd.DataFrame()
        st.success("Cleared!")
        st.rerun()

df_status = st.session_state.master_tracker_df
df_ila = st.session_state.ila_tracker_df

# Operator info, Download report aru Refresh View
with st.container(border=True):
  top_c1, top_c2, top_c3 = st.columns([2, 1.5, 1.5])
  with top_c1:
    st.markdown(
        f"🛡️ **Operator:** `{admin_name}` | 🔑 **Role:** `{admin_role}`"
    )
  with top_c2:
    if st.button("🔄 Refresh View", type="primary", use_container_width=True):
      st.cache_data.clear()
      st.session_state.master_tracker_df = load_excel_tracker()
      st.session_state.ila_tracker_df = load_ila_tracker()
      st.rerun()
  with top_c3:
    if not df_status.empty:
      output = BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_status.to_excel(writer, sheet_name="Automation Status", index=False)
        if not df_ila.empty:
          df_ila.to_excel(
              writer, sheet_name="IPMS Site Automation Status", index=False
          )
      st.download_button(
          label="📥 Download Report",
          data=output.getvalue(),
          file_name=f"NE_Circle_Master_Operations_Report_{datetime.now(IST).strftime('%Y%m%d')}.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          use_container_width=True,
      )

# AI Site Diagnostics অপচনটো প্ৰথম নম্বৰত (1st) ৰখা হৈছে
page = st.radio(
    "Select View:",
    [
        "🔍 AI Site Diagnostics",
        "📊 Executive Control Center",
        "⚙️ Fleet Analytics & Problem Buckets",
        "⛽ Fuel Sensor Telemetry",
        "⏳ Daily Fault Summary",
        "📈 ILA-AG1 Operations Tracker",
        "✏️ In-Portal Master Tracker Editor",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

if page == "🔍 AI Site Diagnostics":
  st.markdown("## 🔍 AI Telemetry & Site Diagnostics Console")
  st.caption(
      "Circle-wide deep diagnostics, equipment specs, telemetry mapping, and"
      " field intervention radar."
  )

  with st.container(border=True):
    st.markdown(
        "<h4 style='margin:0 0 10px 0; color: #facc15;'>🎯 Targeted Site"
        " Telemetry Search</h4>",
        unsafe_allow_html=True,
    )
    sq = (
        st.text_input(
            "Search Network Site:",
            placeholder="Enter SAIP ID (e.g. 9011)...",
            label_visibility="collapsed",
        )
        .strip()
        .upper()
    )

  if sq and not df_status.empty and "SAIP ID" in df_status.columns:
    matches = df_status[
        df_status["SAIP ID"].astype(str).str.contains(sq, case=False, na=False)
    ]
    if matches.empty:
      st.error(f"❌ No network records found matching `{sq}`.")
    else:
      site_options_list = matches["SAIP ID"].tolist()
      st.markdown(
          f"<span style='color: #facc15; font-weight: 700;'>Multiple Sites"
          f" Found ({len(site_options_list)}):</span>",
          unsafe_allow_html=True,
      )
      chosen_site_id = st.selectbox(
          "Select Site ID:", site_options_list, label_visibility="collapsed"
      )

      selected_matches = matches[
          matches["SAIP ID"].astype(str) == str(chosen_site_id)
      ]
      site_row = (
          selected_matches.iloc[0]
          if not selected_matches.empty
          else matches.iloc[0]
      )
      selected_site = site_row["SAIP ID"]
      status_val = str(
          site_row.get("DG Automation Status", "Automation Ok")
      ).strip()

      s_lower = status_val.lower()
      if "ok" in s_lower:
        badge_bg = "#10b981"
      elif "manual" in s_lower:
        badge_bg = "#f59e0b"
      elif "breakdown" in s_lower or "ber" in s_lower:
        badge_bg = "#dc2626"
      else:
        badge_bg = "#f59e0b"

      jc_val = site_row.get("JC", "N/A")
      state_val = site_row.get("State", "N/A")
      site_type_val = site_row.get("Site Type", "P1")
      facility_5g = site_row.get("5G Facility", "NO")
      dg_make = site_row.get("DG Make", "N/A")
      dg_rating = site_row.get("DG Rating", "N/A")
      active_bucket = site_row.get("Bucket", "IPMS")
      aging_val = site_row.get("Aging (Day's)", 62)

      fuel_status_val = "Ok"
      for f_key in ["Fuel Sensor Status", "Fuel Sensor", "Fuel Status"]:
        if f_key in site_row and pd.notna(site_row[f_key]):
          val_s = str(site_row[f_key]).strip()
          if val_s and val_s.lower() not in ["nan", "none", "", "0", "nat"]:
            fuel_status_val = val_s
            break

      fuel_docket = ""
      for d_key in [
          "Fuel Sensor Docket No.",
          "Fuel Docket No.",
          "Fuel Sensor Docket",
          "Docket No.",
      ]:
        if d_key in site_row and pd.notna(site_row[d_key]):
          val_d = str(site_row[d_key]).strip()
          if val_d and val_d.lower() not in ["nan", "none", "", "0", "0.0", "nat"]:
            fuel_docket = val_d
            break

      fuel_open_date = ""
      for dt_key in [
          "Fuel Sensor Open Date",
          "Fuel Sensor Faulty Date",
          "Open Date",
          "Faulty Date",
      ]:
        if dt_key in site_row and pd.notna(site_row[dt_key]):
          val_dt = clean_date_str(site_row[dt_key])
          if val_dt:
            fuel_open_date = val_dt
            break

      fuel_extra = []
      if fuel_docket:
        fuel_extra.append(f"Docket No: {fuel_docket}")
      if fuel_open_date:
        fuel_extra.append(f"Open Date: {fuel_open_date}")

      fuel_display_str = fuel_status_val
      if fuel_extra:
        fuel_display_str += f" ({' | '.join(fuel_extra)})"

      present_remarks = "No remarks recorded."
      for r_key in ["Present Remarks", "Remarks", "Current Remarks"]:
        if r_key in site_row and pd.notna(site_row[r_key]):
          val_r = str(site_row[r_key]).strip()
          if val_r and val_r.lower() not in ["nan", "none", "", "0", "nat"]:
            present_remarks = val_r
            break

      pres_docket = str(site_row.get("Present Docket No.", "")).strip()
      if pres_docket.lower() in ["nan", "none", "", "0", "0.0", "nat"]:
        pres_docket = ""

      pres_raise_date = clean_date_str(
          site_row.get("Present Docket raise Date", "")
      )

      remarks_extra = []
      if pres_docket:
        remarks_extra.append(f"Present Docket No: {pres_docket}")
      if pres_raise_date:
        remarks_extra.append(f"Present Docket raise Date: {pres_raise_date}")

      remarks_display_str = present_remarks
      if remarks_extra:
        remarks_display_str += f"\n\n{' | '.join(remarks_extra)}"

      sup_name = site_row.get("Supervisor Name", "Mojib Kumar Saikia")
      trt_person = site_row.get("TRT Personnel", "Manseng Marak")
      contact_no = site_row.get("Contact No.", "7002843853.0")
      dep_sites = site_row.get("Dependent Site", "nan")
      oem_vendor = site_row.get("OEM Vendor", "Pratap")
      grid_conn = site_row.get("EB Grid Connection", "EB + DG")
      battery_backup = site_row.get("F.Battery Backup (Min)", "120")

      st.markdown(
          f"""
            <div style="background-color: #0f172a; border: 2px solid #facc15; border-radius: 10px; padding: 18px 22px; margin-top: 10px; margin-bottom: 14px; box-shadow: 0 4px 15px rgba(250, 204, 21, 0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: #f97316; font-size: 22px; font-weight: 800;">⚡ {selected_site}</span>
                    </div>
                    <div>
                        <span style="background-color: {badge_bg}; color: #ffffff; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase;">{status_val}</span>
                    </div>
                </div>
                <div style="margin-top: 10px; color: #94a3b8; font-size: 13px; font-weight: 600;">
                    Territory: <span style="color: #ffffff;">{jc_val}</span> &nbsp;|&nbsp; 
                    State: <span style="color: #ffffff;">{state_val}</span> &nbsp;|&nbsp; 
                    Site Type: <span style="color: #ffffff;">{site_type_val}</span> &nbsp;|&nbsp; 
                    5G Facility: <span style="color: #ffffff;">{facility_5g}</span>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      mc1, mc2, mc3, mc4 = st.columns(4)
      with mc1:
        st.markdown(
            f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                    <h4 style="color: #facc15 !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">DG Manufacturer</h4>
                    <span style="color: #ffffff; font-size: 26px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{dg_make}</span><br>
                    <span style="color: #10b981; font-size: 12px; font-weight: 700;">↑ {dg_rating}</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      with mc2:
        st.markdown(
            f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                    <h4 style="color: #facc15 !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Active Problem Bucket</h4>
                    <span style="color: #ffffff; font-size: 26px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{active_bucket}</span><br>
                    <span style="color: #10b981; font-size: 12px; font-weight: 700;">↑ Root-Cause</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      with mc3:
        st.markdown(
            f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                    <h4 style="color: #facc15 !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Incident Aging</h4>
                    <span style="color: #ffffff; font-size: 26px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{aging_val} Days</span><br>
                    <span style="color: #10b981; font-size: 12px; font-weight: 700;">↑ Delay Bracket</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      with mc4:
        st.markdown(
            f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                    <h4 style="color: #facc15 !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Fuel Telemetry</h4>
                    <span style="color: #ffffff; font-size: 26px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{fuel_status_val}</span><br>
                    <span style="color: #10b981; font-size: 12px; font-weight: 700;">↑ Sensor Health</span>
                </div>
                """,
            unsafe_allow_html=True,
        )

      st.markdown(
          f"""
            <div style="background-color: #1e293b; border: 2px solid #facc15; padding: 14px 18px; border-radius: 8px; margin-top: 12px; margin-bottom: 14px; color: #ffffff; font-size: 13px; font-weight: 600; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
                <span style="color: #facc15; font-weight: 800; font-size: 14px;">🧠 AI Diagnostic Inference:</span> <span style="color: #f8fafc;">⚠️ <b>Attention Required:</b> Status active (`{status_val}`). Problem classified under `{active_bucket}`.</span><br>
                <span style="color: #38bdf8; font-weight: 700;">🎯 Recommended Operational Action (SOP):</span> <span style="color: #ffffff;">Verify site access and contact the local supervisor for direct diagnosis.</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

      diag_t1, diag_t2, diag_t3, diag_t4 = st.tabs([
          "📋 Technical Asset Specifications",
          "⚡ Master Tracker (Live) Telemetry",
          "⏳ Resolution History & Previous Dockets (Col Y to AB)",
          "🔗 FSR CM & PM Links (Col AC & AD)",
      ])

      with diag_t1:
        with st.container(border=True):
          sc1, sc2 = st.columns(2)
          with sc1:
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>DG"
                f" Make:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{dg_make}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>DG"
                f" Rating:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{dg_rating}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>OEM"
                f" Vendor:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{oem_vendor}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>EB Grid"
                f" Connection:</span> <span style='color: #
