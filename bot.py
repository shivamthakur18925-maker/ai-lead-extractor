import streamlit as st
import requests
import pandas as pd
import json

# ---------------------------------------------------------
# Page Configuration & Title
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro", page_icon="🚀", layout="wide")

st.title("🚀 AI Lead Extractor Pro")
st.caption("Extract verified real-time B2B business leads powered by Google Places API (New) & AI")

# ---------------------------------------------------------
# Admin & Security Configuration
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]

# Disposable / Temp Mail Domain Blocklist
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
# API Key Fetching (From Streamlit Secrets)
# ---------------------------------------------------------
def get_places_api_key():
    try:
        for i in range(1, 7):
            key = st.secrets.get(f"PLACES_API_KEY_{i}")
            if key and "AIzaSy" in key and "your_" not in key:
                return key
    except Exception:
        pass
    return None

# ---------------------------------------------------------
# Google Places API (New) Lead Extraction Logic
# ---------------------------------------------------------
def fetch_real_google_leads_new_api(category, location, limit=10):
    api_key = get_places_api_key()
    
    if not api_key:
        st.error("⚠️ Google Places API Key not found in Secrets. Please check your configuration.")
        return []

    # Places API (New) Endpoint
    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.rating,places.websiteUri"
    }
    
    payload = {
        "textQuery": f"{category} in {location}",
        "maxResultCount": limit
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        data = response.json()
        
        if "error" in data:
            st.error(f"Google API Error: {data['error'].get('message', 'Unknown Error')}")
            return []
            
        places = data.get("places", [])
        leads = []
        
        for item in places:
            name = item.get("displayName", {}).get("text", "N/A")
            address = item.get("formattedAddress", "N/A")
            phone = item.get("nationalPhoneNumber", "N/A")
            rating = item.get("rating", "N/A")
            website = item.get("websiteUri", "N/A")
            
            # Generate WhatsApp direct link if phone number exists
            whatsapp_link = "N/A"
            if phone != "N/A":
                clean_phone = "".join(filter(str.isdigit, str(phone)))
                if len(clean_phone) >= 10:
                    if len(clean_phone) == 10:
                        clean_phone = "91" + clean_phone
                    whatsapp_link = f"https://wa.me/{clean_phone}"

            leads.append({
                "Business Name": name,
                "Category/Sector": category,
                "Phone Number": phone,
                "Location/Address": address,
                "Rating": rating,
                "Website": website,
                "Direct WhatsApp": whatsapp_link,
                "Status": "Verified Real Lead"
            })
            
        return leads

    except Exception as e:
        st.error(f"Network error while fetching leads: {e}")
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
        location_input = st.text_input("📍 Target Location / City:", placeholder="e.g. Delhi, Bangalore, Mumbai, Patna")
        
    num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=20, value=5)
    
    if st.button("🚀 Extract Real Leads Now"):
        if not category_input or not location_input:
            st.warning("Please fill in both Category/Sector and Location fields.")
        else:
            with st.spinner("Connecting to Google Places API (New) & Extracting Live Business Data..."):
                real_leads = fetch_real_google_leads_new_api(category_input, location_input, limit=num_leads)
                
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
