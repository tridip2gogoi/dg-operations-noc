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

DEFAULT_EXCEL
