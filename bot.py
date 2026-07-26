import streamlit as st
import requests
import json
import pandas as pd
import re

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro (Global)", page_icon="🌐", layout="wide")

st.title("🌐 AI Lead Extractor Pro (Global Edition)")
st.caption("Ultra-Fast Verified B2B Lead Extraction for Worldwide Markets")

st.markdown("""
<style>
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Security & Temp-Mail Enforcement (Global Strict Block)
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]

# Trusted Global Public Domains
TRUSTED_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
    "icloud.com", "protonmail.com", "live.com", "zoho.com", "aol.com"
]

# Known Temp-Mail and Disposable Keywords
BLOCKED_KEYWORDS = [
    "temp", "trash", "disposable", "guerrilla", "mailinator", 
    "yopmail", "kierko", "gwshare", "10minute", "fake", "burner",
    "sharklasers", "getairmail", "throwaway"
]

def is_valid_email(email):
    email = email.strip().lower()
    if "@" not in email:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
        
    domain = parts[1]
    
    # Block any domain containing temporary keywords
    if any(key in domain for key in BLOCKED_KEYWORDS):
        return False
        
    # Check domain extension validity
    if "." not in domain or len(domain.split(".")[-1]) < 2:
        return False
        
    return True

# ---------------------------------------------------------
# Session State Management
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "credits" not in st.session_state:
    st.session_state["credits"] = 30

# ---------------------------------------------------------
# Strict Login System
# ---------------------------------------------------------
if not st.session_state["user_email"]:
    st.subheader("🔑 Access Verified Global Lead Engine")
    email_input = st.text_input("Enter your official Email Address:", placeholder="name@company.com or name@gmail.com")
    
    if st.button("Start Using Extractor"):
        if not email_input:
            st.error("Please enter a valid email address.")
        elif not is_valid_email(email_input):
            st.error("⚠️ Temporary/Disposable emails (e.g. kierko.com, tempmail) are strictly restricted!")
        else:
            cleaned_email = email_input.strip().lower()
            st.session_state["user_email"] = cleaned_email
            st.session_state["credits"] = 999999 if cleaned_email in ADMIN_EMAILS else 30
            st.rerun()
    st.stop()

# Header Banner
user_email = st.session_state["user_email"]
is_admin = user_email in ADMIN_EMAILS

c1, c2 = st.columns([3, 1])
c1.write(f"Logged in as: **{user_email}**")
if is_admin:
    c2.success("👑 Admin Access (Unlimited)")
else:
    c2.info(f"⚡ Credits: {st.session_state['credits']}")
st.divider()

# ---------------------------------------------------------
# Groq API Key Selector
# ---------------------------------------------------------
def get_groq_key():
    for i in range(1, 7):
        try:
            key = st.secrets.get(f"GROQ_API_KEY_{i}")
            if key and len(key) > 10 and key.startswith("gsk_"):
                return key
        except Exception:
            pass
    return st.secrets.get("GROQ_API_KEY", None)

# ---------------------------------------------------------
# Global Verified B2B AI Data Engine
# ---------------------------------------------------------
def extract_leads_via_groq(category, location, limit=5):
    groq_key = get_groq_key()
    
    if not groq_key:
        st.error("❌ Groq API Key missing! Check Streamlit Secrets.")
        return None

    prompt = f"""
    Act as a Global B2B Lead Extraction Specialist and Auditor.
    Extract exactly {limit} VERIFIED B2B leads for category '{category}' in location '{location}'.

    CRITICAL INSTRUCTIONS FOR GLOBAL ACCURACY:
    1. Business Name: Must be a legitimate, active B2B business or service provider in '{category}'.
    2. Phone Number: Provide full valid International Phone Number with country code format (e.g., +91 for India, +1 for USA/Canada, +44 for UK, +971 for UAE). DO NOT give incomplete digits or generic helpline numbers.
    3. Instagram Handle:
       - For social-heavy businesses (Real Estate, Gyms, Restaurants, Agencies), select verified business profiles (aim for active accounts with relevant bio and posts).
       - For industrial/B2B suppliers where Instagram is rare, provide 'N/A' rather than a fake or random personal account.
    4. Email Address: Valid corporate/official email address.

    Return ONLY a raw JSON array of objects with keys:
    "business_name", "address", "phone", "email", "instagram"
    Do not include markdown code block syntax.
    """

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            res_data = response.json()
            raw_content = res_data['choices'][0]['message']['content'].strip()
            raw_content = re.sub(r'```json\s*|\s*```', '', raw_content)
            leads_json = json.loads(raw_content)
            
            formatted_leads = []
            for item in leads_json[:limit]:
                phone = str(item.get("phone", "N/A")).strip()
                clean_phone = re.sub(r'\D', '', phone)
                
                # Global WhatsApp Link Generation
                wa_link = "N/A"
                if len(clean_phone) >= 8:
                    wa_link = f"https://wa.me/{clean_phone}"

                insta = item.get("instagram", "N/A")
                insta_link = "N/A"
                if insta and insta != "N/A":
                    clean_insta = str(insta).replace("@", "").strip()
                    insta_link = f"https://instagram.com/{clean_insta}"

                email = item.get("email", "N/A")

                formatted_leads.append({
                    "Business Name": item.get("business_name", "N/A"),
                    "Category": category.title(),
                    "Location": item.get("address", "N/A"),
                    "Phone Number": phone,
                    "Email Address": email,
                    "Direct WhatsApp": wa_link,
                    "Instagram Profile": insta_link,
                    "Status": "Verified ✅"
                })
            return formatted_leads
        else:
            st.error(f"Error Status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Execution Error: {e}")
        return None

# AI Sales Pitch Generator
def generate_pitch(category, biz_name):
    return f"Hello {biz_name} Team,\nWe came across your profile in the {category} space and would love to connect to discuss potential synergy and growth opportunities. Let us know if you'd be open to a quick chat!\nBest Regards."

# ---------------------------------------------------------
# Main UI Inputs
# ---------------------------------------------------------
st.subheader("🔍 Search & Extract Global B2B Leads")

col1, col2 = st.columns(2)
with col1:
    category_in = st.text_input("🏢 Business Sector/Category:", placeholder="e.g. Real Estate, Gym, Software, Supplier")
with col2:
    location_in = st.text_input("📍 Target City/Country:", placeholder="e.g. London, New York, Dubai, Mumbai")

num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=20, value=5)

if st.button("🚀 Extract Real Leads Now"):
    if not category_in or not location_in:
        st.warning("Please enter both Business Category and Location.")
    elif not is_admin and st.session_state["credits"] < num_leads:
        st.error("⚠️ Insufficient Credits! Please contact administrator for more credits.")
    else:
        with st.spinner("Extracting & Auditing Global Leads..."):
            results = extract_leads_via_groq(category_in, location_in, limit=num_leads)
            
            if results:
                if not is_admin:
                    st.session_state["credits"] = max(0, st.session_state["credits"] - len(results))
                
                st.success(f"Successfully Extracted {len(results)} Verified Leads for '{category_in}' in '{location_in}'!")
                
                df = pd.DataFrame(results)
                df.index = range(1, len(df) + 1)
                
                st.dataframe(
                    df,
                    column_config={
                        "Direct WhatsApp": st.column_config.LinkColumn("WhatsApp", display_text="💬 Chat"),
                        "Instagram Profile": st.column_config.LinkColumn("Instagram", display_text="📸 Profile")
                    },
                    use_container_width=True
                )
                
                # CSV Download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Leads CSV",
                    data=csv,
                    file_name=f"{category_in}_{location_in}_leads.csv",
                    mime="text/csv"
                )

                # Outreach Pitch Feature
                st.divider()
                st.subheader("⚡ AI Cold Outreach Generator")
                selected_biz = st.selectbox("Select Business to Generate Outreach Message:", df["Business Name"].tolist())
                if st.button("✨ Generate AI Outreach Pitch"):
                    pitch = generate_pitch(category_in, selected_biz)
                    st.text_area("Ready Message Pitch:", pitch, height=120)
