import streamlit as st

st.title("Career Move Evaluator")

with st.form("career_form"):
    target_company = st.text_input("Target Company", "Rippling")
    role = st.text_input("Role Title", "Product Manager")
    current_company = st.text_input("Your Current Company", "TCS")
    submitted = st.form_submit_button("Evaluate")

if submitted:
    st.write("Fetching details for:", target_company)
