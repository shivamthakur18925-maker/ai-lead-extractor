import os
import re
import json
import requests
import pandas as pd
import streamlit as st

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="Global B2B AI Lead Extractor",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Safe API Key Resolver (Render Compatible)
# ==========================================
def get_groq_key():
    # 1. Check Primary Environment Variable on Render
    env_key = os.getenv("GROQ_API_KEY")
    if env_key and len(env_key) > 10:
        return env_key.strip()

    # 2. Check Multiple Environment Keys
    for i in range(1, 7):
        k = os.getenv(f"GROQ_API_KEY_{i}")
        if k and len(k) > 10:
            return k.strip()

    # 3. Fallback to Streamlit Secrets safely without crashing
    try:
        if hasattr(st, "secrets"):
            for i in range(1, 7):
                sec_k = st.secrets.get(f"GROQ_API_KEY_{i}")
                if sec_k and len(sec_k) > 10:
                    return sec_k.strip()
            sec_default = st.secrets.get("GROQ_API_KEY", None)
            if sec_default and len(sec_default) > 10:
                return sec_default.strip()
    except Exception:
        pass

    return None

# ==========================================
# 3. AI Data Processing Engine
# ==========================================
def fetch_single_chunk(category, location, chunk_size, offset_index):
    groq_key = get_groq_key()
    if not groq_key:
        st.error("❌ Groq API Key missing! Please set 'GROQ_API_KEY' in Render Environment Variables.")
        return []

    prompt = f"""
Act as an elite Global B2B Data Extraction Specialist.
Extract exactly {chunk_size} unique and verified B2B business leads for:
- Category: {category}
- Location: {location}
- Chunk Offset Batch: {offset_index}

STRICT QUALITY & SOCIAL FILTERS:
1. Business Name: Real active firm/company in '{location}'.
2. Phone: Valid contact number with local/international format.
3. Email: Official corporate or direct contact email address.
4. Website: Complete website URL (e.g., https://example.com).
5. Address: Complete physical or office address.
6. Verification Status: High/Verified.

Respond ONLY with a valid raw JSON array containing exactly {chunk_size} JSON objects.
Do not include markdown formatting like ```json or pre-texts.

JSON Schema:
[
  {{
    "Business Name": "Company Name",
    "Category": "{category}",
    "Location": "{location}",
    "Phone": "+1 000 000 0000",
    "Email": "info@company.com",
    "Website": "[https://company.com](https://company.com)",
    "Address": "Full Street Address",
    "Status": "Verified"
  }}
]
"""

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a precise data extraction API that returns clean JSON arrays only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }

    # Exact API Endpoint Link (Fixed URL Issue)
    api_url = "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)"

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=45
        )
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"].strip()
            cleaned = re.sub(r"^```json\s*", "", content, flags=re.MULTILINE)
            cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        else:
            st.warning(f"Batch request returned status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Extraction Error in batch processing: {str(e)}")
        return []


def extract_high_capacity_leads(category, location, total_limit):
    all_leads = []
    chunk_size = 10
    total_chunks = (total_limit + chunk_size - 1) // chunk_size

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(total_chunks):
        current_req = min(chunk_size, total_limit - len(all_leads))
        if current_req <= 0:
            break

        status_text.text(f"🚀 AI Extraction Batch {i+1} of {total_chunks} ({len(all_leads)}/{total_limit} Leads)...")
        chunk_data = fetch_single_chunk(category, location, current_req, i + 1)

        if chunk_data and isinstance(chunk_data, list):
            all_leads.extend(chunk_data)
        
        progress_bar.progress((i + 1) / total_chunks)

    status_text.text("✅ Extraction Complete!")
    progress_bar.empty()
    return all_leads[:total_limit]

# ==========================================
# 4. Main User Interface (UI)
# ==========================================
def main():
    st.title("⚡ Global B2B AI Lead Extractor")
    st.markdown("Extract targeted, high-value business leads globally powered by ultra-fast Groq AI.")

    st.divider()

    # User Input Controls
    col1, col2, col3 = st.columns([2, 2, 1.5])

    with col1:
        category_in = st.text_input("🎯 Business Category", placeholder="e.g. IT Companies, Real Estate, Clinics")

    with col2:
        location_in = st.text_input("📍 Location / City", placeholder="e.g. Dubai, New York, Mumbai")

    with col3:
        total_limit = st.number_input("🔢 Total Leads Required", min_value=10, max_value=1000, value=50, step=10)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action Button
    if st.button("🚀 Start Extracting Leads"):
        if not category_in or not location_in:
            st.warning("⚠️ Please provide both Category and Location to proceed.")
            return

        with st.spinner("Initializing AI Data Extraction Pipeline..."):
            results = extract_high_capacity_leads(category_in, location_in, total_limit)

        if results:
            df = pd.DataFrame(results)
            st.success(f"🎉 Successfully Extracted {len(df)} B2B Leads!")

            # Data Table View
            st.dataframe(df, use_container_width=True)

            # Export Button
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Leads Dataset (CSV)",
                data=csv_data,
                file_name=f"B2B_Leads_{category_in.replace(' ', '_')}_{location_in.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.error("No leads could be extracted. Please verify your search criteria and API settings.")


if __name__ == "__main__":
    main()
