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
                    url
