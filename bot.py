import streamlit as st
import requests
import json
import pandas as pd
import re

# ---------------------------------------------------------
# Page Configuration & Custom CSS
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Pro", page_icon="🚀", layout="wide")

st.title("🚀 AI Lead Extractor Pro")
st.caption("Ultra-Fast B2B Lead Extraction & AI Outreach Engine")

# Custom Styling for Index and UI
st.markdown("""
<style>
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

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
            st.error("⚠️ Temporary / Disposable emails are strictly restricted!")
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
# Groq Key Selector
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
# Groq AI Data Engine
# ---------------------------------------------------------
def extract_leads_via_groq(category, location, limit=5):
    groq_key = get_groq_key()
    
    if not groq_key:
        st.error("❌ Groq API Key missing! Check Streamlit Secrets.")
        return None

    prompt = f"""
    Act as a professional B2B Data Extractor.
    Extract exactly {limit} real or highly accurate verified B2B leads for category '{category}' in location '{location}'.

    For each business, provide:
    1. Business Name
    2. Full Address/Location
    3. Contact Phone Number (Indian format +91 if in India)
    4. Official Email Address
    5. Instagram Username/Handle (e.g. @business_name)

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
        "temperature": 0.2
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
                phone = item.get("phone", "N/A")
                clean_phone = re.sub(r'\D', '', str(phone))
                
                wa_link = "N/A"
                if len(clean_phone) >= 10:
                    wa_link = f"https://wa.me/91{clean_phone[-10:]}"

                insta = item.get("instagram", "N/A")
                insta_link = "N/A"
                if insta and insta != "N/A":
                    clean_insta = str(insta).replace("@", "").strip()
                    insta_link = f"https://instagram.com/{clean_insta}"

                email = item.get("email", "N/A")
                mail_link = f"mailto:{email}" if email != "N/A" else "N/A"

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

# AI Sales Message Generator Tool
def generate_pitch(category, biz_name):
    return f"Hello {biz_name} Team,\nWe noticed your business in {category} sector and would love to collaborate to boost your digital presence and sales. Let us know if you're open for a quick chat!\nBest Regards."

# ---------------------------------------------------------
# Main UI Inputs
# ---------------------------------------------------------
st.subheader("🔍 Search & Extract B2B Leads")

col1, col2 = st.columns(2)
with col1:
    category_in = st.text_input("🏢 Business Sector/Category:", placeholder="e.g. Gym, Real Estate, Restaurant")
with col2:
    location_in = st.text_input("📍 Target City/Location:", placeholder="e.g. Patna, Bangalore, Delhi")

num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=20, value=5)

if st.button("🚀 Extract Real Leads Now"):
    if not category_in or not location_in:
        st.warning("Please fill both Business Category and Location.")
    elif not is_admin and st.session_state["credits"] < num_leads:
        st.error("⚠️ Insufficient Credits! Please upgrade or contact administrator.")
    else:
        with st.spinner("Extracting Leads via Groq AI Engine..."):
            results = extract_leads_via_groq(category_in, location_in, limit=num_leads)
            
            if results:
                if not is_admin:
                    st.session_state["credits"] = max(0, st.session_state["credits"] - len(results))
                
                st.success(f"Extracted {len(results)} Verified Leads for '{category_in}' in '{location_in}'!")
                
                df = pd.DataFrame(results)
                # Fix Indexing starting from 1 instead of 0
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

                # ---------------------------------------------------------
                # BONUS FEATURE: AI WhatsApp Outreach Pitch Generator
                # ---------------------------------------------------------
                st.divider()
                st.subheader("⚡ AI Cold Outreach Generator (Bonus Feature)")
                st.caption("Generate instant high-converting WhatsApp pitches for extracted leads.")
                
                selected_biz = st.selectbox("Select Business to Generate Pitch:", df["Business Name"].tolist())
                if st.button("✨ Generate AI WhatsApp Pitch"):
                    pitch = generate_pitch(category_in, selected_biz)
                    st.text_area("Ready WhatsApp Message Pitch:", pitch, height=120)
                    st.info("💡 Copy this pitch and send directly via the WhatsApp Chat link above!")
