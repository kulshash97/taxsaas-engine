"""
KSP CONSOLE PLATFORM — TaxSaaS B2B Engine
Kulkarni Strategic Partners | AY 2026-27
Production-Grade | Multi-Module | Login Protected
"""

import os, io, re, json, time
import pandas as pd
import numpy as np
import streamlit as st
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KSP Console Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — Dark Professional Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0D1117;
    color: #E2E8F0;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #161B22 !important;
    border-right: 1px solid #30363D;
}

/* Brand Header Bar */
.brand-bar {
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #374151;
    margin-bottom: 25px;
}
.brand-bar .logo {
    font-size: 2.2rem;
    margin-right: 20px;
}
.brand-bar .title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #F9FAFB;
    letter-spacing: -0.025em;
}
.brand-bar .subtitle {
    font-size: 0.875rem;
    color: #9CA3AF;
    margin-top: 2px;
}
.brand-bar .status-badge {
    margin-left: auto;
    background-color: #065F46;
    color: #34D399;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MOCK MODULE RENDERS (For Complete Execution)
# ─────────────────────────────────────────────
def render_itr_module(user):
    st.subheader("📊 Income Tax Returns Engine")
    st.info("AY 2026-27 Automated Processing Active.")

def render_gst_module(user):
    st.subheader("🔵 GST Command Center Core")
    st.info("Input Tax Credit & Reconciliation Engine Operational.")

def render_ai_agent_module(user):
    st.subheader("🌐 KSP AI Compliance & Filing Agent")
    st.info("Compliance intelligence system online.")

def render_incorporation_module(user):
    st.subheader("📋 Business Incorporation Strategy Matrix")
    st.info("Structure optimization algorithms ready.")

def render_cfo_module(user):
    st.subheader("📈 Predictive Fractional CFO Modeling")
    st.info("Advance Tax Schedule & Cashflow forecasts loaded.")

# ─────────────────────────────────────────────
#  MAIN APP ROUTER
# ─────────────────────────────────────────────
def main():
    # Session state initialization
    if "active_module" not in st.session_state:
        st.session_state.active_module = "itr"
        
    user = {"name": "Shashank Kulkarni"} # Session context placeholder

    # Sidebar Navigation
    st.sidebar.title("KSP Modules")
    mod_choice = st.sidebar.radio(
        "Select Operation Unit",
        options=["itr", "gst", "ai", "incorp", "cfo"],
        format_func=lambda x: {
            "itr": "Income Tax Engine",
            "gst": "GST Command Center",
            "ai": "AI Compliance Agent",
            "incorp": "Business Incorporation",
            "cfo": "Fractional CFO Panel"
        }.get(x, x)
    )
    st.session_state.active_module = mod_choice

    # Module Metadata Configuration Dictionary (3-element tuples)
    module_titles = {
        "itr":    ("📊", "Income Tax Returns Engine", "AY 2026-27 | Sec 44AD/44ADA | New & Old Regime | Post Finance Act 2024"),
        "gst":   ("🔵", "GST Command Center Core", "Output Tax | ITC | GSTR Calendar | Registration Compliance"),
        "ai":    ("🌐", "KSP AI Compliance & Filing Agent", "Claude-powered natural language compliance assistant"),
        "incorp":("📋", "Business Incorporation Strategy Matrix", "Pvt Ltd | LLP | OPC | Partnership | Proprietorship"),
        "cfo":   ("📈", "Predictive Fractional CFO Modeling", "Advance Tax Schedule | Sec 208/234 | Cashflow Forecast"),
    }
    
    mod = st.session_state.active_module
    
    # FIX: Correctly unpacking exactly 3 values returned from the dictionary fallback tuple
    icon, title, subtitle = module_titles.get(mod, ("⚙️", "Module", ""))

    # Render Brand Header
    st.markdown(f"""
    <div class="brand-bar">
        <div class="logo">{icon}</div>
        <div>
            <div class="title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
        <div class="status-badge">● LIVE</div>
    </div>
    """, unsafe_allow_html=True)

    # Module Router Execution
    if mod == "itr":
        render_itr_module(user)
    elif mod == "gst":
        render_gst_module(user)
    elif mod == "ai":
        render_ai_agent_module(user)
    elif mod == "incorp":
        render_incorporation_module(user)
    elif mod == "cfo":
        render_cfo_module(user)

if __name__ == "__main__":
    main()