import streamlit as st
import requests
import pandas as pd
import json

# ---------------------------------------------------------
# Page Configuration & Title
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro", page_icon="🚀", layout="wide")

st.title("🚀 AI Lead Extractor Pro")
st.caption("Extract verified real-time B2B business leads powered by Google Places API & AI")

# ---------------------------------------------------------
# Admin & Security Configuration
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]

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
# Session State Management
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
# API Key Fetching Engine
# ---------------------------------------------------------
def get_places_api_key():
    # Streamlit secrets fetch
    for i in range(1, 7):
        try:
            key = st.secrets.get(f"PLACES_API_KEY_{i}")
            if key and len(key) > 10:
                return key
        except Exception:
            pass
    return None

# ---------------------------------------------------------
# Robust Google Places Search Engine
# ---------------------------------------------------------
def fetch_google_leads(category, location, limit=5):
    api_key = get_places_api_key()
    
    if not api_key:
        st.error("❌ API Key Error: Streamlit Secrets mein PLACES_API_KEY nahi mili. Kripya Secrets check karein!")
        return []

    # Try Google Places Text Search (Universal Version)
    query = f"{category} in {location}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(query)}&key={api_key}"
    
    try:
        response = requests.get(url, timeout=12)
        data = response.json()
        
        status = data.get("status")
        
        # If Key restricts Legacy, auto-switch to Places (New) Endpoint
        if status == "REQUEST_DENIED" or "Legacy" in str(data.get("error_message", "")):
            url_new = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.rating,places.websiteUri"
            }
            payload = {"textQuery": query, "maxResultCount": limit}
            res_new = requests.post(url_new, headers=headers, json=payload, timeout=12).json()
            
            places = res_new.get("places", [])
            leads = []
            for p in places:
                phone = p.get("nationalPhoneNumber", "N/A")
                clean_phone = "".join(filter(str.isdigit, str(phone)))
                wa_link = f"https://wa.me/91{clean_phone[-10:]}" if len(clean_phone) >= 10 else "N/A"
                
                leads.append({
                    "Business Name": p.get("displayName", {}).get("text", "N/A"),
                    "Phone Number": phone,
                    "Location": p.get("formattedAddress", "N/A"),
                    "Rating": p.get("rating", "N/A"),
                    "Website": p.get("websiteUri", "N/A"),
                    "Direct WhatsApp": wa_link
                })
            return leads

        elif status == "OK":
            results = data.get("results", [])[:limit]
            leads = []
            for item in results:
                name = item.get("name")
                address = item.get("formatted_address")
                rating = item.get("rating", "N/A")
                
                leads.append({
                    "Business Name": name,
                    "Phone Number": "Available in CSV",
                    "Location": address,
                    "Rating": rating,
                    "Direct WhatsApp": f"https://wa.me/?text=Hello%20{requests.utils.quote(name)}"
                })
            return leads
            
        else:
            st.error(f"Google Response Error: {data.get('error_message', status)}")
            return []

    except Exception as e:
        st.error(f"Network Connection Exception: {e}")
        return []

# ---------------------------------------------------------
# Main UI Logic
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
        category_input = st.text_input("🏢 Business Category / Sector:", placeholder="e.g. Real Estate, Gym, Dentist")
    with col2:
        location_input = st.text_input("📍 Target Location / City:", placeholder="e.g. Bangalore, Delhi, Mumbai")
        
    num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=20, value=5)
    
    if st.button("🚀 Extract Real Leads Now"):
        if not category_input or not location_input:
            st.warning("Please fill in both Category and Location fields.")
        else:
            with st.spinner("Extracting Live Leads..."):
                real_leads = fetch_google_leads(category_input, location_input, limit=num_leads)
                
                if real_leads:
                    if not is_admin:
                        st.session_state["credits"] = max(0, st.session_state["credits"] - len(real_leads))
                    
                    st.success(f"Successfully fetched {len(real_leads)} leads for '{category_input}' in '{location_input}'!")
                    df = pd.DataFrame(real_leads)
                    st.dataframe(df, use_container_width=True)
                    st.rerun()
