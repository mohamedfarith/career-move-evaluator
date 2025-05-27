import streamlit as st
import requests
import re

# Function to call the Hugging Face Inference API
def query_llm(prompt):
    API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {
        "Authorization": f"Bearer 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"  # Replace with your HF API key
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        generated = response.json()
        if isinstance(generated, list) and "generated_text" in generated[0]:
            return generated[0]["generated_text"].strip()
        elif "generated_text" in generated:
            return generated["generated_text"].strip()
        else:
            return str(generated)
    except Exception as e:
        return f"❌ Error: {e}"

# Extract the first two sentences from a block of text
def get_first_two_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return ' '.join(sentences[:2])

# Streamlit UI
st.set_page_config(page_title="Career Move Evaluator", layout="centered")
st.title("🚀 Career Move Evaluator")

current_company = st.text_input("Your Current Company", "TCS")
company_name = st.text_input("Target Company", "Rippling")
job_title = st.text_input("Role", "Product Manager")

if st.button("Evaluate Move"):
    prompt = f"""
You are a career advisor.

Someone currently works at {current_company} and is considering moving to {company_name} as a {job_title}.

Based on funding, layoffs, team size, culture, and growth risk, provide a clear, concise 2-sentence verdict about whether this is a good career move. Only output those two sentences.
"""

    with st.spinner("Analyzing your career move..."):
        verdict_raw = query_llm(prompt)

    verdict = get_first_two_sentences(verdict_raw)

    st.subheader("🤖 AI Verdict")
    st.write(verdict)
