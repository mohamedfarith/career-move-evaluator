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
        df.columns = [col.strip('"') for col in df.columns]
        df['company'] = df['company'].astype(str).str.lower().str.strip()

        matches = df[df['company'].str.contains(company_name.lower(), na=False)]
        return matches
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
        return None

if submitted:
    st.write("🔍 Fetching details for:", target_company)

    company_info = get_company_info(lookup_name)

    layoffs = check_layoff_status(lookup_name)

    if company_info:
        st.subheader("🏢 Company Info")
        st.write("**Name:**", company_info["name"])
        st.write("**Domain:**", company_info["domain"])
        st.image(company_info["logo"], width=100)

        # Funding info (Clearbit metrics might be empty or missing)
        funding = None
        if "metrics" in company_info and "funding" in company_info["metrics"]:
            try:
                funding = int(company_info["metrics"]["funding"])
            except:
                funding = None

        if funding:
            st.write(f"💰 **Total Funding:** ${funding:,}")
        else:
            st.write("💰 **Total Funding:** Not available")

        # Layoff status + recommendation logic
        if layoffs is not None and not layoffs.empty:
            st.warning("⚠️ Layoffs reported")
            st.dataframe(layoffs[['company', 'layoff_date', 'location', 'total_laid_off']])
            if funding and funding > 10_000_000:
                st.info("📈 Despite layoffs, recent funding suggests company is investing in growth — use caution but could be opportunity.")
            else:
                st.error("⚠️ Layoffs + no significant funding — be cautious about this move.")
        else:
            st.success("✅ No layoffs found in recent records.")
            if funding and funding > 10_000_000:
                st.success("🚀 Strong funding and no layoffs — good sign for career move!")
            else:
                st.info("ℹ️ No layoffs but funding info is limited, consider researching more.")
    else:
        st.error("❌ Could not fetch company info.")
