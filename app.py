import streamlit as st
import pandas as pd
import requests
import re

# Set page title
st.set_page_config(page_title="Career Move Evaluator", layout="centered")
st.title("🚀 Career Move Evaluator")

# Load layoff data
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

# Helper function to shorten AI text verdict
def summarize_verdict(long_text, max_sentences=3):
    sentences = re.split(r'(?<=[.!?]) +', long_text.strip())
    short_text = ' '.join(sentences[:max_sentences])
    return short_text

# User inputs
st.subheader("Compare Your Career Move")

company_name = st.text_input("Target Company", "Rippling")
job_title = st.text_input("Role", "Product Manager")
current_company = st.text_input("Your Current Company", "TCS")

if st.button("Evaluate Move"):
    # Display basic company data if available
    st.subheader("📉 Layoff Snapshot (if any)")
    if not layoffs.empty:
        matched = layoffs[layoffs['company'].str.lower().str.contains(company_name.lower())]
        if not matched.empty:
            st.dataframe(matched[['company', 'layoff_date', 'location', 'total_laid_off']].drop_duplicates().head(5))
        else:
            st.info("No layoff data found for that company.")
    else:
        st.warning("Layoff data unavailable.")

    # AI Prompt
    prompt = f"""
The person currently works at {current_company}. Here's some information about the company {company_name}. The role is {job_title}.
Based on funding, layoffs, team size, culture, and growth risk, give a short (2–3 sentence) verdict:
Is this a good move? Explain clearly and concisely in a supportive but strategic tone.
"""

    # Call Hugging Face inference API
    def query_llm(prompt):
        API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        headers = {
            "Authorization": f"Bearer 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"
        }
        try:
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 300, "temperature": 0.7}
            }
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            generated = response.json()
            if isinstance(generated, list):
                text = generated[0]["generated_text"].split("###")[-1].strip()
            elif "generated_text" in generated:
                text = generated["generated_text"].strip()
            else:
                text = str(generated)
            return summarize_verdict(text)
        except Exception as e:
            return f"❌ Error from Hugging Face: {e}"

    # Show spinner while LLM processes
    with st.spinner("Analyzing the opportunity..."):
        verdict = query_llm(prompt)

    st.subheader("🤖 AI Verdict")
    st.write(verdict)
