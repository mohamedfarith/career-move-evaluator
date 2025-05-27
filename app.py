import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

# ======= Add your OpenAI API key here =======
OPENAI_API_KEY = "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"

# Instantiate OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

st.title("Career Move Evaluator")

with st.form("career_form"):
    target_company = st.text_input("Target Company", "Rippling")
    role = st.text_input("Role Title", "Product Manager")
    current_company = st.text_input("Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

# Function to get company data from Clearbit autocomplete API
def get_company_info(company_name):
    clearbit_url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    response = requests.get(clearbit_url)
    if response.status_code == 200 and response.json():
        return response.json()[0]  # Return top suggestion
    else:
        return None

# Function to load layoffs data from GitHub repo CSV (semicolon delimited)
@st.cache_data
def load_layoffs_data():
    url = "https://github.com/m0rningLight/Data_Analysis--Layoffs_Dataset/raw/main/data/layoffs_cleaned.csv"
    try:
        df = pd.read_csv(url, delimiter=";", encoding="latin1")
        # Clean columns and lowercase for search
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
        return pd.DataFrame()

# Function to check layoffs for a company
def check_layoff_status(company_name, df):
    if df.empty:
        return pd.DataFrame()
    matches = df[df['company'].str.lower().str.contains(company_name.lower(), na=False)]
    return matches

# Function to get AI verdict from OpenAI
def get_ai_verdict(company_info, layoffs_df, current_company, target_role):
    funding = "Unknown"
    if company_info and "metrics" in company_info:
        metrics = company_info["metrics"]
        if metrics.get("raised"):
            funding = f"${metrics['raised']:,}" if isinstance(metrics['raised'], (int,float)) else metrics['raised']
        elif metrics.get("funding"):
            funding = str(metrics['funding'])

    layoffs_count = 0
    last_layoff_date = "N/A"
    if layoffs_df is not None and not layoffs_df.empty:
        layoffs_count = layoffs_df['total_laid_off'].sum()
        last_layoff_date = layoffs_df['layoff_date'].max()

    prompt = f"""
You are a career advisor bot.

Here is data about a company and role:

Company: {company_info['name'] if company_info else 'Unknown'}
Funding: {funding}
Layoffs: {layoffs_count} people, last on {last_layoff_date}
Role applied for: {target_role}
Current company: {current_company}

Based on funding, layoffs, and risk factors, is this a good career move for someone currently working at {current_company}?

Please provide a friendly but strategic explanation with an overall verdict.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        verdict = response.choices[0].message.content.strip()
    except Exception as e:
        verdict = f"Error calling OpenAI API: {e}"

    return verdict

if submitted:
    st.write(f"Fetching details for: **{target_company}**")

    # Step 1: Get company info
    company_info = get_company_info(target_company)
    if company_info:
        st.subheader("Company Info")
        st.write("**Name:**", company_info.get("name", "N/A"))
        st.write("**Domain:**", company_info.get("domain", "N/A"))
        st.image(company_info.get("logo", ""), width=100)
    else:
        st.error("Could not fetch company info.")
        company_info = None

    # Step 2: Load layoffs data and filter
    layoffs_df = load_layoffs_data()
    company_layoffs = check_layoff_status(target_company, layoffs_df)

    if not company_layoffs.empty:
        st.warning("⚠️ Layoffs reported")
        st.dataframe(company_layoffs[['company', 'layoff_date', 'location', 'total_laid_off']])
    else:
        st.success("✅ No layoffs found in recent records.")

    # Step 3: Call AI for verdict
    if company_info:
        with st.spinner("Evaluating career move with AI..."):
            verdict = get_ai_verdict(company_info, company_layoffs, current_company, role)
            st.subheader("AI Career Move Verdict")
            st.write(verdict)
