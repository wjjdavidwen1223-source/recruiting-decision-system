import streamlit as st
import pandas as pd
from resume_scoring import run_screening

st.set_page_config(page_title="AI Recruiting Decision System", layout="wide")

st.title("AI Recruiting Decision System (David Wen)")
st.caption("Bank Frontline Resume Screening | Rule-based Decision Engine")

st.markdown(
    """
Upload a CSV file containing candidate data.  
The app evaluates candidates based on:
- Sales experience
- Customer service experience
- Banking / financial exposure
- Education
- Role-relevant skills

Outputs include:
- Match score
- Interview / Hold / Reject decision
- Recruiter signal
- Reason
- Improvement suggestions
"""
)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Original Data")
    st.dataframe(df, use_container_width=True)

    if st.button("Run Screening"):
        results = run_screening(df)

        st.subheader("Results")
        st.dataframe(results, use_container_width=True)

        st.subheader("Summary")
        summary = results["Decision"].value_counts()
        st.write(summary)

        st.bar_chart(summary)

        st.subheader("Top Candidates")
        top_cols = [
            "Name",
            "Score",
            "Match_Score_%",
            "Decision",
            "Recruiter_Signal",
            "Matched_Skills",
        ]
        existing_top_cols = [col for col in top_cols if col in results.columns]
        st.dataframe(results[existing_top_cols].head(10), use_container_width=True)

        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="screening_results.csv",
            mime="text/csv",
        )
