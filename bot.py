import streamlit as st
import requests
import json
import pandas as pd
import re

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro", page_icon="🚀", layout="wide")

st.title("🚀 AI Lead Extractor Pro")
st.caption("Ultra-Fast B2B Lead Extraction powered by Groq AI Engine")

# ---------------------------------------------------------
# Security & Email Constraints
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]
BLOCKED_DOMAINS = [
    "tempmail.com", "yopmail.com", "guerrillamail.com", "gwshare.com", 
    "mailinator.com", "trashmail.com", "10minutemail.com", "dispostable.com"
]

def is_temp_email(email):
    email = email.strip().lower()
    if "@" not in email:
        return True
    domain = email.split("@")[-1]
    return any(b in domain for b in BLOCKED_DOMAINS)

# ---------------------------------------------------------
# Session State Management
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "credits" not in st.session_state:
    st.session_state["credits"] = 30

# ---------------------------------------------------------
# Login System
# ---------------------------------------------------------
if not st.session_state["user_email"]:
    st.subheader("🔑 Access Lead Extractor Engine")
    email_input = st.text_input("Enter your official Email Address:", placeholder="name@company.com")
    
    if st.button("Start Using Tool"):
        if not email_input:
            st.error("Please enter a valid email address.")
        elif is_temp_email(email_input):
            st.error("⚠️ Temporary / Disposable emails are strictly restricted for security reasons!")
        else:
            cleaned_email = email_input.strip().lower()
            st.session_state["user_email"] = cleaned_email
            if cleaned_email in ADMIN_EMAILS:
                st.session_state["credits"] = 999999
            else:
                st.session_state["credits"] = 30
            st.rerun()
    st.stop()

# User Header Banner
user_email = st.session_state["user_email"]
is_admin = user_email in ADMIN_EMAILS

c1, c2 = st.columns([3, 1])
c1.write(f"Logged in as: **{user_email}**")
if is_admin:
    c2.success("👑 Admin Access (Unlimited)")
else:
    c2.info(f"⚡ Available Credits: {st.session_state['credits']}")
st.divider()

# ---------------------------------------------------------
# Groq Multi-Key Selector (Zero Billing Risk)
# ---------------------------------------------------------
def get_groq_key():
    for i in range(1, 7):
        try:
            key = st.secrets.get(f"GROQ_API_KEY_{i}")
            if key and len(key) > 10 and key.startswith("gsk_"):
                return key
        except Exception:
            pass
    # Fallback default key check
    return st.secrets.get("GROQ_API_KEY", None)

# ---------------------------------------------------------
# Groq AI B2B Data Engine
# ---------------------------------------------------------
def extract_leads_via_groq(category, location, limit=5):
    groq_key = get_groq_key()
    
    if not groq_key:
        st.error("❌ Groq API Key missing! Please check GROQ_API_KEY_1 in Streamlit Secrets.")
        return None

    prompt = f"""
    Act as a professional B2B Data Extractor and Market Researcher.
    Extract exactly {limit} real or highly accurate, verified B2B leads for business category '{category}' in location '{location}'.

    For each business, provide:
    1. Business Name
    2. Full Address/Location
    3. Contact Phone Number (Indian standard format with +91 if in India)
    4. Official Email Address
    5. Instagram Username/Handle (e.g. @business_name)

    Return ONLY a raw JSON array of objects with the exact keys:
    "business_name", "address", "phone", "email", "instagram"
    Do not include markdown code block formatting or extra conversational text.
    """

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            res_data = response.json()
            raw_content = res_data['choices'][0]['message']['content'].strip()
            
            # Clean JSON Response
            raw_content = re.sub(r'```json\s*|\s*```', '', raw_content)
            leads_json = json.loads(raw_content)
            
            formatted_leads = []
            for item in leads_json[:limit]:
                phone = item.get("phone", "N/A")
                clean_phone = re.sub(r'\D', '', str(phone))
                
                # Generate Direct WhatsApp Link
                wa_link = "N/A"
                if len(clean_phone) >= 10:
                    wa_link = f"https://wa.me/91{clean_phone[-10:]}"

                # Generate Direct Instagram Link
                insta = item.get("instagram", "N/A")
                insta_link = "N/A"
                if insta and insta != "N/A":
                    clean_insta = str(insta).replace("@", "").strip()
                    insta_link = f"https://instagram.com/{clean_insta}"

                formatted_leads.append({
                    "Business Name": item.get("business_name", "N/A"),
                    "Category": category,
                    "Location": item.get("address", "N/A"),
                    "Phone Number": phone,
                    "Email Address": item.get("email", "N/A"),
                    "Direct WhatsApp": wa_link,
                    "Instagram Profile": insta_link
                })
            return formatted_leads
        else:
            st.error(f"Groq API Error Status: {response.status_code}")
            st.write(response.text)
            return None
    except Exception as e:
        st.error(f"Execution Error: {e}")
        return None

# ---------------------------------------------------------
# Main UI Inputs
# ---------------------------------------------------------
st.subheader("🔍 Search & Extract Live B2B Leads")

col1, col2 = st.columns(2)
with col1:
    category_in = st.text_input("🏢 Business Sector/Category:", placeholder="e.g. Gym, Real Estate, Restaurant")
with col2:
    location_in = st.text_input("📍 Target City/Location:", placeholder="e.g. Patna, Bangalore, Delhi")

num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=20, value=5)

if st.button("🚀 Extract Real Leads Now"):
    if not category_in or not location_in:
        st.warning("Please fill both Business Category and Target Location.")
    elif not is_admin and st.session_state["credits"] < num_leads:
        st.error("⚠️ Insufficient Credits! Please contact administrator for more credits.")
    else:
        with st.spinner("Extracting Leads via Groq AI Engine..."):
            results = extract_leads_via_groq(category_in, location_in, limit=num_leads)
            
            if results:
                if not is_admin:
                    st.session_state["credits"] = max(0, st.session_state["credits"] - len(results))
                
                st.success(f"Successfully Extracted {len(results)} Leads for '{category_in}' in '{location_in}'!")
                df = pd.DataFrame(results)
                
                # Display Interactive Table
                st.dataframe(
                    df,
                    column_config={
                        "Direct WhatsApp": st.column_config.LinkColumn("WhatsApp Chat", display_text="💬 Chat on WA"),
                        "Instagram Profile": st.column_config.LinkColumn("Instagram", display_text="📸 View Profile")
                    },
                    use_container_width=True
                )
                
                # CSV Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Leads as CSV File",
                    data=csv,
                    file_name=f"{category_in}_{location_in}_leads.csv",
                    mime="text/csv"
                )
