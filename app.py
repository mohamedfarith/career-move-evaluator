import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Career Move Evaluator", layout="centered")
st.title("📊 Career Move Evaluator")

# Form for user inputs
with st.form("career_form"):
    target_company = st.text_input("🎯 Target Company", "Rippling")
    role = st.text_input("💼 Role Title", "Product Manager")
    current_company = st.text_input("🏢 Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

# 1. Clearbit API for company info
def get_company_info(company_name):
    clearbit_url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    response = requests.get(clearbit_url)
    if response.status_code == 200 and response.json():
        return response.json()[0]
    else:
        return None

# 2. Layoff dataset from GitHub
@st.cache_data
def check_layoff_status(company_name):
    try:
        url = "https://raw.githubusercontent.com/m0rningLight/Data_Analysis--Layoffs_Dataset/main/data/layoffs_cleaned.csv"
        df = pd.read_csv(url, encoding='latin1', delimiter=';')
        df['company'] = df['company'].str.lower()
        matches = df[df['company'].str.contains(company_name.lower(), na=False)]
        return matches
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
        return None

# 3. Hugging Face AI model (free)
def call_huggingface_ai(prompt):
    api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer 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"}  # Replace this with your Hugging Face token
    payload = {"inputs": prompt}

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            st.error(f"❌ Error from Hugging Face: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ API call failed: {e}")
        return None

# Run evaluation logic
if submitted:
    st.markdown("---")
    st.subheader("🔍 Company Overview")
    company_info = get_company_info(target_company)

    if company_info:
        st.write("**Name:**", company_info["name"])
        st.write("**Domain:**", company_info["domain"])
        st.image(company_info["logo"], width=100)
    else:
        st.error("Company details not found.")

    st.markdown("---")
    st.subheader("📉 Layoff Records")
    layoffs = check_layoff_status(target_company)

    if layoffs is not None and not layoffs.empty:
        st.warning("⚠️ Recent layoffs reported")
        st.dataframe(layoffs[['company', 'layoff_date', 'location', 'total_laid_off']])
    else:
        st.success("✅ No layoffs found in public records.")

    st.markdown("---")
    st.subheader("🤖 AI Career Move Verdict")

    ai_prompt = (
        f"The person currently works at {current_company}. "
        f"Here's some information about the company {target_company}. "
        f"The role is {role}. "
        f"Considering the funding stage, layoffs, team size, culture, and growth risks, "
        f"please provide a strategic but friendly advice on whether this is a good career move."
    )

    verdict = call_huggingface_ai(ai_prompt)
    if verdict:
        st.success(verdict)
