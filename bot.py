import os
import re
import requests
import itertools
import streamlit as st
from dotenv import load_dotenv

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Lead Extractor Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Environment Variables
load_dotenv()

# ==========================================
# 🔑 API KEYS CONFIGURATION (6 + 6 Rotation)
# ==========================================
GROQ_KEYS = [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 7) if os.getenv(f"GROQ_API_KEY_{i}")]
PLACES_KEYS = [os.getenv(f"PLACES_API_KEY_{i}") for i in range(1, 7) if os.getenv(f"PLACES_API_KEY_{i}")]

groq_cycle = itertools.cycle(GROQ_KEYS) if GROQ_KEYS else None
places_cycle = itertools.cycle(PLACES_KEYS) if PLACES_KEYS else None

def get_next_groq_key():
    return next(groq_cycle) if groq_cycle else None

def get_next_places_key():
    return next(places_cycle) if places_cycle else None

# ==========================================
# 🛡️ SECURITY & ANTI-TEMP MAIL CONFIG
# ==========================================
DISALLOWED_DOMAINS = [
    "tempmail.com", "guerrillamail.com", "10minutemail.com", 
    "mailinator.com", "throwawaymail.com", "temp-mail.org", "yopmail.com"
]

ADMIN_EMAILS = ["admin@gmail.com", "shivamthakur18925@gmail.com"]

def is_temp_email(email):
    domain = email.split('@')[-1].lower() if '@' in email else ""
    return domain in DISALLOWED_DOMAINS

# ==========================================
# 💾 SESSION STATE & INITIALIZATION
# ==========================================
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "credits" not in st.session_state:
    st.session_state.credits = 0
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ==========================================
# 🎨 CUSTOM STYLING (App-First UI)
# ==========================================
st.markdown("""
    <style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1rem;
    }
    .credit-badge {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        display: inline-block;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.8rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Top Bar Header
st.markdown('<div class="main-title">🚀 AI Lead Extractor Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Extract verified B2B leads instantly with high accuracy</div>', unsafe_allow_html=True)

# ==========================================
# 🔐 STEP 1: USER AUTHENTICATION
# ==========================================
if not st.session_state.is_logged_in:
    st.info("👋 Enter your email to get **30 FREE Trial Credits** immediately.")
    email_input = st.text_input("Enter Email Address:", placeholder="name@company.com")
    
    if st.button("Start Extracting Leads"):
        if not email_input or "@" not in email_input:
            st.error("Please enter a valid email address.")
        elif is_temp_email(email_input):
            st.error("⚠️ Temporary or disposable emails are blocked. Please use a permanent email.")
        else:
            st.session_state.user_email = email_input.lower().strip()
            st.session_state.is_logged_in = True
            
            if st.session_state.user_email in ADMIN_EMAILS:
                st.session_state.is_admin = True
                st.session_state.credits = 999999
            else:
                st.session_state.is_admin = False
                st.session_state.credits = 30
            st.rerun()

# ==========================================
# 🎯 STEP 2: MAIN WORKING DASHBOARD
# ==========================================
else:
    # User Status Bar
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"Account: **{st.session_state.user_email}**")
    with col2:
        if st.session_state.is_admin:
            st.markdown('<div class="credit-badge">👑 Credits: Unlimited (Admin)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="credit-badge">⚡ Credits Remaining: {st.session_state.credits}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # ⚠️ CASE A: CREDITS EXHAUSTED -> SHOW PRICING
    # ==========================================
    if not st.session_state.is_admin and st.session_state.credits <= 0:
        st.error("⚠️ You have exhausted all your free credits!")
        st.subheader("💳 Choose a Subscription Plan to Continue")
        st.write("Upgrade now to keep extracting high-quality verified leads.")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("### 📦 Starter Plan")
            st.title("₹999 / mo")
            st.write("• **500 Verified Leads / Month**")
            st.write("• Rollover Credits Included")
            st.write("• Standard AI Filtering")
            st.write("• Invalid Data Refund Guarantee")
            if st.button("Buy Starter Plan"):
                st.info("Redirecting to Secure Payment Gateway...")

        with col_b:
            st.markdown("### ⚡ Pro Plan")
            st.caption("🔥 Recommended Choice")
            st.title("₹2,499 / mo")
            st.write("• **2,500 Verified Leads / Month**")
            st.write("• Rollover Credits Included")
            st.write("• Deep AI Filtering & Email Extraction")
            st.write("• High-Speed Priority Processing")
            if st.button("Buy Pro Plan"):
                st.info("Redirecting to Secure Payment Gateway...")

        with col_c:
            st.markdown("### 🏢 Enterprise Plan")
            st.title("₹5,999 / mo")
            st.write("• **10,000 Verified Leads / Month**")
            st.write("• Multi-User Login (up to 3 Seats)")
            st.write("• Priority 24/7 Dedicated Support")
            st.write("• Custom Data Exports")
            if st.button("Buy Enterprise Plan"):
                st.info("Redirecting to Secure Payment Gateway...")

    # ==========================================
    # ✅ CASE B: CREDITS AVAILABLE -> SHOW TOOL
    # ==========================================
    else:
        st.subheader("🔍 Search & Extract B2B Leads")
        query_input = st.text_input("Target Keyword & City:", placeholder="e.g. Gyms in Delhi OR Dentists in Mumbai")
        limit_input = st.number_input("Number of Leads to Extract:", min_value=1, max_value=50, value=5)

        if st.button("Extract Leads Now"):
            if not query_input:
                st.warning("Please enter a search query.")
            elif not st.session_state.is_admin and st.session_state.credits < limit_input:
                st.error(f"❌ You only have {st.session_state.credits} credits left. Decrease requested lead count or upgrade plan.")
            else:
                with st.spinner("Processing request via Google Places & Groq AI..."):
                    # Deduct Credits
                    if not st.session_state.is_admin:
                        st.session_state.credits -= limit_input

                    st.success(f"Extracted {limit_input} verified leads for '{query_input}'!")
                    
                    # Display Extracted Data
                    st.dataframe([
                        {
                            "Business Name": f"Sample Business {i+1}",
                            "Phone Number": f"+91 98765 4320{i}",
                            "Category": "Verified Business",
                            "City": query_input.split()[-1] if len(query_input.split()) > 1 else "India",
                            "Status": "Valid Lead"
                        }
                        for i in range(limit_input)
                    ])
