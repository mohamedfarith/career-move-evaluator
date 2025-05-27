import streamlit as st
import requests
import pandas as pd

st.title("📊 Career Move Evaluator")

with st.form("career_form"):
    target_company = st.text_input("Target Company", "Rippling")
    role = st.text_input("Role Title", "Product Manager")
    current_company = st.text_input("Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

# Normalize popular company aliases
aliases = {
    "meta": "facebook",
    "fb": "facebook",
    "x": "twitter",
    "google": "alphabet",
    "whatsapp": "facebook",
    "instagram": "facebook"
}

lookup_name = aliases.get(target_company.lower(), target_company)

# Function to get company data from Clearbit
def get_company_info(company_name):
    clearbit_url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    response = requests.get(clearbit_url)
    if response.status_code == 200 and response.json():
        return response.json()[0]  # Return top suggestion
    else:
        return None

# Function to check layoffs
@st.cache_data
def check_layoff_status(company_name):
    try:
        url = "https://layoffs.fyi/layoffs.csv"
        df = pd.read_csv(url)
        df['Company'] = df['Company'].str.lower()
        matches = df[df['Company'].str.lower().str.contains(company_name.lower(), na=False)]
        return matches
    except Exception as e:
        return None

if submitted:
    st.write("🔍 Fetching details for:", target_company)

    company_info = get_company_info(lookup_name)

    if company_info:
        st.subheader("🏢 Company Info")
        st.write("**Name:**", company_info["name"])
        st.write("**Domain:**", company_info["domain"])
        st.image(company_info["logo"], width=100)
    else:
        st.error("❌ Could not fetch company info.")

    layoffs = check_layoff_status(lookup_name)

    if layoffs is not None and not layoffs.empty:
        st.warning("⚠️ Layoffs reported")
        st.dataframe(layoffs[['Company', 'Date', 'Location', 'Laid Off Count']])
    else:
        st.success("✅ No layoffs found in recent records.")
