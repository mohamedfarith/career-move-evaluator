import streamlit as st
import requests
import pandas as pd

st.title("Career Move Evaluator (Hugging Face)")

# ===== User inputs form =====
with st.form("career_form"):
    target_company = st.text_input("Target Company", "Rippling")
    role = st.text_input("Role Title", "Product Manager")
    current_company = st.text_input("Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

# ===== Hugging Face API Token =====
HF_API_TOKEN = "hf_your_token_here"  # Replace with your HF API token

# ===== Function to get company info from Clearbit =====
def get_company_info(company_name):
    clearbit_url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    response = requests.get(clearbit_url)
    if response.status_code == 200 and response.json():
        return response.json()[0]  # Return top suggestion
    else:
        return None

# ===== Function to call Hugging Face summarization model =====
def call_hf_summarization(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and 'summary_text' in result[0]:
            return result[0]['summary_text']
        else:
            return "Sorry, could not generate summary."
    else:
        return f"Error: {response.status_code} - {response.text}"

# ===== Load layoffs dataset from cleaned CSV (GitHub raw URL) =====
@st.cache_data(ttl=86400)  # cache for 1 day
def load_layoffs_data():
    url = "https://raw.githubusercontent.com/m0rningLight/Data_Analysis--Layoffs_Dataset/main/data/layoffs_cleaned.csv"
    df = pd.read_csv(url, sep=';', encoding='latin1')
    return df

# ===== Check layoffs for the target company =====
def check_layoffs(company_name, df):
    df['company'] = df['company'].str.lower()
    filtered = df[df['company'].str.contains(company_name.lower(), na=False)]
    return filtered

if submitted:
    st.write(f"Evaluating career move to **{target_company}** as **{role}** from **{current_company}**...")

    # Get company info from Clearbit
    company_info = get_company_info(target_company)
    if company_info:
        st.subheader("Company Info")
        st.write(f"**Name:** {company_info.get('name', 'N/A')}")
        st.write(f"**Domain:** {company_info.get('domain', 'N/A')}")
        if company_info.get('logo'):
            st.image(company_info['logo'], width=100)
    else:
        st.warning("No company info found.")

    # Load layoffs data and check layoffs for target company
    layoffs_df = load_layoffs_data()
    layoffs_found = check_layoffs(target_company, layoffs_df)
    if not layoffs_found.empty:
        st.warning("⚠️ Layoffs reported recently:")
        st.dataframe(layoffs_found[['company', 'layoff_date', 'location', 'total_laid_off']])
    else:
        st.success("✅ No layoffs found in recent records.")

    # Build prompt for summarization
    prompt = (
        f"Here's some information about the company {target_company}. "
        f"The role is {role}. The person currently works at {current_company}. "
        "Considering the funding stage, layoffs, team size, culture, and growth risks, "
        "please provide a strategic but friendly advice on whether this is a good career move."
    )

    # Call Hugging Face summarization model
    st.subheader("AI Career Move Analysis")
    analysis = call_hf_summarization(prompt)
    st.write(analysis)
