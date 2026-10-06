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
        padding: 12px
