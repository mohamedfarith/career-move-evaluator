import streamlit as st
import pandas as pd
import requests

# Set page title
st.set_page_config(page_title="Career Move Evaluator", layout="centered")
st.title("🚀 Career Move Evaluator")

# Load layoff data with caching
@st.cache_data
def load_layoff_data():
    url = "https://raw.githubusercontent.com/m0rningLight/Data_Analysis--Layoffs_Dataset/main/data/layoffs_cleaned.csv"
    try:
        df = pd.read_csv(url, encoding="ISO-8859-1", sep=";")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error loading layoff data: {e}")
        return pd.DataFrame()

layoffs = load_layoff_data()

# User inputs
st.subheader("Compare Your Career Move")

company_name = st.text_input("Target Company", "Rippling")
job_title = st.text_input("Role", "Product Manager")
current_company = st.text_input("Your Current Company", "TCS")

def query_llm(prompt):
    API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {
        "Authorization": f"Bearer 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"
    }
    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200, "temperature": 0.7}
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        generated = response.json()
        if isinstance(generated, list):
            return generated[0]["generated_text"].split("###")[-1].strip()
        elif "generated_text" in generated:
            return generated["generated_text"].strip()
        else:
            return str(generated)
    except Exception as e:
        return f"❌ Error from Hugging Face: {e}"

if st.button("Evaluate Move"):
    st.subheader("📉 Layoff Snapshot (if any)")
    if not layoffs.empty:
        matched = layoffs[layoffs['company'].str.lower().str.contains(company_name.lower())]
        if not matched.empty:
            st.dataframe(matched[['company', 'layoff_date', 'location', 'total_laid_off']].drop_duplicates().head(5))
        else:
            st.info("No layoff data found for that company.")
    else:
        st.warning("Layoff data unavailable.")

    # Simplified prompt — keep it short to avoid LLM echoing raw data
    prompt = f"""
You are a career advisor. Someone currently works at {current_company} and is considering moving to {company_name} as a {job_title}.
Based on factors like funding, layoffs, team size, culture, and growth risk, provide a concise (2-3 sentence) verdict:
Is this a good career move? Answer clearly and supportively, focusing on strategic advice.
"""

    with st.spinner("Analyzing the opportunity..."):
        verdict = query_llm(prompt)

    st.subheader("🤖 AI Verdict")
    st.write(verdict)
