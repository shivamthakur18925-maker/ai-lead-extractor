import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro", page_icon="🚀", layout="wide")

st.title("🚀 AI Lead Extractor Pro")
st.caption("Real-time B2B Lead Extraction System")

# ---------------------------------------------------------
# Admin & Temp-Mail Security
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]
BLOCKED_DOMAINS = ["tempmail.com", "yopmail.com", "guerrillamail.com", "gwshare.com", "mailinator.com", "trashmail.com"]

def is_temp_email(email):
    email = email.strip().lower()
    if "@" not in email:
        return True
    domain = email.split("@")[-1]
    return any(b in domain for b in BLOCKED_DOMAINS)

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "credits" not in st.session_state:
    st.session_state["credits"] = 30

# ---------------------------------------------------------
# Login UI
# ---------------------------------------------------------
if not st.session_state["user_email"]:
    st.subheader("🔑 Access Lead Extractor")
    email_input = st.text_input("Enter Email Address:", placeholder="name@company.com")
    if st.button("Start Extractor"):
        if not email_input:
            st.error("Please enter your email.")
        elif is_temp_email(email_input):
            st.error("⚠️ Temporary/Disposable emails are strictly blocked!")
        else:
            st.session_state["user_email"] = email_input.strip().lower()
            st.session_state["credits"] = 999999 if st.session_state["user_email"] in ADMIN_EMAILS else 30
            st.rerun()
    st.stop()

# Header
user_email = st.session_state["user_email"]
is_admin = user_email in ADMIN_EMAILS

c1, c2 = st.columns([3, 1])
c1.write(f"Account: **{user_email}**")
c2.success("👑 Unlimited (Admin)") if is_admin else c2.info(f"⚡ Credits: {st.session_state['credits']}")
st.divider()

# ---------------------------------------------------------
# Fast Single Key Selector (Prevents Timeout)
# ---------------------------------------------------------
def get_active_google_key():
    # Priority order check
    for i in range(1, 7):
        try:
            k = st.secrets.get(f"PLACES_API_KEY_{i}")
            if k and len(k) > 10 and "AIzaSy" in k:
                return k
        except Exception:
            pass
    return None

# ---------------------------------------------------------
# Lead Search Function
# ---------------------------------------------------------
def search_leads(category, location, limit=5):
    key = get_active_google_key()
    
    if not key:
        st.error("❌ Secrets Error: Streamlit Secrets mein PLACES_API_KEY_1 nahi mil rahi hai.")
        return None

    # Standard Google Text Search Endpoint
    query = f"{category} in {location}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(query)}&key={key}"
    
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        
        status = data.get("status")
        
        if status == "OK":
            results = data.get("results", [])[:limit]
            leads_data = []
            for item in results:
                name = item.get("name", "N/A")
                address = item.get("formatted_address", "N/A")
                rating = item.get("rating", "N/A")
                place_id = item.get("place_id")
                
                # Fetch Phone Number using Place Details
                phone = "N/A"
                wa_link = "N/A"
                if place_id:
                    det_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number&key={key}"
                    d_data = requests.get(det_url, timeout=5).json()
                    if d_data.get("status") == "OK":
                        phone = d_data.get("result", {}).get("formatted_phone_number", "N/A")
                        clean_p = "".join(filter(str.isdigit, str(phone)))
                        if len(clean_p) >= 10:
                            wa_link = f"https://wa.me/91{clean_p[-10:]}"

                leads_data.append({
                    "Business Name": name,
                    "Category": category,
                    "Location": address,
                    "Phone Number": phone,
                    "Rating": rating,
                    "Direct WhatsApp": wa_link
                })
            return leads_data
        else:
            # Show exact Google Error
            st.error(f"⚠️ Google API Status: {status}")
            if "error_message" in data:
                st.warning(f"Google Message: {data['error_message']}")
            return None

    except Exception as e:
        st.error(f"Network Connection Error: {e}")
        return None

# ---------------------------------------------------------
# Main UI Inputs
# ---------------------------------------------------------
st.subheader("🔍 Search & Extract Real B2B Leads")

col1, col2 = st.columns(2)
with col1:
    category_in = st.text_input("🏢 Business Sector/Category:", placeholder="e.g. Gym, Real Estate, Restaurant")
with col2:
    location_in = st.text_input("📍 Target City/Location:", placeholder="e.g. Bangalore, Delhi, Patna")

num_leads = st.number_input("Number of Leads:", min_value=1, max_value=20, value=5)

if st.button("🚀 Extract Real Leads Now"):
    if not category_in or not location_in:
        st.warning("Please fill both Category and Location.")
    else:
        with st.spinner("Fetching Live Leads from Google Maps..."):
            results = search_leads(category_in, location_in, limit=num_leads)
            
            if results:
                if not is_admin:
                    st.session_state["credits"] = max(0, st.session_state["credits"] - len(results))
                
                st.success(f"Extracted {len(results)} verified leads for '{category_in}' in '{location_in}'!")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # CSV Download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Leads CSV", csv, f"{category_in}_{location_in}.csv", "text/csv")
