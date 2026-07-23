import streamlit as st
import pandas as pd
import io
import re
import hashlib
from groq import Groq

# -------------------------------------------------------------------
# 1. Page Config & CSS Branding
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Lead Extractor & Outreach Bot",
    page_icon="🚀",
    layout="wide"
)

# Custom Styling for Branding & Pricing Cards
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0px; }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 25px; }
    .credit-badge { background-color: #E0F2FE; color: #0369A1; padding: 6px 12px; border-radius: 20px; font-weight: bold; }
    .price-card { border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center; background: #FFFFFF; }
    .price-card-popular { border: 2px solid #2563EB; border-radius: 12px; padding: 20px; text-align: center; background: #EFF6FF; }
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
    """Check if provided email belongs to a disposable email service."""
    if "@" not in email:
        return True
    domain = email.split("@")[1].lower()
    for temp in TEMP_MAIL_DOMAINS:
        if temp in domain:
            return True
    return False

def get_user_hash(email):
    """Generate unique user key."""
    return hashlib.md5(email.strip().lower().encode()).hexdigest()

# Initialize Session States
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
# 4. Header & Branding Section
# -------------------------------------------------------------------
st.markdown("<div class='main-header'>🚀 AI Lead Extractor & Pro Outreach Bot</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Extract high-converting business leads & generate personalized outreach in seconds.</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 5. Sidebar: Authentication & Subscription
# -------------------------------------------------------------------
st.sidebar.title("👤 User Account & Plan")

if not st.session_state.user_email:
    st.sidebar.subheader("Login / Register")
    email_input = st.sidebar.text_input("Enter your Work or Personal Email:")
    
    if st.sidebar.button("Login to Start Trial"):
        if not email_input or not re.match(r"[^@]+@[^@]+\.[^@]+", email_input):
            st.sidebar.error("❌ Please enter a valid email address.")
        elif is_temp_email(email_input):
            st.sidebar.error("🚨 Temporary / Disposable Emails are strictly BLOCKED! Use Gmail/Yahoo/Work email.")
        else:
            st.session_state.user_email = email_input.strip().lower()
            st.session_state.user_credits = 5
            st.sidebar.success("✅ Logged in successfully! 5 Free Credits loaded.")
            st.rerun()

else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user_email}**")
    
    if st.session_state.is_pro:
        st.sidebar.markdown("🌟 **Status:** <span style='color:green;font-weight:bold;'>PRO UNLIMITED</span>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"🎟️ **Free Credits Remaining:** `{st.session_state.user_credits} / 5`")

    # License Key Activation Option
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 Activate Pro License")
    license_key = st.sidebar.text_input("Enter License / Activation Key:", type="password")
    if st.sidebar.button("Activate Plan"):
        # Secret Key to unlock Pro for testing or paid users
        if license_key.strip() == "SHIVAM_PRO_2026":
            st.session_state.is_pro = True
            st.sidebar.success("🎉 Pro Plan Activated Successfully!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid License Key!")

    if st.sidebar.button("Logout"):
        st.session_state.user_email = ""
        st.session_state.is_pro = False
        st.rerun()

# -------------------------------------------------------------------
# 6. Main App UI Logic & Controls
# -------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    model_choice = st.selectbox(
        "Select AI Model Engine:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    )

with col2:
    outreach_type = st.selectbox(
        "Outreach Format:",
        ["Cold Email", "LinkedIn / Instagram DM", "WhatsApp Direct Message"]
    )

input_text = st.text_area(
    "Paste Raw Business Info, Website Content, or Prospect Details Here:",
    height=180,
    placeholder="Paste website text, business bio, directory info, or raw prospect details..."
)

# Extract Button
if st.button("⚡ Extract Leads & Generate Outreach", type="primary", use_container_width=True):
    
    # 1. Login Check
    if not st.session_state.user_email:
        st.warning("⚠️ Please Login with your Email in the sidebar first to access the tool!")
    
    # 2. Credit Check
    elif not st.session_state.is_pro and st.session_state.user_credits <= 0:
        st.error("🚨 Your 5 Free Credits are EXHAUSTED! Upgrade to PRO to continue extracting leads.")
        st.info("💡 Check the Upgrade Plans section below to unlock unlimited access.")
        
    # 3. Input Check
    elif not input_text.strip():
        st.warning("Please paste some text or details to analyze.")
        
    else:
        with st.spinner("🤖 AI is extracting leads and crafting personalized messages..."):
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

                # Deduct 1 credit if not PRO
                if not st.session_state.is_pro:
                    st.session_state.user_credits -= 1

                st.success("✅ Lead Extraction & Outreach Generation Completed!")

                # Display Results
                st.subheader("📊 Extracted Data & Messages")
                
                try:
                    clean_csv = result_text.replace("```csv", "").replace("```", "").strip()
                    df = pd.read_csv(io.StringIO(clean_csv))
                    st.dataframe(df, use_container_width=True)

                    # Download Options
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
                st.error(f"Error during execution: {e}")

# -------------------------------------------------------------------
# 7. Pricing & Payment Gateway Upgrade Section (Updated Plans)
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("💳 Upgrade & Pricing Plans")

p_col1, p_col2 = st.columns(2)

with p_col1:
    st.markdown("""
        <div class='price-card'>
            <h3>Basic Plan</h3>
            <h2>₹599 <span style='font-size:14px;'>/ month</span></h2>
            <p>✔ <b>100 Lead Extractions</b></p>
            <p>✔ Access to All AI Models</p>
            <p>✔ Cold Email, WhatsApp & Social DMs</p>
            <p>✔ CSV / Excel Data Export</p>
            <br>
            <a href="https://razorpay.me" target="_blank" style="background-color:#2563EB;color:white;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;">Buy Basic Plan (₹599)</a>
        </div>
    """, unsafe_allow_html=True)

with p_col2:
    st.markdown("""
        <div class='price-card-popular'>
            <h3>🔥 Pro Unlimited</h3>
            <h2>₹999 <span style='font-size:14px;'>/ month</span></h2>
            <p>✔ <b>UNLIMITED Lead Extractions</b></p>
            <p>✔ Full Access to All Features & Formats</p>
            <p>✔ Priority High-Speed Llama-3 AI Engine</p>
            <p>✔ Instant License Key Activation</p>
            <br>
            <a href="https://razorpay.me" target="_blank" style="background-color:#16A34A;color:white;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;">Buy Pro Unlimited (₹999)</a>
        </div>
    """, unsafe_allow_html=True)

st.caption("🔒 Payments are processed securely via Razorpay & UPI. After payment, enter your License Key in the sidebar to activate.")
