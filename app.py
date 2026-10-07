from datetime import date, datetime, timedelta, timezone
from io import BytesIO
import hashlib
import os
import gspread
from google.oauth2.service_account import Credentials
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

GOOGLE_SHEET_NAME = "DG Auto-Update Automation Tracker 26"
DEFAULT_EXCEL = "DG Auto-Update Automation Tracker 26.xlsx"
DEFAULT_CM_TRACKER = "CM Tracker Jio.xlsx"

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


USER_CREDENTIALS = {
    "tridip2.gogoi": {
        "password_hash": hashlib.sha256("Gogoi@6095".encode()).hexdigest(),
        "role": "Super Admin / Operations Head",
        "name": "Tridip Gogoi",
        "access": ["all"],
    },
    "ptpl": {
        "password_hash": hashlib.sha256("Rintu@2026".encode()).hexdigest(),
        "role": "NOC Viewer",
        "name": "PTPL Operations Desk",
        "access": ["read_only"],
    },
}


def verify_login(username, password):
  if username in USER_CREDENTIALS:
    if (
        hashlib.sha256(password.encode()).hexdigest()
        == USER_CREDENTIALS[username]["password_hash"]
    ):
      return USER_CREDENTIALS[username]
  return None


@st.cache_data(ttl=60)
def load_google_sheet_tracker():
  df_status = pd.DataFrame()
  try:
    if os.path.exists("credentials.json"):
      scopes = [
          "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive",
      ]
      credentials = Credentials.from_service_account_file(
          "credentials.json", scopes=scopes
      )
      gc = gspread.authorize(credentials)
      spreadsheet = gc.open(GOOGLE_SHEET_NAME)
      worksheet = (
          spreadsheet.worksheet("Automation Status")
          if "Automation Status" in [ws.title for ws in spreadsheet.worksheets()]
          else spreadsheet.sheet1
      )
      df_status = pd.DataFrame(worksheet.get_all_records())
    else:
      raise Exception("credentials.json not found in root directory")

    for col in df_status.columns:
      df_status[col] = df_status[col].astype(object)

    ac_col_name = None
    for idx, col in enumerate(df_status.columns):
      c_str = str(col).strip().upper()
      if (
          "AC" in c_str
          or "PDF" in c_str
          or "LINK" in c_str
          or "FSR" in c_str
          or idx == 28
      ):
        ac_col_name = col
        break
    if ac_col_name:
      df_status["Col AC (FSR PDF link)"] = df_status[ac_col_name].apply(
          lambda x: "" if pd.isna(x) else str(x).strip()
      )
    else:
      if "Col AC (FSR PDF link)" not in df_status.columns:
        df_status["Col AC (FSR PDF link)"] = ""

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
  except Exception as e:
    st.error(f"Google Sheet Error: {e}")
    if os.path.exists(DEFAULT_EXCEL):
      try:
        df_status = pd.read_excel(DEFAULT_EXCEL, sheet_name="Automation Status")
      except:
        pass
  return df_status


def load_ila_tracker():
  df_ila = pd.DataFrame()
  if DEFAULT_ILA and os.path.exists(DEFAULT_ILA):
    try:
      xls_ila = pd.ExcelFile(DEFAULT_ILA)
      ila_sheet = (
          "IPMS Site Automation Status"
          if "IPMS Site Automation Status" in xls_ila.sheet_names
          else xls_ila.sheet_names[0]
      )
      df_ila = pd.read_excel(xls_ila, sheet_name=ila_sheet)
      for col in df_ila.columns:
        df_ila[col] = df_ila[col].astype(object)
      if "Sap ID" in df_ila.columns:
        df_ila = df_ila[df_ila["Sap ID"].notna()]
        df_ila["Sap ID"] =
