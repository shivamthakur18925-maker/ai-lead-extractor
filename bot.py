import streamlit as st
import requests
import pandas as pd
import json
import re

# ---------------------------------------------------------
# Page Configuration & Title
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro", page_icon="🚀", layout="wide")

st.title("🚀 AI Lead Extractor Pro")
st.caption("Extract verified real-time B2B business leads powered by Google Places & AI")

# ---------------------------------------------------------
# Admin & Security Configuration
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]

# Comprehensive Temp Mail Domain Blocklist
BLOCKED_TEMP_DOMAINS = [
    "tempmail.com", "yopmail.com", "guerrillamail.com", "10minutemail.com",
    "gwshare.com", "mailinator.com", "trashmail.com", "dispostable.com",
    "getnada.com", "throwawaymail.com", "temp-mail.org", "sharklasers.com"
]

def is_temp_email(email):
    email = email.strip().lower()
    if "@" not in email:
        return True
    domain = email.split("@")[-1]
    for blocked in BLOCKED_TEMP_DOMAINS:
        if blocked in domain:
            return True
    return False

# ---------------------------------------------------------
# Session State & Credit Management
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

if "credits" not in st.session_state:
    st.session_state["credits"] = 30

# ---------------------------------------------------------
# Login Section
# ---------------------------------------------------------
if not st.session_state["user_email"]:
    st.subheader("🔑 Login to Access Lead Extractor")
    
    # Simple Device Fingerprint Check warning
    st.info("👋 Enter your permanent business or personal email to claim 30 Free Trial Credits.")
    
    email_input = st.text_input("Enter Email Address:", placeholder="name@company.com")
    
    if st.button("Start Extracting Leads"):
        if not email_input:
            st.error("Please enter a valid email address.")
        elif is_temp_email(email_input):
            st.error("⚠️ Temporary or disposable emails are blocked! Please use a permanent email address.")
        else:
            st.session_state["user_email"] = email_input.strip().lower()
            if st.session_state["user_email"] in ADMIN_EMAILS:
                st.session_state["credits"] = 999999
            else:
                st.session_state["credits"] = 30
            st.rerun()
    st.stop()

# ---------------------------------------------------------
# Logged-In User Header
# ---------------------------------------------------------
user_email = st.session_state["user_email"]
is_admin = user_email in ADMIN_EMAILS

col_a, col_b = st.columns([3, 1])
with col_a:
    st.write(f"Logged in as: **{user_email}**")
with col_b:
    if is_admin:
        st.success("👑 Credits: Unlimited (Admin)")
    else:
        st.info(f"⚡ Credits Remaining: {st.session_state['credits']}")

st.divider()

# ---------------------------------------------------------
# API Key Fetching (From Streamlit Secrets / Environment)
# ---------------------------------------------------------
def get_places_api_key():
    # Try fetching from secrets
    try:
        for i in range(1, 7):
            key = st.secrets.get(f"PLACES_API_KEY_{i}")
            if key and "AIzaSy" in key and "your_" not in key:
                return key
    except Exception:
        pass
    return None

# ---------------------------------------------------------
# Real Google Places Lead Extraction Logic
# ---------------------------------------------------------
def fetch_real_google_leads(category, location, limit=10):
    api_key = get_places_api_key()
    
    if not api_key:
        st.warning("⚠️ Google Places API Key not found or invalid in Secrets. Please check your Secrets configuration.")
        return []

    query = f"{category} in {location}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(query)}&key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("status") != "OK":
            st.error(f"Google API Error: {data.get('error_message', data.get('status'))}")
            return []
            
        results = data.get("results", [])[:limit]
        leads = []
        
        for item in results:
            place_id = item.get("place_id")
            name = item.get("name")
            address = item.get("formatted_address")
            rating = item.get("rating", "N/A")
            
            # Fetch Place Details for Phone Number
            phone = "N/A"
            website = "N/A"
            if place_id:
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number,website&key={api_key}"
                d_res = requests.get(details_url, timeout=5).json()
                if d_res.get("status") == "OK":
                    res_det = d_res.get("result", {})
                    phone = res_det.get("formatted_phone_number", "N/A")
                    website = res_det.get("website", "N/A")
            
            leads.append({
                "Business Name": name,
                "Category/Sector": category,
                "Phone Number": phone,
                "Location/Address": address,
                "Rating": rating,
                "Website": website,
                "Status": "Verified Real Lead"
            })
            
        return leads

    except Exception as e:
        st.error(f"Network error while fetching real leads: {e}")
        return []

# ---------------------------------------------------------
# Search Form (Separated Category & Location)
# ---------------------------------------------------------
if st.session_state["credits"] <= 0 and not is_admin:
    st.error("❌ Your free trial credits are exhausted!")
    st.subheader("💳 Choose a Plan to Upgrade:")
    c1, c2, c3 = st.columns(3)
    c1.metric("Starter Plan", "₹999", "500 Leads")
    c2.metric("Pro Plan", "₹2,499", "3,000 Leads")
    c3.metric("Enterprise Plan", "₹5,999", "Unlimited Leads")
else:
    st.subheader("🔍 Search & Extract Real B2B Leads")
    
    col1, col2 = st.columns(2)
    with col1:
        category_input = st.text_input("🏢 Business Category / Sector:", placeholder="e.g. Real Estate, Gym, Dentist, Restaurant")
    with col2:
        location_input = st.text_input("📍 Target Location / City:", placeholder="e.g. Delhi, Mumbai, Patna, New York")
        
    num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=20, value=5)
    
    if st.button("🚀 Extract Real Leads Now"):
        if not category_input or not location_input:
            st.warning("Please fill in both Category/Sector and Location fields.")
        else:
            with st.spinner("Connecting to Google Maps & Extracting Live Business Data..."):
                real_leads = fetch_real_google_leads(category_input, location_input, limit=num_leads)
                
                if real_leads:
                    # Deduct Credits for non-admin
                    if not is_admin:
                        st.session_state["credits"] = max(0, st.session_state["credits"] - len(real_leads))
                    
                    st.success(f"Successfully extracted {len(real_leads)} real verified leads for '{category_input}' in '{location_input}'!")
                    
                    df = pd.DataFrame(real_leads)
                    st.dataframe(df, use_container_width=True)
                    
                    # CSV Download Button
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Leads as CSV",
                        data=csv_data,
                        file_name=f"{category_input}_{location_input}_leads.csv",
                        mime="text/csv"
                    )
                    st.rerun()
