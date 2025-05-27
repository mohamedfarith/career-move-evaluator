import streamlit as st
import requests
import pandas as pd

st.title("📊 Career Move Evaluator")

with st.form("career_form"):
    target_company = st.text_input("Target Company", "Stripe")
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

# Function to check layoffs with new dataset and encoding fix
@st.cache_data
def check_layoff_status(company_name):
    try:
        url = "https://raw.githubusercontent.com/m0rningLight/Data_Analysis--Layoffs_Dataset/main/data/layoffs_cleaned.csv"
        df = pd.read_csv(url, encoding='latin1', on_bad_lines='skip')

        # Normalize company names in the dataset
        df['company'] = df['company'].astype(str).str.lower().str.strip()

        matches = df[df['company'].str.contains(company_name.lower(), na=False)]

        return matches
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
        return None

if submitted:
    st.write("🔍 Fetching details for:", target_company)

    # Company Info from Clearbit
    company_info = get_company_info(lookup_name)
    if company_info:
        st.subheader("🏢 Company Info")
        st.write("**Name:**", company_info["name"])
        st.write("**Domain:**", company_info["domain"])
        st.image(company_info["logo"], width=100)
    else:
        st.error("❌ Could not fetch company info.")

    # Layoff Info from new dataset
    layoffs = check_layoff_status(lookup_name)
    if layoffs is not None and not layoffs.empty:
        st.warning("⚠️ Layoffs reported")
        # Adjust these column names based on the dataset
        st.dataframe(layoffs[['company', 'date', 'location', 'laidoff_count']])
    else:
        st.success("✅ No layoffs found in recent records.")

    # Debug output to see matched companies
    if layoffs is not None:
        st.write("🔎 Debug: Companies matched for layoffs")
        st.write(layoffs['company'].unique())
    else:
        st.write("No layoff data matched.")
