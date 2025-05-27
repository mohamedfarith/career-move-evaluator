import streamlit as st
import requests
import pandas as pd

st.title("📊 Career Move Evaluator")

with st.form("career_form"):
    target_company = st.text_input("Target Company", "Stripe")
    role = st.text_input("Role Title", "Product Manager")
    current_company = st.text_input("Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

aliases = {
    "meta": "facebook",
    "fb": "facebook",
    "x": "twitter",
    "google": "alphabet",
    "whatsapp": "facebook",
    "instagram": "facebook"
}

lookup_name = aliases.get(target_company.lower(), target_company)

def get_company_info(company_name):
    clearbit_url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    response = requests.get(clearbit_url)
    if response.status_code == 200 and response.json():
        return response.json()[0]
    else:
        return None

@st.cache_data
def check_layoff_status(company_name):
    try:
        url = "https://raw.githubusercontent.com/m0rningLight/Data_Analysis--Layoffs_Dataset/main/data/layoffs_cleaned.csv"
        df = pd.read_csv(url, encoding='latin1', sep=';', on_bad_lines='skip')

        # Strip quotes from column names
        df.columns = [col.strip('"') for col in df.columns]

        # Normalize company column
        df['company'] = df['company'].astype(str).str.lower().str.strip()

        matches = df[df['company'].str.contains(company_name.lower(), na=False)]
        return matches
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
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

    if layoffs is not None:
        st.write("🔎 Debug: Companies matched for layoffs")
        st.write(layoffs['Company'].unique())
    else:
        st.write("No layoff data matched.")
