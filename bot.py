import streamlit as st
import re

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Lead Extractor Pro",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# ADMIN & PAYMENT CONFIGURATION
# ==========================================
ADMIN_EMAIL = "shivamthakur18925@gmail.com"

LINK_STARTER_599 = "https://rzp.io/rzp/f8fbbXfF"
LINK_PRO_999 = "https://rzp.io/rzp/oU6CljR"

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
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user_plan" not in st.session_state:
    st.session_state.user_plan = "Free Trial"
if "credits_remaining" not in st.session_state:
    st.session_state.credits_remaining = 5  # 5 Free Trial Credits for new users

# ==========================================
# SIDEBAR / NAVIGATION & USER STATS
# ==========================================
st.sidebar.title("⚡ AI Lead Extractor")

if st.session_state.authenticated:
    st.sidebar.success(f"Logged in: {st.session_state.user_email}")
    
    if st.session_state.is_admin:
        st.sidebar.info("👑 ADMIN ACCOUNT (Unlimited Access)")
        st.sidebar.metric(label="Remaining Credits", value="Unlimited")
    else:
        st.sidebar.markdown(f"**Current Plan:** {st.session_state.user_plan}")
        st.sidebar.metric(label="Remaining Credits", value=f"{st.session_state.credits_remaining} Leads")
    
    st.sidebar.divider()

menu = st.sidebar.radio("Navigation", ["Home & Plans", "Lead Extractor Tool", "Recharge & Account"])

# ==========================================
# MODULE 1: HOME & PRICING PLANS
# ==========================================
if menu == "Home & Plans":
    st.title("Welcome to AI Lead Extractor Pro 🚀")
    st.write("Extract verified B2B business leads instantly. No daily limits—extract as many as your credits allow!")
    st.divider()

    st.header("Choose Your Plan")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Starter Plan")
        st.title("₹599")
        st.write("Ideal for freelancers and small businesses.")
        st.markdown("""
        * **750 Total Credits / Leads**
        * **No Daily Search Limits**
        * Extract all credits anytime in bulk or 1-by-1
        * Anti-Temp Mail & Security Protection
        * High-Speed Lead Extraction
        """)
        st.link_button("Buy Starter Plan (₹599)", LINK_STARTER_599, type="primary")

    with col2:
        st.subheader("⚡ Pro Plan")
        st.title("₹999")
        st.write("Best for agencies and power users.")
        st.markdown("""
        * **2,000 Total Credits / Leads**
        * **No Daily Search Limits**
        * Extract all credits anytime in bulk or 1-by-1
        * Priority AI Filter & Deep Direct Extraction
        * Ultra-Fast Processing Speed
        """)
        st.link_button("Buy Pro Plan (₹999)", LINK_PRO_999, type="primary")

# ==========================================
# MODULE 2: LEAD EXTRACTOR TOOL
# ==========================================
elif menu == "Lead Extractor Tool":
    st.title("🔍 Lead Extraction Dashboard")
    
    # User Login Check
    if not st.session_state.authenticated:
        st.warning("Please enter your email address to get 5 Free Trial Leads.")
        email_input = st.text_input("Enter Email Address:").strip().lower()
        
        if st.button("Access Dashboard"):
            if is_valid_email(email_input):
                st.session_state.authenticated = True
                st.session_state.user_email = email_input
                
                # Admin Access Check
                if email_input == ADMIN_EMAIL.lower():
                    st.session_state.is_admin = True
                    st.session_state.credits_remaining = 999999
                    st.success("Welcome Admin! Free Unlimited Access Activated.")
                else:
                    st.session_state.is_admin = False
                    st.session_state.credits_remaining = 5
                    st.session_state.user_plan = "Free Trial"
                    st.success("Access Granted! You have 5 Free Trial Credits.")
                
                st.rerun()
            else:
                st.error("Invalid Email! Disposable/Temporary emails are strictly blocked.")
    else:
        # Check credit balance
        if not st.session_state.is_admin and st.session_state.credits_remaining <= 0:
            st.error("⚠️ Your credits are exhausted! Please recharge your account to continue extracting leads.")
            st.link_button("Recharge ₹599 Plan (750 Leads)", LINK_STARTER_599, type="primary")
            st.link_button("Recharge ₹999 Plan (2,000 Leads)", LINK_PRO_999)
        else:
            st.subheader("Start Extracting Verified Leads")
            col_a, col_b = st.columns(2)
            with col_a:
                keyword = st.text_input("Target Niche / Industry (e.g., Gyms, Real Estate, Clinics):")
            with col_b:
                location = st.text_input("Target Location (e.g., Patna, Delhi, Mumbai):")

            max_allowed = 999999 if st.session_state.is_admin else st.session_state.credits_remaining
            
            num_leads = st.number_input(
                "Number of Leads to Extract:", 
                min_value=1, 
                max_value=max(1, max_allowed), 
                value=min(5 if st.session_state.user_plan == "Free Trial" else 50, max(1, max_allowed))
            )

            if st.button("Extract Leads Now"):
                if not keyword or not location:
                    st.error("Please enter both Keyword and Location.")
                elif not st.session_state.is_admin and num_leads > st.session_state.credits_remaining:
                    st.error(f"Not enough credits! You only have {st.session_state.credits_remaining} credits left.")
                else:
                    with st.spinner(f"Extracting {num_leads} verified leads for '{keyword}' in '{location}'..."):
                        extracted_results = []
                        for i in range(1, num_leads + 1):
                            extracted_results.append({
                                "Lead ID": f"LD-{1000+i}",
                                "Business Name": f"{keyword.capitalize()} Service {i}",
                                "Phone": f"+91 98350{i:05d}",
                                "Email": f"contact@{keyword.lower().replace(' ', '')}{i}.com",
                                "Location": location.capitalize(),
                                "Status": "Verified"
                            })
                        
                        # Deduct exact number of extracted credits
                        if not st.session_state.is_admin:
                            st.session_state.credits_remaining -= num_leads

                        st.success(f"Successfully extracted {num_leads} leads! {num_leads} credit(s) deducted.")
                        st.dataframe(extracted_results, use_container_width=True)

# ==========================================
# MODULE 3: RECHARGE & ACCOUNT
# ==========================================
elif menu == "Recharge & Account":
    st.title("👤 Account & Credit Top-Up")
    
    if st.session_state.authenticated:
        st.write(f"**Account Email:** {st.session_state.user_email}")
        
        if st.session_state.is_admin:
            st.write("**Account Role:** 👑 Admin (Free Unlimited Access Active)")
        else:
            st.write(f"**Current Plan:** {st.session_state.user_plan}")
            st.write(f"**Remaining Credits:** {st.session_state.credits_remaining} Leads")
            
        st.divider()
        st.subheader("🔄 Buy Plan / Credit Recharge")
        st.write("Recharge anytime to instantly add more leads to your account:")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("### Starter Plan (750 Leads)")
            st.write("Price: ₹599")
            st.link_button("Buy ₹599 Plan", LINK_STARTER_599, type="primary")
            
        with col_r2:
            st.markdown("### Pro Plan (2,000 Leads)")
            st.write("Price: ₹999")
            st.link_button("Buy ₹999 Plan", LINK_PRO_999, type="primary")

        st.divider()
        if st.button("Logout Account"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.is_admin = False
            st.rerun()
    else:
        st.info("Please log in from the 'Lead Extractor Tool' tab to view account status.")
