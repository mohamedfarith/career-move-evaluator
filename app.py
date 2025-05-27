import streamlit as st
import requests
import pandas as pd
import openai
import os

st.title("🚀 Career Move Evaluator")

# OpenAI API key should be set as Streamlit Secret or env variable for deployment safety
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

LAYOFFS_CSV_URL = "https://raw.githubusercontent.com/m0rningLight/Data_Analysis--Layoffs_Dataset/main/data/layoffs_cleaned.csv"

with st.form("career_form"):
    target_company = st.text_input("Target Company", "Rippling")
    role = st.text_input("Role Title", "Product Manager")
    current_company = st.text_input("Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

def get_company_info(company_name):
    url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.json():
            return res.json()[0]
    except:
        pass
    return None

@st.cache_data(show_spinner=False)
def load_layoffs_data():
    try:
        df = pd.read_csv(LAYOFFS_CSV_URL, sep=';', encoding='latin1')
        # Normalize columns: lowercase and strip quotes/spaces
        df.columns = [col.strip().lower().replace('"','').replace(' ', '_') for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
        return None

def check_layoffs(company_name, layoffs_df):
    if layoffs_df is None:
        return None
    comp = company_name.lower()
    filtered = layoffs_df[layoffs_df['company'].str.lower().str.contains(comp, na=False)]
    return filtered

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        verdict = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        verdict = f"Error calling OpenAI API: {e}"

    return verdict

if submitted:
    st.write(f"### Searching for company info on '{target_company}'...")
    company_info = get_company_info(target_company)

    if company_info:
        st.subheader("Company Info")
        st.write(f"**Name:** {company_info.get('name', 'N/A')}")
        st.write(f"**Domain:** {company_info.get('domain', 'N/A')}")
        if company_info.get("logo"):
            st.image(company_info["logo"], width=100)
    else:
        st.error("Could not fetch company info.")

    st.write("### Checking layoffs data...")
    layoffs_df = load_layoffs_data()
    layoffs = check_layoffs(target_company, layoffs_df)

    if layoffs is not None and not layoffs.empty:
        st.warning("⚠️ Layoffs reported")
        st.dataframe(layoffs[['company', 'layoff_date', 'location', 'total_laid_off']])
    else:
        st.success("✅ No layoffs found in recent records.")

    if company_info:
        st.write("### Analyzing career move with AI...")
        verdict = get_ai_verdict(company_info, layoffs, current_company, role)
        st.subheader("🤖 AI Career Move Verdict")
        st.write(verdict)
