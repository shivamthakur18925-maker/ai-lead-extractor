import streamlit as st
import pandas as pd
import io
import re
import hashlib
from groq import Groq

# -------------------------------------------------------------------
# 1. Page Config & CSS Branding (Dark/Light Mode Compatible)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Lead Extractor & Pro Outreach Bot",
    page_icon="🚀",
    layout="wide"
)

# Custom Styling for Pricing Cards and Dark/Light Mode Fix
st.markdown("""
    <style>
    .main-header { font-size: 2.3rem; font-weight: 800; margin-bottom: 5px; }
    .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 20px; }
    
    /* Feature Badge Styling */
    .feature-badge {
        background-color: #F1F5F9;
        color: #0F172A;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        margin-right: 10px;
        margin-bottom: 10px;
        border: 1px solid #E2E8F0;
    }

    /* Fixed Card Styles for Both Light & Dark Modes */
    .price-card {
        border: 2px solid #CBD5E1;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .price-card-popular {
        border: 2px solid #3B82F6;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        box-shadow: 0 10px 15px -3px rgba(59,130,246,0.3);
    }
    .price-card h3, .price-card-popular h3 {
        color: #60A5FA !important;
        margin-bottom: 10px;
    }
    .price-card h2, .price-card-popular h2 {
        color: #FFFFFF !important;
        margin-bottom: 15px;
    }
    .price-card p, .price-card-popular p {
        color: #94A3B8 !important;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. Temp-Mail Detection & Security Helper Functions
# -------------------------------------------------------------------
TEMP_MAIL_DOMAINS = [
    "tempmail", "10minutemail", "guerrillamail", "mailinator", "throwawaymail",
    "yopmail", "sharklasers", "dispostable", "getairmail", "getnada", "temp-mail"
]

def is_temp_email(email):
    if "@" not in email:
        return True
    domain = email.split("@")[1].lower()
    for temp in TEMP_MAIL_DOMAINS:
        if temp in domain:
            return True
    return False

# Session States Initialization
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_credits" not in st.session_state:
    st.session_state.user_credits = 5
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

# -------------------------------------------------------------------
# 3. Fetch API Keys from Secrets
# -------------------------------------------------------------------
API_KEYS = [
    st.secrets.get("GROQ_API_KEY_1", ""),
    st.secrets.get("GROQ_API_KEY_2", ""),
    st.secrets.get("GROQ_API_KEY_3", "")
]

def get_groq_client():
    for key in API_KEYS:
        if key and key.startswith("gsk_"):
            try:
                return Groq(api_key=key)
            except Exception:
                continue
    first_key = next((k for k in API_KEYS if k), "")
    return Groq(api_key=first_key)

client = get_groq_client()

# -------------------------------------------------------------------
# 4. Header & Feature Highlights
# -------------------------------------------------------------------
st.markdown("<div class='main-header'>🚀 AI Lead Extractor & Pro Outreach Bot</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Turn raw internet text into structured leads and high-converting personalized outreach in seconds.</div>", unsafe_allow_html=True)

# Visual Enhancements to fill empty space
st.markdown("""
    <div style='margin-bottom: 20px;'>
        <span class='feature-badge'>⚡ 10x Faster Extraction</span>
        <span class='feature-badge'>🎯 High-Accuracy AI Parsing</span>
        <span class='feature-badge'>📩 Cold Email, WhatsApp & DMs</span>
        <span class='feature-badge'>📥 Instant CSV Export</span>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 5. Sidebar: Authentication & License Activation
# -------------------------------------------------------------------
st.sidebar.title("👤 Account & Plan Status")

if not st.session_state.user_email:
    st.sidebar.subheader("Login / Register")
    email_input = st.sidebar.text_input("Enter your Work or Personal Email:")
    
    if st.sidebar.button("Login to Start Trial", use_container_width=True):
        if not email_input or not re.match(r"[^@]+@[^@]+\.[^@]+", email_input):
            st.sidebar.error("❌ Please enter a valid email address.")
        elif is_temp_email(email_input):
            st.sidebar.error("🚨 Temporary / Disposable Emails are strictly BLOCKED!")
        else:
            st.session_state.user_email = email_input.strip().lower()
            st.session_state.user_credits = 5
            st.sidebar.success("✅ Logged in! 5 Free Credits loaded.")
            st.rerun()

else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user_email}**")
    
    if st.session_state.is_pro:
        st.sidebar.markdown("🌟 **Status:** <span style='color:#22C55E;font-weight:bold;'>PRO UNLIMITED</span>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"🎟️ **Free Credits Remaining:** `{st.session_state.user_credits} / 5`")

    # License Key Activation Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 Activate Paid License")
    license_key = st.sidebar.text_input("Enter License Key received after payment:", type="password")
    if st.sidebar.button("Activate License", use_container_width=True):
        if license_key.strip() == "SHIVAM_PRO_2026":
            st.session_state.is_pro = True
            st.sidebar.success("🎉 Pro Plan Activated!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid Key! Contact support after payment.")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user_email = ""
        st.session_state.is_pro = False
        st.rerun()

# -------------------------------------------------------------------
# 6. Main App UI Logic & Controls
# -------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    model_choice = st.selectbox(
        "Select AI Engine:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    )

with col2:
    outreach_type = st.selectbox(
        "Target Outreach Format:",
        ["Cold Email", "LinkedIn / Instagram DM", "WhatsApp Direct Message"]
    )

input_text = st.text_area(
    "Paste Raw Business Details, Website Copy, or Directory Text Here:",
    height=200,
    placeholder="Paste prospect profiles, business bio, website text, or directory listings here..."
)

# Extract Button
if st.button("⚡ Extract Leads & Generate Outreach", type="primary", use_container_width=True):
    
    if not st.session_state.user_email:
        st.warning("⚠️ Please enter your email in the sidebar first to access the tool!")
    
    elif not st.session_state.is_pro and st.session_state.user_credits <= 0:
        st.error("🚨 Free Credits Exhausted! Upgrade below to continue.")
        
    elif not input_text.strip():
        st.warning("Please paste some text first.")
        
    else:
        with st.spinner("🤖 AI is parsing leads and writing custom outreach..."):
            try:
                prompt = f"""
                Analyze the following text and extract potential business leads.
                Extract:
                1. Company/Person Name
                2. Niche/Industry
                3. Key Problem/Pain Point
                4. Personalized Outreach Message formatted specifically as a {outreach_type}.

                Output STRICTLY as a CSV table with commas, using exact headers:
                Name, Industry, Pain_Point, Outreach_Message

                Text:
                {input_text}
                """

                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )

                result_text = response.choices[0].message.content

                if not st.session_state.is_pro:
                    st.session_state.user_credits -= 1

                st.success("✅ Leads Extracted Successfully!")

                st.subheader("📊 Extracted Results")
                
                try:
                    clean_csv = result_text.replace("```csv", "").replace("```", "").strip()
                    df = pd.read_csv(io.StringIO(clean_csv))
                    st.dataframe(df, use_container_width=True)

                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Data as CSV / Excel",
                        data=csv_data,
                        file_name="extracted_leads.csv",
                        mime="text/csv"
                    )
                except Exception:
                    st.text(result_text)

            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------------------------------------------------
# 7. How It Works Section (Fills UI Space & Adds Trust)
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("📖 How It Works")
h_col1, h_col2, h_col3 = st.columns(3)

with h_col1:
    st.markdown("#### 1. Paste Data")
    st.caption("Paste any raw website text, social bio, or business directory content into the box.")

with h_col2:
    st.markdown("#### 2. Select Outreach")
    st.caption("Choose whether you want Cold Emails, Instagram/LinkedIn DMs, or WhatsApp Messages.")

with h_col3:
    st.markdown("#### 3. Export Leads")
    st.caption("Get structured tables with pain points and 1-click personalized messages exported to CSV.")

# -------------------------------------------------------------------
# 8. Fixed Dark/Light Mode Pricing Section
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("💳 Upgrade & Pricing Plans")

p_col1, p_col2 = st.columns(2)

with p_col1:
    st.markdown("""
        <div class='price-card'>
            <h3>Basic Plan</h3>
            <h2>₹599 <span style='font-size:14px; color:#94A3B8;'>/ month</span></h2>
            <p>✔ <b>100 Lead Extractions</b></p>
            <p>✔ Access to All AI Models</p>
            <p>✔ Cold Email, WhatsApp & Social DMs</p>
            <p>✔ CSV / Excel Data Export</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.info("📲 **To Purchase (₹599):** Send payment via UPI to **`yourupi@upi`** and submit transaction ID to get your Activation Key instantly.")

with p_col2:
    st.markdown("""
        <div class='price-card-popular'>
            <h3>🔥 Pro Unlimited</h3>
            <h2>₹999 <span style='font-size:14px; color:#94A3B8;'>/ month</span></h2>
            <p>✔ <b>UNLIMITED Lead Extractions</b></p>
            <p>✔ Full Access to All Features & Formats</p>
            <p>✔ Priority High-Speed Llama-3 AI Engine</p>
            <p>✔ Instant Activation Key</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.success("📲 **To Purchase (₹999):** Send payment via UPI to **`yourupi@upi`** and submit transaction ID to get your Activation Key instantly.")

st.caption("🔒 Payments are 100% secure. After payment, your License Key will be sent to your registered email or instant chat.")
