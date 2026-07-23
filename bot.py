import streamlit as st
import re
import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Lead Extractor Pro",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# CONSTANTS & RAZORPAY PAYMENT LINKS
# ==========================================
LINK_STARTER_599 = "https://rzp.io/rzp/f8fbbXfF"
LINK_PRO_999 = "https://rzp.io/rzp/oU6CljR"

# Disallowed Disposable & Temp Mail Domains
DISALLOWED_EMAIL_DOMAINS = [
    "tempmail.com", "guerrillamail.com", "10minutemail.com", 
    "mailinator.com", "trashmail.com", "sharklasers.com",
    "dispostable.com", "getairmail.com", "temp-mail.org",
    "generator.email", "emailondeck.com", "yopmail.com"
]

# ==========================================
# HELPER FUNCTIONS & SECURITY CHECKS
# ==========================================
def is_valid_email(email: str) -> bool:
    """Validates proper email format and blocks temporary/disposable providers."""
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return False
    domain = email.split("@")[-1].lower()
    if domain in DISALLOWED_EMAIL_DOMAINS:
        return False
    return True

# Initialize Session States
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_plan" not in st.session_state:
    st.session_state.user_plan = "Starter"  # Default plan
if "credits_remaining" not in st.session_state:
    st.session_state.credits_remaining = 750  # 750 credits for ₹599 plan
if "daily_used" not in st.session_state:
    st.session_state.daily_used = 0
if "last_extraction_date" not in st.session_state:
    st.session_state.last_extraction_date = datetime.date.today()

# Reset daily limit counter if new day starts
if st.session_state.last_extraction_date != datetime.date.today():
    st.session_state.daily_used = 0
    st.session_state.last_extraction_date = datetime.date.today()

# ==========================================
# SIDEBAR / NAVIGATION & USER STATS
# ==========================================
st.sidebar.title("⚡ AI Lead Extractor")

if st.session_state.authenticated:
    st.sidebar.success(f"Logged in: {st.session_state.user_email}")
    st.sidebar.markdown(f"**Current Plan:** {st.session_state.user_plan}")
    st.sidebar.metric(label="Remaining Credits", value=f"{st.session_state.credits_remaining} Leads")
    
    daily_limit = 50 if st.session_state.user_plan == "Starter" else 150
    st.sidebar.caption(f"Today's Usage: {st.session_state.daily_used} / {daily_limit} Leads")
    st.sidebar.divider()

menu = st.sidebar.radio("Navigation", ["Home & Plans", "Lead Extractor Tool", "Recharge & Account"])

# ==========================================
# MODULE 1: HOME & PRICING PLANS
# ==========================================
if menu == "Home & Plans":
    st.title("Welcome to AI Lead Extractor Pro 🚀")
    st.write("Extract verified business leads with AI-powered search, zero spam, and automated limits.")
    st.divider()

    st.header("Choose Your Plan")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Starter Plan")
        st.title("₹599")
        st.write("Perfect for individual lead generation.")
        st.markdown("""
        * **750 Total Credits / Leads**
        * **Daily Limit:** 50 Leads / day
        * **Batch Limit:** 20 Leads per search
        * Temp-Mail Protection & Security Check
        * Standard Extraction Speed
        """)
        st.link_button("Buy Starter Plan (₹599)", LINK_STARTER_599, type="primary")

    with col2:
        st.subheader("⚡ Pro Plan")
        st.title("₹999")
        st.write("Best for agencies & power users.")
        st.markdown("""
        * **2,000 Total Credits / Leads**
        * **Daily Limit:** 150 Leads / day
        * **Batch Limit:** 50 Leads per search
        * Priority AI Filter & Deep Search
        * Ultra-Fast Extraction Speed
        """)
        st.link_button("Buy Pro Plan (₹999)", LINK_PRO_999, type="primary")

# ==========================================
# MODULE 2: LEAD EXTRACTOR TOOL
# ==========================================
elif menu == "Lead Extractor Tool":
    st.title("🔍 Lead Extraction Dashboard")
    
    # User Login Check
    if not st.session_state.authenticated:
        st.warning("Please enter your registered email address to access the extraction tool.")
        email_input = st.text_input("Enter Email Address:")
        
        if st.button("Access Dashboard"):
            if is_valid_email(email_input):
                st.session_state.authenticated = True
                st.session_state.user_email = email_input
                st.success("Access Granted! Loading your dashboard...")
                st.rerun()
            else:
                st.error("Invalid or Disallowed Email! Temporary and throwaway emails are strictly blocked.")
    else:
        # Check credit balance
        if st.session_state.credits_remaining <= 0:
            st.error("⚠️ You have exhausted your credits! Please recharge your account to continue extracting leads.")
            st.link_button("Recharge ₹599 Plan", LINK_STARTER_599, type="primary")
            st.link_button("Recharge ₹999 Plan", LINK_PRO_999)
        else:
            daily_limit = 50 if st.session_state.user_plan == "Starter" else 150
            
            st.subheader("Start Extracting Verified Leads")
            col_a, col_b = st.columns(2)
            with col_a:
                keyword = st.text_input("Target Niche / Industry (e.g., Gyms, Real Estate, Clinics):")
            with col_b:
                location = st.text_input("Target Location (e.g., Mumbai, Delhi, Bangalore):")

            max_allowed = min(20 if st.session_state.user_plan == "Starter" else 50, 
                             st.session_state.credits_remaining, 
                             daily_limit - st.session_state.daily_used)
            
            num_leads = st.number_input("Number of Leads to Extract:", min_value=1, max_value=max(1, max_allowed), value=min(10, max(1, max_allowed)))

            if st.button("Extract Leads Now"):
                if not keyword or not location:
                    st.error("Please enter both Keyword and Location.")
                elif st.session_state.daily_used + num_leads > daily_limit:
                    st.error(f"Daily limit reached! You can only extract {daily_limit - st.session_state.daily_used} more leads today.")
                else:
                    with st.spinner(f"Extracting {num_leads} verified leads for '{keyword}' in '{location}'..."):
                        # Lead extraction simulation
                        extracted_results = []
                        for i in range(1, num_leads + 1):
                            extracted_results.append({
                                "Lead ID": f"LD-{1000+i}",
                                "Business Name": f"{keyword.capitalize()} Service {i}",
                                "Phone": f"+91 98765{i:05d}",
                                "Email": f"info@service{i}.com",
                                "Location": location.capitalize(),
                                "Status": "Verified"
                            })
                        
                        # Deduct credits & update usage
                        st.session_state.credits_remaining -= num_leads
                        st.session_state.daily_used += num_leads

                        st.success(f"Successfully extracted {num_leads} leads! {num_leads} credits deducted.")
                        st.dataframe(extracted_results, use_container_width=True)

# ==========================================
# MODULE 3: RECHARGE & ACCOUNT
# ==========================================
elif menu == "Recharge & Account":
    st.title("👤 Account & Credit Top-Up")
    
    if st.session_state.authenticated:
        st.write(f"**Account Email:** {st.session_state.user_email}")
        st.write(f"**Current Plan:** {st.session_state.user_plan}")
        st.write(f"**Remaining Credits:** {st.session_state.credits_remaining} Leads")
        st.write(f"**Security Shield:** Active (Anti-Temp Mail & Anti-Abuse Enabled)")
        
        st.divider()
        st.subheader("🔄 Instant Credit Top-Up / Recharge")
        st.write("Run out of credits before the month ends? Instantly recharge your account below:")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("### Top-Up 750 Leads")
            st.write("Price: ₹599")
            st.link_button("Recharge ₹599", LINK_STARTER_599, type="primary")
            
        with col_r2:
            st.markdown("### Top-Up 2,000 Leads")
            st.write("Price: ₹999")
            st.link_button("Recharge ₹999", LINK_PRO_999, type="primary")

        st.divider()
        if st.button("Logout Account"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.rerun()
    else:
        st.info("Please log in from the 'Lead Extractor Tool' tab to view account status.")
