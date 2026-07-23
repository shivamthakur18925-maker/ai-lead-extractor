import streamlit as st
import pandas as pd
import io
from groq import Groq

# -------------------------------------------------------------------
# 1. Page Configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Lead Extractor & Outreach Bot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Lead Extractor & Outreach Generator")
st.write("Extract structured leads from raw text, select outreach formats, and download data as CSV/Excel.")

# -------------------------------------------------------------------
# 2. Groq API Keys List Setup (Fallback Support)
# -------------------------------------------------------------------
# Replace these placeholders with your actual API keys when running locally
API_KEYS = [
    "YOUR_GROQ_API_KEY_1",
    "YOUR_GROQ_API_KEY_2",
    "YOUR_GROQ_API_KEY_3"
]

def get_groq_client(api_keys):
    """Loops through API keys to find a working client."""
    for key in api_keys:
        if key and not key.startswith("YOUR_GROQ"):
            try:
                return Groq(api_key=key)
            except Exception:
                continue
    # Fallback default
    return Groq(api_key=api_keys[0])

client = get_groq_client(API_KEYS)

# -------------------------------------------------------------------
# 3. Sidebar Controls & Settings
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Bot Settings")

model_choice = st.sidebar.selectbox(
    "Select AI Model",
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
)

outreach_type = st.sidebar.selectbox(
    "Select Outreach Format",
    ["Cold Email", "LinkedIn / Instagram DM", "WhatsApp Message"]
)

# -------------------------------------------------------------------
# 4. Input Area
# -------------------------------------------------------------------
input_text = st.text_area(
    "Paste Raw Business / Prospect Text Here:",
    height=200,
    placeholder="Paste website content, business descriptions, or prospect info here..."
)

# -------------------------------------------------------------------
# 5. Extraction & Outreach Logic
# -------------------------------------------------------------------
if st.button("🚀 Extract Leads & Generate Outreach", type="primary"):
    if not input_text.strip():
        st.warning("Please paste some text first!")
    else:
        with st.spinner("AI is analyzing and extracting leads..."):
            try:
                prompt = f"""
                Analyze the following text and extract potential business leads.
                For each lead found, extract:
                1. Company/Person Name
                2. Niche/Industry
                3. Key Problem/Pain Point
                4. A Personalized Outreach Message formatted specifically as a {outreach_type}.

                Format the output strictly as a CSV table with commas, using these exact column headers:
                Name, Industry, Pain_Point, Outreach_Message

                Text to analyze:
                {input_text}
                """

                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )

                result_text = response.choices[0].message.content

                st.success("Extraction Complete!")

                # Display Output
                st.subheader("📊 Extracted Results")
                st.text(result_text)

                # Attempt to parse as DataFrame for clean Table and Download options
                try:
                    # Clean markdown code blocks if AI returned them
                    clean_csv = result_text.replace("```csv", "").replace("```", "").strip()
                    df = pd.read_csv(io.StringIO(clean_csv))
                    
                    st.subheader("📋 Formatted Data Table")
                    st.dataframe(df, use_container_width=True)

                    # Download Buttons
                    col1, col2 = st.columns(2)
                    
                    # CSV Download
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    col1.download_button(
                        label="📥 Download as CSV",
                        data=csv_data,
                        file_name="extracted_leads.csv",
                        mime="text/csv"
                    )

                except Exception:
                    st.info("Raw response displayed above. (Data formatted as plain text)")

            except Exception as e:
                st.error(f"An error occurred: {e}")