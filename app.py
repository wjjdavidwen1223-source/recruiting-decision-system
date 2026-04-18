import streamlit as st
import pandas as pd
from resume_scoring import run_screening

st.set_page_config(page_title="AI Recruiting Operations System", layout="wide")

st.title("AI Recruiting Operations System (David Wen)")
st.caption("Built for high-speed recruiting workflows | Evaluation, communication, dashboards, and follow-ups")

st.markdown(
    """
This system is designed to automate key recruiting operations, including:

- candidate evaluation
- decision routing
- recruiter action prioritization
- follow-up messaging
- pipeline visibility and dashboard metrics

It is built to support faster, more consistent, and more scalable hiring workflows.
"""
)

with st.expander("Expected CSV columns"):
    st.write(
        [
            "Name",
            "Role",
            "Sales_Years",
            "Customer_Service_Years",
            "Banking_Experience",
            "Education",
            "Skills",
            "Days_In_Pipeline",
            "Candidate_Response_Status",
        ]
    )

uploaded_file = st.file_uploader("Upload recruiting CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Input Data")
    st.dataframe(df, use_container_width=True)

    if st.button("Run Recruiting Workflow"):
        results = run_screening(df)

        st.subheader("Recruiting Dashboard")

        total_candidates = len(results)
        interview_count = (results["Decision"] == "Interview").sum()
        hold_count = (results["Decision"] == "Hold").sum()
        reject_count = (results["Decision"] == "Reject").sum()
        follow_up_due_count = (results["Follow_Up_Due"] == "Yes").sum()
        avg_score = round(results["Score"].mean(), 1) if total_candidates > 0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Candidates", total_candidates)
        col2.metric("Interview", interview_count)
        col3.metric("Hold", hold_count)
        col4.metric("Reject", reject_count)
        col5.metric("Follow-Ups Due", follow_up_due_count)

        col6, col7 = st.columns(2)
        col6.metric(
            "Interview Rate",
            f"{round((interview_count / total_candidates) * 100, 1) if total_candidates else 0}%",
        )
        col7.metric("Average Score", avg_score)

        st.subheader("Decision Distribution")
        decision_counts = results["Decision"].value_counts()
        st.write(decision_counts)
        st.bar_chart(decision_counts)

        st.subheader("Pipeline Stage Distribution")
        stage_counts = results["Pipeline_Stage"].value_counts()
        st.write(stage_counts)
        st.bar_chart(stage_counts)

        st.subheader("Recruiter Action Queue")
        recruiter_queue_cols = [
            "Name",
            "Role",
            "Score",
            "Match_Score_%",
            "Decision",
            "Priority",
            "Follow_Up_Due",
            "Next_Action",
            "Recruiter_Signal",
        ]
        st.dataframe(results[recruiter_queue_cols], use_container_width=True)

        st.subheader("Top Candidates")
        top_candidate_cols = [
            "Name",
            "Role",
            "Score",
            "Match_Score_%",
            "Decision",
            "Matched_Skills",
            "Reason",
        ]
        st.dataframe(results[top_candidate_cols].head(10), use_container_width=True)

        st.subheader("Full Candidate Output")
        st.dataframe(results, use_container_width=True)

        st.subheader("Workflow Architecture")
        st.markdown(
            """
**Input Layer**  
Candidate data → structured fields (experience, education, skills, pipeline timing)

**Evaluation Layer**  
Scoring model → role alignment, experience fit, banking exposure, communication signals

**Decision Layer**  
Interview / Hold / Reject

**Operations Layer**  
Priority queue → follow-up due → recruiter next action

**Communication Layer**  
Auto-generated candidate message based on decision stage
"""
        )

        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Workflow Results as CSV",
            data=csv,
            file_name="recruiting_workflow_results.csv",
            mime="text/csv",
        )
