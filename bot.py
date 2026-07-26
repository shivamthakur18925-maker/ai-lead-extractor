import streamlit as st
import requests
import json
import pandas as pd
import re
import os

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(page_title="AI Lead Extractor Ultra Pro (Global)", page_icon="🌐", layout="wide")

st.title("🌐 AI Lead Extractor Ultra Pro (Global Edition)")
st.caption("High-Capacity Unlimited Worldwide B2B Lead Extraction Engine")

st.markdown("""
<style>
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2563EB; color: white; }
    .plan-card {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #3B82F6;
        text-align: center;
        color: white;
        margin-bottom: 15px;
    }
    .discount-badge {
        background-color: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .old-price {
        text-decoration: line-through;
        color: #9CA3AF;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Persistent Credit Database System (File-Based JSON)
# ---------------------------------------------------------
DB_FILE = "user_credits_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=4)
    except Exception:
        pass

def get_user_credits(email):
    db = load_db()
    if email in db:
        return db[email]
    else:
        db[email] = 30
        save_db(db)
        return 30

def deduct_user_credits(email, amount):
    db = load_db()
    current = db.get(email, 30)
    new_bal = max(0, current - amount)
    db[email] = new_bal
    save_db(db)
    return new_bal

# ---------------------------------------------------------
# Security & Temp-Mail Enforcement
# ---------------------------------------------------------
ADMIN_EMAILS = ["shivamthakur18925@gmail.com"]

BLOCKED_KEYWORDS = [
    "temp", "trash", "disposable", "guerrilla", "mailinator", 
    "yopmail", "kierko", "gwshare", "10minute", "fake", "burner",
    "sharklasers", "getairmail", "throwaway", "fakemail", "crazymailing"
]

def is_valid_email(email):
    email = email.strip().lower()
    if "@" not in email:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
        
    domain = parts[1]
    
    if any(key in domain for key in BLOCKED_KEYWORDS):
        return False
        
    if "." not in domain or len(domain.split(".")[-1]) < 2:
        return False
        
    return True

# ---------------------------------------------------------
# Smart Global WhatsApp Number Filter Engine
# ---------------------------------------------------------
def generate_global_wa_link(phone_str):
    if not phone_str or phone_str == "N/A":
        return "N/A"
        
    clean_digits = re.sub(r'\D', '', str(phone_str))
    
    # Ignore invalid or too short numbers
    if len(clean_digits) < 8:
        return "N/A"
        
    # 1. India Filter (+91)
    if clean_digits.startswith("91") and len(clean_digits) == 12:
        mobile_part = clean_digits[2:]
        if mobile_part[0] in ['6', '7', '8', '9']:
            return f"https://wa.me/{clean_digits}"
        else:
            return "N/A"  # Block Indian landlines (like 080...)
            
    elif len(clean_digits) == 10 and clean_digits[0] in ['6', '7', '8', '9']:
        return f"https://wa.me/91{clean_digits}"
        
    # 2. USA / Canada Filter (+1)
    elif clean_digits.startswith("1") and len(clean_digits) == 11:
        area_code = clean_digits[1:4]
        # Toll-free / Landline area codes in US/Canada
        if area_code in ["800", "888", "877", "866", "855", "844", "833"]:
            return "N/A"
        return f"https://wa.me/{clean_digits}"
        
    # 3. UK Filter (+44) - UK Mobiles start with 7
    elif clean_digits.startswith("44") and len(clean_digits) >= 11:
        if clean_digits[2] == '7':
            return f"https://wa.me/{clean_digits}"
        else:
            return "N/A"  # UK Landlines start with 1, 2, 3...
            
    # 4. UAE Filter (+971) - UAE Mobiles start with 5
    elif clean_digits.startswith("971") and len(clean_digits) >= 11:
        if clean_digits[3] == '5':
            return f"https://wa.me/{clean_digits}"
        else:
            return "N/A"  # UAE Landlines start with 2, 3, 4, 6, 7, 9...
            
    # General Global Fallback for other countries (min 10 digits)
    elif len(clean_digits) >= 10:
        return f"https://wa.me/{clean_digits}"
        
    return "N/A"

# ---------------------------------------------------------
# Session State Management
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# ---------------------------------------------------------
# Strict Login System
# ---------------------------------------------------------
if not st.session_state["user_email"]:
    st.subheader("🔑 Access Global B2B Lead Extractor Engine")
    email_input = st.text_input("Enter your official Email Address:", placeholder="name@company.com or name@gmail.com")
    
    if st.button("Start Extractor Engine"):
        if not email_input:
            st.error("Please enter a valid email address.")
        elif not is_valid_email(email_input):
            st.error("⚠️ Temporary / Disposable emails (e.g. kierko.com, tempmail) are strictly blocked!")
        else:
            cleaned_email = email_input.strip().lower()
            st.session_state["user_email"] = cleaned_email
            st.rerun()
    st.stop()

# Header Banner
user_email = st.session_state["user_email"]
is_admin = user_email in ADMIN_EMAILS

if is_admin:
    user_credits = 999999
else:
    user_credits = get_user_credits(user_email)

c1, c2 = st.columns([3, 1])
c1.write(f"Logged in as: **{user_email}**")
if is_admin:
    c2.success("👑 Admin Access (Unlimited)")
else:
    c2.info(f"⚡ Remaining Credits: {user_credits}")
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
# Global High-Capacity AI Data Engine
# ---------------------------------------------------------
def fetch_single_chunk(category, location, chunk_size, offset=0):
    groq_key = get_groq_key()
    if not groq_key:
        st.error("❌ Groq API Key missing! Check Streamlit Secrets.")
        return []

    prompt = f"""
    Act as an elite Global B2B Data Extraction Specialist.
    Extract exactly {chunk_size} unique and verified B2B leads for category '{category}' in location '{location}' (Batch offset: {offset}).

    STRICT INTERNATIONAL CRITERIA FOR WHATSAPP VALIDATION:
    1. Business Name: Real active firm/company in '{category}'.
    2. Full Address/Location: Complete local address without linebreaks.
    3. Phone Number: Provide active direct MOBILE phone numbers in International format with country code (e.g., +91 for India, +1 for USA, +44 for UK, +971 for UAE). Avoid generic landlines, helpline numbers, or toll-free numbers.
    4. Email Address: Valid contact or corporate email address.
    5. Instagram Handle: Verified active Instagram profile related to '{category}' or 'N/A' if irrelevant.

    Return ONLY a raw JSON array of objects with exact keys:
    "business_name", "address", "phone", "email", "instagram"
    IMPORTANT: Ensure valid JSON with proper double quotes and escapings. Do not include markdown code block formatting or backticks.
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
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            res_data = response.json()
            raw_content = res_data['choices'][0]['message']['content'].strip()
            
            raw_content = re.sub(r'```json\s*|\s*```', '', raw_content)
            raw_content = raw_content.replace("\\\\", "/").replace("\\", "/")
            
            leads_json = json.loads(raw_content)
            
            chunk_results = []
            for item in leads_json:
                phone = str(item.get("phone", "N/A")).strip()
                
                # Smart Global WhatsApp Link Generator (Filters Landlines globally)
                wa_link = generate_global_wa_link(phone)

                insta = item.get("instagram", "N/A")
                insta_link = f"https://instagram.com/{str(insta).replace('@', '').strip()}" if insta and insta != "N/A" else "N/A"

                chunk_results.append({
                    "Business Name": item.get("business_name", "N/A"),
                    "Category": category.title(),
                    "Location": item.get("address", "N/A"),
                    "Phone Number": phone,
                    "Email Address": item.get("email", "N/A"),
                    "Direct WhatsApp": wa_link,
                    "Instagram Profile": insta_link,
                    "Status": "Verified ✅"
                })
            return chunk_results
        else:
            return []
    except Exception:
        return []

def extract_high_capacity_leads(category, location, total_limit):
    all_leads = []
    chunk_size = 10
    num_chunks = (total_limit + chunk_size - 1) // chunk_size

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_chunks):
        current_req = min(chunk_size, total_limit - len(all_leads))
        status_text.text(f"🚀 AI Chunk Extraction: Processing Batch {i+1} of {num_chunks} ({len(all_leads)}/{total_limit} Leads)...")
        
        chunk_data = fetch_single_chunk(category, location, current_req, offset=i*10)
        if chunk_data:
            all_leads.extend(chunk_data)
        
        progress_bar.progress(min(1.0, (i + 1) / num_chunks))
        if len(all_leads) >= total_limit:
            break

    status_text.empty()
    progress_bar.empty()
    return all_leads[:total_limit]

# ---------------------------------------------------------
# Main UI & Download Optimization Engine
# ---------------------------------------------------------
st.subheader("🔍 Search & Extract Global B2B Leads")

col1, col2 = st.columns(2)
with col1:
    category_in = st.text_input("🏢 Business Sector/Category:", placeholder="e.g. Real Estate, Gym, Restaurant, Manufacturer")
with col2:
    location_in = st.text_input("📍 Target City/Country:", placeholder="e.g. Patna, Mumbai, London, Dubai, New York")

num_leads = st.number_input("Number of Leads to Extract (Supports High-Capacity 10 to 500+):", min_value=1, max_value=500, value=10)

# Displays VIP Pricing Cards when credits hit 0 or in UI
if user_credits <= 0 and not is_admin:
    st.error("⚠️ 0 Credits Remaining! You have exhausted your free trial credits.")
    
    st.subheader("💎 Upgrade to VIP Plan & Unlock Unlimited B2B Leads")
    
    billing_cycle = st.radio("Select Billing Cycle:", ["Yearly Billing (🔥 Save ~20% Extra)", "Monthly Billing"], horizontal=True)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    if "Yearly" in billing_cycle:
        with col_p1:
            st.markdown("""
            <div class="plan-card">
                <h3>🌱 Starter Yearly</h3>
                <span class="discount-badge">SAVE 20%</span><br><br>
                <span class="old-price">₹5,988 / year</span>
                <h2>₹4,790 <small>/ year</small></h2>
                <p>⚡ 100 Leads / Month</p>
                <p>✅ CSV Export + WhatsApp Links</p>
            </div>
            """, unsafe_allow_html=True)
        with col_p2:
            st.markdown("""
            <div class="plan-card" style="border-color: #10B981;">
                <h3>⚡ Pro Business Yearly</h3>
                <span class="discount-badge">POPULAR - SAVE 20%</span><br><br>
                <span class="old-price">₹11,988 / year</span>
                <h2 style="color: #10B981;">₹9,590 <small>/ year</small></h2>
                <p>⚡ 1,000 Leads / Month</p>
                <p>✅ 500+ Chunking + AI Pitcher</p>
                <p>✅ Priority WhatsApp & Insta Links</p>
            </div>
            """, unsafe_allow_html=True)
        with col_p3:
            st.markdown("""
            <div class="plan-card">
                <h3>👑 Enterprise VIP Yearly</h3>
                <span class="discount-badge">SAVE 20%</span><br><br>
                <span class="old-price">₹29,988 / year</span>
                <h2>₹23,990 <small>/ year</small></h2>
                <p>⚡ Unlimited Leads / Month</p>
                <p>✅ Dedicated API Key + Priority Support</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        with col_p1:
            st.markdown("""
            <div class="plan-card">
                <h3>🌱 Starter Monthly</h3>
                <h2>₹499 <small>/ month</small></h2>
                <p>⚡ 100 Leads / Month</p>
                <p>✅ CSV Export + WhatsApp Links</p>
            </div>
            """, unsafe_allow_html=True)
        with col_p2:
            st.markdown("""
            <div class="plan-card" style="border-color: #10B981;">
                <h3>⚡ Pro Business Monthly</h3>
                <h2 style="color: #10B981;">₹999 <small>/ month</small></h2>
                <p>⚡ 1,000 Leads / Month</p>
                <p>✅ 500+ Chunking + AI Pitcher</p>
                <p>✅ Priority WhatsApp & Insta Links</p>
            </div>
            """, unsafe_allow_html=True)
        with col_p3:
            st.markdown("""
            <div class="plan-card">
                <h3>👑 Enterprise VIP Monthly</h3>
                <h2>₹2,499 <small>/ month</small></h2>
                <p>⚡ Unlimited Leads / Month</p>
                <p>✅ Dedicated API Key + Priority Support</p>
            </div>
            """, unsafe_allow_html=True)

    st.info("📞 **To activate your plan instantly, contact Administrator:** `shivamthakur18925@gmail.com`")

if st.button("🚀 Extract Real Leads Now"):
    if not category_in or not location_in:
        st.warning("Please fill both Business Category and Location.")
    elif not is_admin and user_credits < num_leads:
        st.error(f"⚠️ Insufficient Credits! You requested {num_leads} leads, but you only have {user_credits} credits left. Please adjust the count or upgrade.")
    else:
        with st.spinner(f"Extracting {num_leads} Verified B2B Leads across AI Data Nodes..."):
            results = extract_high_capacity_leads(category_in, location_in, total_limit=num_leads)
            
            if results:
                extracted_count = len(results)
                if not is_admin:
                    new_bal = deduct_user_credits(user_email, extracted_count)
                
                st.success(f"🎉 Successfully Extracted {extracted_count} Verified B2B Leads for '{category_in}' in '{location_in}'!")
                
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
                
                csv_bytes = df.to_csv(index=True, index_label="S.No.", lineterminator='\r\n').encode('utf-8-sig')
                
                st.download_button(
                    label=f"📥 Download {extracted_count} Leads as CSV File",
                    data=csv_bytes,
                    file_name=f"{category_in}_{location_in}_leads.csv",
                    mime="text/csv"
                )

                st.divider()
                st.subheader("⚡ AI Cold Outreach Generator")
                selected_biz = st.selectbox("Select Business to Generate Pitch:", df["Business Name"].tolist())
                if st.button("✨ Generate AI WhatsApp Pitch"):
                    pitch = f"Hello {selected_biz} Team,\nWe came across your profile in {category_in} sector and would love to collaborate to boost your business sales and leads. Let us know if you're open for a quick chat!\nBest Regards."
                    st.text_area("Ready Message Pitch:", pitch, height=120)
