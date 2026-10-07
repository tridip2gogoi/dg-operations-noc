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

    /* Professional Navigation Radio Button Styling */
    div[data-testid="stRadio"] label p, div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #facc15 !important; font-weight: 800 !important; font-size: 14px !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
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

DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"

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
    return dt.strftime("%d-%b-%Y")
  except:
    return val_str.split(" ")[0] if " " in val_str else val_str


PASSWORD_CREDENTIALS = {
    hashlib.sha256("Gogoi&6095".encode()).hexdigest(): {
        "role": "Super Admin",
        "name": "Tridip Gogoi",
        "is_admin": True,
    },
     hashlib.sha256("Sukanta@2026".encode()).hexdigest(): {
        "role": "Super Admin",
        "name": "SME Operations Desk",
        "is_admin": True,
    },
    hashlib.sha256("Rintu@2026".encode()).hexdigest(): {
        "role": "NOC Viewer",
        "name": "PTPL Operations Desk",
        "is_admin": False,
    },
     hashlib.sha256("SHQ@2026".encode()).hexdigest(): {
        "role": "NOC Viewer",
        "name": "SHQ Operations Desk",
        "is_admin": False,
    },
     hashlib.sha256("Nipl@2026".encode()).hexdigest(): {
        "role": "NOC Viewer",
        "name": "Fild Operations Desk",
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
        <div style="background: rgba(15, 23, 42, 0.92); padding: 2.2rem 2rem; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.7); border: 2px solid #facc15; margin: 3.5rem auto;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #facc15 !important; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.25rem;">⚡ DG NOC Portal</h2>
                <p style="color: #cbd5e1 !important; font-size: 0.9rem;">North East Circle Operations Gateway</p>
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

# Admin-ৰ বাবে আপলোড আৰু ক্লিয়াৰ অপচন
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

      # --- Previous Remarks (Col Z), Docket Raise Date (Col AA / index 26) & Closed Date (Col AB / index 27) ---
      prev_remarks = "No previous remarks."
      for pr_key in ["Previous Remarks", "Prev Remarks"]:
        if pr_key in site_row and pd.notna(site_row[pr_key]):
          val_pr = str(site_row[pr_key]).strip()
          if val_pr and val_pr.lower() not in ["nan", "none", "", "0", "nat"]:
            prev_remarks = val_pr
            break

      prev_raise_date = ""
      try:
        if len(site_row.index) > 26:
          col_aa_val = site_row.iloc[26]  # Column AA is index 26
          if pd.notna(col_aa_val):
            prev_raise_date = clean_date_str(col_aa_val)
      except:
        pass

      if not prev_raise_date:
        for prd_key in [
            "Previous Docket raise Date",
            "Previous Raise Date",
            "Prev Raise Date",
        ]:
          if prd_key in site_row and pd.notna(site_row[prd_key]):
            val_prd = clean_date_str(site_row[prd_key])
            if val_prd:
              prev_raise_date = val_prd
              break

      prev_closed_date = ""
      try:
        if len(site_row.index) > 27:
          col_ab_val = site_row.iloc[27]  # Column AB is index 27
          if pd.notna(col_ab_val):
            prev_closed_date = clean_date_str(col_ab_val)
      except:
        pass

      if not prev_closed_date:
        for pcd_key in [
            "Previous Closed Date",
            "Prev Closed Date",
            "Closed Date",
        ]:
          if pcd_key in site_row and pd.notna(site_row[pcd_key]):
            val_pcd = clean_date_str(site_row[pcd_key])
            if val_pcd:
              prev_closed_date = val_pcd
              break

      prev_extra = []
      if prev_raise_date:
        prev_extra.append(f"Docket Raise Date: {prev_raise_date}")
      if prev_closed_date:
        prev_extra.append(f"Closed Date: {prev_closed_date}")

      prev_remarks_display_str = prev_remarks
      if prev_extra:
        prev_remarks_display_str += f"\n\n{' | '.join(prev_extra)}"

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
                f" Connection:</span> <span style='color: #ffffff;"
                f" font-weight: 800;'>`{grid_conn}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>Battery"
                f" Backup (Min):</span> <span style='color: #ffffff;"
                f" font-weight: 800;'>`{battery_backup}`</span>",
                unsafe_allow_html=True,
            )
          with sc2:
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>Supervisor"
                f" Name:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{sup_name}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>TRT"
                f" Personnel:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{trt_person}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>Contact"
                f" Number:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{contact_no}`</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #facc15; font-weight: 700;'>Dependent"
                f" Sites:</span> <span style='color: #ffffff; font-weight:"
                f" 800;'>`{dep_sites}`</span>",
                unsafe_allow_html=True,
            )

      with diag_t2:
        with st.container(border=True):
          st.markdown(
              f"<span style='color: #facc15; font-weight: 700;'>Fuel Sensor"
              f" Status:</span> <span style='color: #ffffff; font-weight:"
              f" 800;'>`{fuel_display_str}`</span>",
              unsafe_allow_html=True,
          )
          st.markdown(
              f"<span style='color: #facc15; font-weight: 700;'>Present"
              f" Remarks:</span>",
              unsafe_allow_html=True,
          )
          st.markdown(
              f'<div class="previous-remarks-box">{remarks_display_str}</div>',
              unsafe_allow_html=True,
          )

      with diag_t3:
        with st.container(border=True):
          st.markdown(
              f"<span style='color: #facc15; font-weight: 700;'>Previous"
              f" Docket No (Col AA):</span> <span style='color: #ffffff;"
              f" font-weight: 800;'>`{site_row.get('Previous Docket No.', 'None')}`</span>",
              unsafe_allow_html=True,
          )
          st.markdown(
              "<span style='color: #facc15; font-weight: 700;'>Previous"
              " Remarks (Col Z):</span>",
              unsafe_allow_html=True,
          )
          st.markdown(
              f'<div class="previous-remarks-box">{prev_remarks_display_str}</div>',
              unsafe_allow_html=True,
          )

      with diag_t4:
        with st.container(border=True):
          cm_link = site_row.get("Col AC (FSR CM link)", "")
          pm_link = site_row.get("Col AD (FSR PM link)", "")

          col_l1, col_l2 = st.columns(2)
          with col_l1:
            st.markdown("#### 📄 FSR CM Link (Col AC)")
            if cm_link and str(cm_link).lower() not in [
                "",
                "nan",
                "none",
                "0",
                "0.0",
                "nat",
            ]:
              st.markdown(f"`{cm_link}`")
              cm_url = (
                  cm_link
                  if cm_link.startswith(("http://", "https://"))
                  else (
                      f"https://{cm_link}"
                      if cm_link.startswith("www.")
                      else f"https://drive.google.com/drive/u/0/search?q={cm_link}"
                  )
              )
              st.link_button(
                  "🌐 Open FSR CM Link", cm_url, use_container_width=True
              )
            else:
              st.info("No FSR CM link available in Col AC.")

          with col_l2:
            st.markdown("#### 📄 FSR PM Link (Col AD)")
            if pm_link and str(pm_link).lower() not in [
                "",
                "nan",
                "none",
                "0",
                "0.0",
                "nat",
            ]:
              st.markdown(f"`{pm_link}`")
              pm_url = (
                  pm_link
                  if pm_link.startswith(("http://", "https://"))
                  else (
                      f"https://{pm_link}"
                      if pm_link.startswith("www.")
                      else f"https://drive.google.com/drive/u/0/search?q={pm_link}"
                  )
              )
              st.link_button(
                  "🌐 Open FSR PM Link", pm_url, use_container_width=True
              )
            else:
              st.info("No FSR PM link available in Col AD.")

elif page == "📊 Executive Control Center":
  st.markdown("## ⚡ North East Circle - DG Operations Control Center")
  if not df_status.empty:
    tot = len(df_status)
    ok = (
        len(
            df_status[
                df_status["DG Automation Status"].astype(str).str.strip()
                == "Automation Ok"
            ]
        )
        if "DG Automation Status" in df_status.columns
        else 0
    )
    man = (
        len(
            df_status[
                df_status["DG Automation Status"].astype(str).str.strip()
                == "Manual Mode"
            ]
        )
        if "DG Automation Status" in df_status.columns
        else 0
    )
    bd = (
        len(
            df_status[
                df_status["DG Automation Status"]
                .astype(str)
                .str.strip()
                .str.lower()
                == "dg breakdown"
            ]
        )
        if "DG Automation Status" in df_status.columns
        else 0
    )
    ber = (
        len(
            df_status[
                df_status["DG Automation Status"]
                .astype(str)
                .str.strip()
                .str.lower()
                == "dg ber"
            ]
        )
        if "DG Automation Status" in df_status.columns
        else 0
    )
    ovr = (
        len(
            df_status[
                df_status["DG Automation Status"]
                .astype(str)
                .str.strip()
                .str.lower()
                == "dg overload"
            ]
        )
        if "DG Automation Status" in df_status.columns
        else 0
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Sites", f"{tot:,}")
    k2.metric("Automation Rate", f"{round((ok/tot)*100, 1)}%" if tot else "0%")
    k3.metric("Manual Mode", man)
    k4.metric("DG Breakdown", bd)
    k5.metric("DG BER", ber)
    k6.metric("DG Overload", ovr)

    st.markdown("---")
    if "State" in df_status.columns:
      state_options = ["All States"] + sorted([
          str(x)
          for x in df_status["State"].dropna().unique()
          if str(x).strip().lower() not in ["", "nan", "none"]
      ])
      selected_state = st.selectbox("🌐 Filter Circle by State:", state_options)
      state_filtered_df = (
          df_status
          if selected_state == "All States"
          else df_status[
              df_status["State"].astype(str).str.strip() == selected_state
          ]
      )

      c1, c2 = st.columns([3, 2])
      with c1:
        with st.container(border=True):
          st.markdown(
              "<h4 style='margin:0 0 10px 0; color: #facc15;'>JC / State Wise"
              " Automation Health</h4>",
              unsafe_allow_html=True,
          )
          if (
              "JC" in state_filtered_df.columns
              and "DG Automation Status" in state_filtered_df.columns
          ):
            fig_bar = px.histogram(
                state_filtered_df,
                x="JC",
                color="DG Automation Status",
                barmode="group",
                color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#6366f1"],
            )
            fig_bar.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
      with c2:
        with st.container(border=True):
          st.markdown(
              "<h4 style='margin:0 0 10px 0; color: #facc15;'>DG Make Fleet"
              " Allocation</h4>",
              unsafe_allow_html=True,
          )
          if "DG Make" in state_filtered_df.columns:
            valid_makes = state_filtered_df[
                state_filtered_df["DG Make"].notna()
                & (state_filtered_df["DG Make"].astype(str).str.strip() != "")
            ]
            fig_donut = px.pie(
                valid_makes,
                names="DG Make",
                hole=0.58,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_donut.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
            )
            st.plotly_chart(fig_donut, use_container_width=True)

elif page == "⚙️ Fleet Analytics & Problem Buckets":
  st.markdown("## ⚙️ Fleet Automation Classification & Root-Cause Analysis")
  st.caption(
      "JC-wise breakdown of network automation health, problem buckets, and"
      " docket fulfillment statuses."
  )

  if not df_status.empty:
    jc_options = (
        ["All JCs"]
        + sorted([
            str(x)
            for x in df_status["JC"].dropna().unique()
            if str(x).strip().lower() not in ["", "nan", "none"]
        ])
        if "JC" in df_status.columns
        else ["All JCs"]
    )
    selected_fleet_jc = st.selectbox("Select JC Circle:", jc_options)

    filtered_status = (
        df_status
        if selected_fleet_jc == "All JCs" or "JC" not in df_status.columns
        else df_status[
            df_status["JC"].astype(str).str.strip() == selected_fleet_jc
        ]
    )

    if "DG Automation Status" in filtered_status.columns:
      valid_bucket_base = filtered_status[
          filtered_status["DG Automation Status"]
          .astype(str)
          .str.strip()
          .str.lower()
          != "automation ok"
      ].copy()
    else:
      valid_bucket_base = filtered_status.copy()

    valid_bucket = (
        valid_bucket_base[
            valid_bucket_base["Bucket"].notna()
            & (valid_bucket_base["Bucket"].astype(str).str.strip() != "")
        ]
        if "Bucket" in valid_bucket_base.columns
        else pd.DataFrame()
    )

    col1, col2 = st.columns([1, 2])
    with col1:
      with st.container(border=True):
        st.markdown(
            f"<h4 style='margin:0 0 10px 0; color: #facc15;'>Status Summary"
            f" ({selected_fleet_jc})</h4>",
            unsafe_allow_html=True,
        )
        if "DG Automation Status" in filtered_status.columns:
          stat_summary = (
              filtered_status["DG Automation Status"]
              .value_counts(dropna=False)
              .reset_index()
          )
          stat_summary.columns = ["Status Category", "Site Count"]
          st.dataframe(stat_summary, use_container_width=True, hide_index=True)
    with col2:
      with st.container(border=True):
        st.markdown(
            f"<h4 style='margin:0 0 10px 0; color: #facc15;'>Bucket"
            f" Distribution ({selected_fleet_jc})</h4>",
            unsafe_allow_html=True,
        )
        if not valid_bucket.empty:
          b_summary = valid_bucket["Bucket"].value_counts().reset_index()
          b_summary.columns = ["Root-Cause Bucket", "Incidents"]
          fig_b = px.bar(
              b_summary,
              x="Root-Cause Bucket",
              y="Incidents",
              text="Incidents",
              color="Incidents",
              color_continuous_scale="Blues",
          )
          fig_b.update_layout(
              height=340,
              margin=dict(l=10, r=10, t=10, b=10),
              plot_bgcolor="#ffffff",
              paper_bgcolor="#ffffff",
          )
          st.plotly_chart(fig_b, use_container_width=True)
        else:
          st.info("No active problem bucket recorded.")

    st.markdown("---")
    t1, t2, t3, t4, t5 = st.tabs([
        "📊 JC-Wise Automation Status Matrix",
        "🗂️ JC-Wise Problem Bucket Matrix",
        "⚡ GCU Sites: JC vs DG Make & KVA",
        "🛠️ DG Breakdown & Manual (GCU, OEM, Breakdown)",
        "📋 JC-Wise Docket Received & Pending Summary",
    ])

    with t1:
      with st.container(border=True):
        st.markdown(
            "<h4 style='color: #facc15;'>JC vs DG Automation Status"
            " Cross-Tabulation</h4>",
            unsafe_allow_html=True,
        )
        if (
            "JC" in df_status.columns
            and "DG Automation Status" in df_status.columns
        ):
          st.dataframe(
              pd.crosstab(
                  df_status["JC"],
                  df_status["DG Automation Status"],
                  margins=True,
                  margins_name="Total",
              ),
              use_container_width=True,
          )
    with t2:
      with st.container(border=True):
        st.markdown(
            "<h4 style='color: #facc15;'>JC vs Root-Cause Bucket"
            " Cross-Tabulation</h4>",
            unsafe_allow_html=True,
        )
        if "JC" in df_status.columns and "Bucket" in df_status.columns:
          clean_bkt = df_status[
              df_status["DG Automation Status"]
              .astype(str)
              .str.strip()
              .str.lower()
              != "automation ok"
          ]
          st.dataframe(
              pd.crosstab(
                  clean_bkt["JC"],
                  clean_bkt["Bucket"],
                  margins=True,
                  margins_name="Total",
              ),
              use_container_width=True,
          )
    with t3:
      with st.container(border=True):
        st.markdown(
            "<h4 style='color: #facc15;'>GCU Sites: JC vs DG Make & KVA"
            " Breakdown</h4>",
            unsafe_allow_html=True,
        )
        if "Bucket" in df_status.columns:
          df_gcu = df_status[
              df_status["Bucket"].astype(str).str.strip().str.upper() == "GCU"
          ]
          if (
              not df_gcu.empty
              and "DG Make" in df_gcu.columns
              and "DG Rating" in df_gcu.columns
          ):
            st.dataframe(
                pd.crosstab(
                    [df_gcu["JC"], df_gcu["DG Make"]],
                    df_gcu["DG Rating"],
                    margins=True,
                    margins_name="Total",
                ),
                use_container_width=True,
            )
    with t4:
      with st.container(border=True):
        st.markdown(
            "<h4 style='color: #facc15;'>JC-Wise: DG Breakdown & Manual (GCU,"
            " OEM, Breakdown)</h4>",
            unsafe_allow_html=True,
        )
        bm_f1, bm_f2, bm_f3, bm_f4 = st.columns(4)
        with bm_f1:
          b_states = (
              ["All States"]
              + sorted([
                  str(x)
                  for x in df_status["State"].dropna().unique()
                  if str(x).strip().lower() not in ["", "nan", "none"]
              ])
              if "State" in df_status.columns
              else ["All States"]
          )
          chosen_b_state = st.selectbox(
              "Filter State:", b_states, key="breakdown_state_filter"
          )
        with bm_f2:
          b_jcs = (
              ["All JCs"]
              + sorted([
                  str(x)
                  for x in df_status["JC"].dropna().unique()
                  if str(x).strip().lower() not in ["", "nan", "none"]
              ])
              if "JC" in df_status.columns
              else ["All JCs"]
          )
          chosen_b_jc = st.selectbox(
              "Filter JC:", b_jcs, key="breakdown_jc_filter"
          )
        with bm_f3:
          b_statuses = (
              ["All Statuses"]
              + sorted([
                  str(x)
                  for x in df_status["DG Automation Status"].dropna().unique()
                  if str(x).strip().lower()
                  not in ["", "nan", "none", "automation ok"]
              ])
              if "DG Automation Status" in df_status.columns
              else ["All Statuses"]
          )
          chosen_b_status = st.selectbox(
              "Filter Status:", b_statuses, key="breakdown_status_filter"
          )
        with bm_f4:
          b_buckets = (
              ["All Buckets"]
              + sorted([
                  str(x)
                  for x in df_status["Bucket"].dropna().unique()
                  if str(x).strip().lower() not in ["", "nan", "none"]
              ])
              if "Bucket" in df_status.columns
              else ["All Buckets"]
          )
          chosen_b_bucket = st.selectbox(
              "Filter Bucket:", b_buckets, key="breakdown_bucket_filter"
          )

        filtered_b_df = df_status.copy()
        if not filtered_b_df.empty:
          if "DG Automation Status" in filtered_b_df.columns:
            filtered_b_df = filtered_b_df[
                filtered_b_df["DG Automation Status"]
                .astype(str)
                .str.strip()
                .str.lower()
                != "automation ok"
            ]
          if chosen_b_state != "All States" and "State" in filtered_b_df.columns:
            filtered_b_df = filtered_b_df[
                filtered_b_df["State"].astype(str).str.strip() == chosen_b_state
            ]
          if chosen_b_jc != "All JCs" and "JC" in filtered_b_df.columns:
            filtered_b_df = filtered_b_df[
                filtered_b_df["JC"].astype(str).str.strip() == chosen_b_jc
            ]
          if (
              chosen_b_status != "All Statuses"
              and "DG Automation Status" in filtered_b_df.columns
          ):
            filtered_b_df = filtered_b_df[
                filtered_b_df["DG Automation Status"].astype(str).str.strip()
                == chosen_b_status
            ]
          if chosen_b_bucket != "All Buckets" and "Bucket" in filtered_b_df.columns:
            filtered_b_df = filtered_b_df[
                filtered_b_df["Bucket"].astype(str).str.strip()
                == chosen_b_bucket
            ]

        st.markdown("##### JC-Wise Summary: Bucket Distribution")
        if (
            "JC" in filtered_b_df.columns
            and "Bucket" in filtered_b_df.columns
            and not filtered_b_df.empty
        ):
          st.dataframe(
              pd.crosstab(
                  filtered_b_df["JC"],
                  filtered_b_df["Bucket"],
                  margins=True,
                  margins_name="Total",
              ),
              use_container_width=True,
          )
        st.markdown("##### Detailed Site Records")
        st.dataframe(filtered_b_df, use_container_width=True)

    with t5:
      with st.container(border=True):
        st.markdown(
            "<h4 style='color: #facc15;'>JC-Wise Docket Received & Pending"
            " Summary (DG Breakdown, GCU, OEM Spare part)</h4>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Filters strictly for Buckets: **DG Breakdown**, **GCU**, and **OEM"
            " Spare parts**, categorized by Docket Received vs Docket Pending."
        )

        p_f1, p_f2 = st.columns(2)
        with p_f1:
          p_states = (
              ["All States"]
              + sorted([
                  str(x)
                  for x in df_status["State"].dropna().unique()
                  if str(x).strip().lower() not in ["", "nan", "none"]
              ])
              if "State" in df_status.columns
              else ["All States"]
          )
          chosen_p_state = st.selectbox(
              "Filter State:", p_states, key="docket_state_filter"
          )
        with p_f2:
          p_jcs = (
              ["All JCs"]
              + sorted([
                  str(x)
                  for x in df_status["JC"].dropna().unique()
                  if str(x).strip().lower() not in ["", "nan", "none"]
              ])
              if "JC" in df_status.columns
              else ["All JCs"]
          )
          chosen_p_jc = st.selectbox(
              "Filter JC:", p_jcs, key="docket_jc_filter"
          )

        docket_df = df_status.copy()
        if not docket_df.empty:
          if "DG Automation Status" in docket_df.columns:
            docket_df = docket_df[
                docket_df["DG Automation Status"]
                .astype(str)
                .str.strip()
                .str.lower()
                != "automation ok"
            ]
          if "Bucket" in docket_df.columns:
            docket_df["Bucket_Clean"] = (
                docket_df["Bucket"].astype(str).str.strip().str.title()
            )
            target_bkts = [
                b.title() for b in ["DG Breakdown", "GCU", "OEM Spare parts"]
            ]
            docket_df = docket_df[docket_df["Bucket_Clean"].isin(target_bkts)]
          if chosen_p_state != "All States" and "State" in docket_df.columns:
            docket_df = docket_df[
                docket_df["State"].astype(str).str.strip() == chosen_p_state
            ]
          if chosen_p_jc != "All JCs" and "JC" in docket_df.columns:
            docket_df = docket_df[
                docket_df["JC"].astype(str).str.strip() == chosen_p_jc
            ]

          def get_docket_status(row):
            doc = str(row.get("Present Docket No.", "")).strip()
            if doc and doc.lower() not in [
                "",
                "nan",
                "none",
                "0",
                "0.0",
                "nat",
            ]:
              return "Docket Received"
            else:
              return "Docket Pending"

          if not docket_df.empty:
            docket_df["Docket_Status"] = docket_df.apply(
                get_docket_status, axis=1
            )
            st.markdown(
                "##### JC-Wise Cross-Tabulation: Bucket vs Docket Status"
            )
            docket_matrix = pd.crosstab(
                docket_df["JC"],
                [docket_df["Bucket_Clean"], docket_df["Docket_Status"]],
                margins=True,
                margins_name="Total",
            )
            st.dataframe(docket_matrix, use_container_width=True)
            st.markdown("##### Detailed Docket Summary Records")
            st.dataframe(docket_df, use_container_width=True)
          else:
            st.info("No records matching the selected buckets and filters.")
        else:
          st.info("No data available.")

elif page == "⛽ Fuel Sensor Telemetry":
  st.markdown("## ⛽ Fuel Sensor Fault Telemetry")
  st.caption(
      "Active fuel sensor fault distribution automatically scanned from Master"
      " Tracker and cross-tabulated strictly by JC, DG Make, and KVA rating."
  )

  auto_df_fuel = pd.DataFrame()
  if not df_status.empty:
    bkt_match = (
        df_status["Bucket"].astype(str).str.strip().str.upper() == "FUEL SENSOR"
        if "Bucket" in df_status.columns
        else pd.Series([False] * len(df_status))
    )
    stat_match = (
        df_status["Fuel Sensor Status"]
        .astype(str)
        .str.strip()
        .str.upper()
        == "FUEL SENSOR FAULTY"
        if "Fuel Sensor Status" in df_status.columns
        else pd.Series([False] * len(df_status))
    )
    auto_df_fuel = df_status[bkt_match | stat_match].copy()

  if not auto_df_fuel.empty:
    fuel_jcs = (
        ["All JCs"]
        + sorted([
            str(x)
            for x in auto_df_fuel["JC"].dropna().unique()
            if str(x).strip().lower() not in ["", "nan", "none"]
        ])
        if "JC" in auto_df_fuel.columns
        else ["All JCs"]
    )
    chosen_fuel_jc = st.selectbox(
        "🌐 Filter JC for Fuel Sensor Telemetry:",
        fuel_jcs,
        key="fuel_jc_filter",
    )

    if chosen_fuel_jc != "All JCs" and "JC" in auto_df_fuel.columns:
      auto_df_fuel_filtered = auto_df_fuel[
          auto_df_fuel["JC"].astype(str).str.strip() == chosen_fuel_jc
      ]
    else:
      auto_df_fuel_filtered = auto_df_fuel

    tot_faults = len(auto_df_fuel_filtered)
    aff_jc = (
        auto_df_fuel_filtered["JC"].mode()[0]
        if "JC" in auto_df_fuel_filtered.columns
        and not auto_df_fuel_filtered["JC"].mode().empty
        else "N/A"
    )
    p_make = (
        auto_df_fuel_filtered["DG Make"].mode()[0]
        if "DG Make" in auto_df_fuel_filtered.columns
        and not auto_df_fuel_filtered["DG Make"].mode().empty
        else "N/A"
    )
    p_rat = (
        auto_df_fuel_filtered["DG Rating"].mode()[0]
        if "DG Rating" in auto_df_fuel_filtered.columns
        and not auto_df_fuel_filtered["DG Rating"].mode().empty
        else "N/A"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 18px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Active Faulty Sensors (Master)</h4>
                <span style="color: #ffffff; font-size: 32px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{tot_faults}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with c2:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 18px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Most Affected JC</h4>
                <span style="color: #ffffff; font-size: 32px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{aff_jc}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with c3:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 18px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Primary Fault Make</h4>
                <span style="color: #ffffff; font-size: 32px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{p_make}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with c4:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 18px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Primary Fault Rating</h4>
                <span style="color: #ffffff; font-size: 32px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{p_rat}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")
    with st.container(border=True):
      st.markdown(
          "<h4 style='color: #facc15;'>JC-Wise Faulty Sensors Breakdown</h4>",
          unsafe_allow_html=True,
      )
      if (
          "JC" in auto_df_fuel_filtered.columns
          and "DG Make" in auto_df_fuel_filtered.columns
      ):
        st.dataframe(
            pd.crosstab(
                auto_df_fuel_filtered["JC"],
                auto_df_fuel_filtered["DG Make"],
                margins=True,
                margins_name="Total",
            ),
            use_container_width=True,
        )

    with st.container(border=True):
      st.markdown(
          "<h4 style='color: #facc15;'>DG Make Wise & KVA Rating Fault"
          " Telemetry</h4>",
          unsafe_allow_html=True,
      )
      if (
          "DG Make" in auto_df_fuel_filtered.columns
          and "DG Rating" in auto_df_fuel_filtered.columns
      ):
        st.dataframe(
            pd.crosstab(
                auto_df_fuel_filtered["DG Make"],
                auto_df_fuel_filtered["DG Rating"],
                margins=True,
                margins_name="Total",
            ),
            use_container_width=True,
        )

    with st.container(border=True):
      st.markdown(
          "<h4 style='color: #facc15;'>Active Fuel Sensor Fault Site"
          " Registry</h4>",
          unsafe_allow_html=True,
      )
      st.dataframe(auto_df_fuel_filtered, use_container_width=True)
  else:
    st.info("No active fuel sensor faults detected in Master Tracker.")

elif page == "⏳ Daily Fault Summary":
  st.markdown("## ⏳ Daily Fault Summary & JC-Wise Breakdown")
  st.caption(
      "Filter faults by specific date (scanned from Col W: Present Docket"
      " raise Date) and analyze State, JC, and Problem Buckets."
  )

  if not df_status.empty:
    dc_f1, dc_f2, dc_f3 = st.columns(3)
    with dc_f1:
      selected_date_filter = "All Dates"
      if "Present Docket raise Date" in df_status.columns:
        valid_dates = sorted([
            str(x)
            for x in df_status["Present Docket raise Date"].dropna().unique()
            if str(x).strip().lower() not in ["", "nat", "nan", "none", "0"]
        ])
        date_options = ["All Dates"] + valid_dates
        selected_date_filter = st.selectbox(
            "📅 Select Date (Col W):", date_options
        )
    with dc_f2:
      summary_state_opts = (
          ["All States"]
          + sorted([
              str(x)
              for x in df_status["State"].dropna().unique()
              if str(x).strip().lower() not in ["", "nan", "none"]
          ])
          if "State" in df_status.columns
          else ["All States"]
      )
      chosen_summary_state = st.selectbox(
          "🌐 Filter by State:", summary_state_opts, key="summary_state_filter"
      )
    with dc_f3:
      summary_jc_opts = (
          ["All JCs"]
          + sorted([
              str(x)
              for x in df_status["JC"].dropna().unique()
              if str(x).strip().lower() not in ["", "nan", "none"]
          ])
          if "JC" in df_status.columns
          else ["All JCs"]
      )
      chosen_summary_jc = st.selectbox(
          "🌐 Filter by JC Circle:", summary_jc_opts, key="summary_jc_filter"
      )

    filtered_date_df = df_status.copy()
    if not filtered_date_df.empty:
      if (
          selected_date_filter != "All Dates"
          and "Present Docket raise Date" in filtered_date_df.columns
      ):
        filtered_date_df = filtered_date_df[
            filtered_date_df["Present Docket raise Date"]
            .astype(str)
            .str.startswith(selected_date_filter)
        ]
      if (
          chosen_summary_state != "All States"
          and "State" in filtered_date_df.columns
      ):
        filtered_date_df = filtered_date_df[
            filtered_date_df["State"].astype(str).str.strip()
            == chosen_summary_state
        ]
      if chosen_summary_jc != "All JCs" and "JC" in filtered_date_df.columns:
        filtered_date_df = filtered_date_df[
            filtered_date_df["JC"].astype(str).str.strip() == chosen_summary_jc
        ]

    p_fuel_sensor = (
        len(
            filtered_date_df[
                (
                    filtered_date_df["Bucket"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    == "FUEL SENSOR"
                )
                | (
                    filtered_date_df["Fuel Sensor Status"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    == "FUEL SENSOR FAULTY"
                )
            ]
        )
        if not filtered_date_df.empty and "Bucket" in filtered_date_df.columns
        else 0
    )
    p_dg_battery = (
        len(
            filtered_date_df[
                filtered_date_df["Bucket"]
                .astype(str)
                .str.strip()
                .str.lower()
                == "dg battery"
            ]
        )
        if not filtered_date_df.empty and "Bucket" in filtered_date_df.columns
        else 0
    )
    p_gcu = (
        len(
            filtered_date_df[
                filtered_date_df["Bucket"]
                .astype(str)
                .str.strip()
                .str.lower()
                == "gcu"
            ]
        )
        if not filtered_date_df.empty and "Bucket" in filtered_date_df.columns
        else 0
    )
    p_oem = (
        len(
            filtered_date_df[
                filtered_date_df["Bucket"]
                .astype(str)
                .str.strip()
                .str.lower()
                == "oem spare parts"
            ]
        )
        if not filtered_date_df.empty and "Bucket" in filtered_date_df.columns
        else 0
    )
    tot_master_base = len(df_status)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Filtered Faults</h4>
                <span style="color: #ffffff; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{len(filtered_date_df):,}</span><br>
                <span style="color: #10b981; font-size: 11px; font-weight: 700;">↑ Date: {selected_date_filter}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with m2:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Fuel Sensor Faults</h4>
                <span style="color: #ffffff; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{p_fuel_sensor:,}</span><br>
                <span style="color: #10b981; font-size: 11px; font-weight: 700;">↑ Active Faults</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with m3:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">DG Battery</h4>
                <span style="color: #ffffff; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{p_dg_battery:,}</span><br>
                <span style="color: #10b981; font-size: 11px; font-weight: 700;">↑ Battery Issues</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with m4:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">GCU Faults</h4>
                <span style="color: #ffffff; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{p_gcu:,}</span><br>
                <span style="color: #10b981; font-size: 11px; font-weight: 700;">↑ Controller Faults</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with m5:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">OEM Spare Parts</h4>
                <span style="color: #ffffff; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{p_oem:,}</span><br>
                <span style="color: #10b981; font-size: 11px; font-weight: 700;">↑ Spares Required</span>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with m6:
      st.markdown(
          f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.3); padding: 14px 16px; border-radius: 8px;">
                <h4 style="color: #facc15 !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin: 0 0 6px 0;">Total Master Base</h4>
                <span style="color: #ffffff; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{tot_master_base:,}</span><br>
                <span style="color: #10b981; font-size: 11px; font-weight: 700;">↑ Circle Base</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")
    with st.container(border=True):
      st.markdown(
          f"<h4 style='margin:0 0 10px 0; color: #facc15; border-bottom: 2px"
          f" solid #facc15; padding-bottom: 6px;'>📊 JC-Wise vs Problem Bucket"
          f" Count Breakdown (Date: {selected_date_filter})</h4>",
          unsafe_allow_html=True,
      )
      if (
          "JC" in filtered_date_df.columns
          and "Bucket" in filtered_date_df.columns
          and not filtered_date_df.empty
      ):
        st.dataframe(
            pd.crosstab(
                filtered_date_df["JC"],
                filtered_date_df["Bucket"],
                margins=True,
                margins_name="Total",
            ),
            use_container_width=True,
        )
      else:
        st.info("No records matching current filters.")

    with st.container(border=True):
      st.markdown(
          "<h4 style='margin:0 0 10px 0; color: #facc15; border-bottom: 2px"
          " solid #facc15; padding-bottom: 6px;'>📋 Detailed Filtered Faults"
          " Registry</h4>",
          unsafe_allow_html=True,
      )
      st.dataframe(filtered_date_df, use_container_width=True)
  else:
    st.info("No data available.")

elif page == "📈 ILA-AG1 Operations Tracker":
  st.markdown("## 📈 ILA-AG1 Operations Tracker & Telemetry")
  if not df_ila.empty:
    st.dataframe(df_ila, use_container_width=True)
  else:
    st.info("ILA Tracker sheet not loaded.")

elif page == "✏️ In-Portal Master Tracker Editor":
  st.markdown("## ✏️ In-Portal Master Tracker Editor")
  edited_grid = st.data_editor(
      df_status, use_container_width=True, height=500, disabled=not is_admin
  )
  if is_admin and st.button("Save Grid Changes", type="primary"):
    st.session_state.master_tracker_df = edited_grid
    st.success("Changes saved for current session!")
