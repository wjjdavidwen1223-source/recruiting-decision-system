import streamlit as st
import pandas as pd
from resume_scoring import run_screening

st.title("Recruiting Decision System")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Original Data")
    st.dataframe(df)

    if st.button("Run Screening"):
        results = run_screening(df)

        st.subheader("Results")
        st.dataframe(results)
