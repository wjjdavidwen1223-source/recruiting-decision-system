from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import pandas as pd

from resume_scoring import run_screening
from workflow_engine import (
    apply_workflow_to_dataframe,
    stage_summary,
    action_queue,
)
from jd_profiles import HEALTHCARE_ROLE_PROFILES


app = FastAPI(
    title="AI Healthcare Recruiting API",
    description="Backend API for healthcare candidate screening, clinical evaluation, and recruiting workflow automation.",
    version="1.0.0",
)


# =========================
# Pydantic Models
# =========================

class CandidateRequest(BaseModel):
    Name: str = ""
    Role: str = "Registered Nurse"

    Certifications: str = ""
    Clinical_Years: float = 0
    Education: str = ""
    Skills: str = ""

    Days_In_Pipeline: float = 0
    Candidate_Response_Status: str = "New Applicant"

    # Healthcare signals
    RN_License_Flag: str = "No"
    BLS_ACLS_Flag: str = "No"
    Hospital_Experience_Flag: str = "No"
    Patient_Care_Flag: str = "No"
    EMR_Flag: str = "No"
    HIPAA_Flag: str = "No"
    Communication_Flag: str = "No"
    Teamwork_Flag: str = "No"

    Experience_Summaries: str = ""

    # Workflow
    Current_Stage: str = "Applied"
    Assessment_Status: str = "Not Sent"
    Assessment_Result: str = "Pending"

    Clinical_Judgment_Status: str = "Not Sent"
    Patient_Care_Scenario_Status: str = "Not Sent"
    Compliance_Check_Status: str = "Not Sent"

    Recruiter_Call_Status: str = "Not Scheduled"
    Recruiter_Call_Outcome: str = "Pending"

    Manager_Interview_Status: str = "Not Scheduled"
    Manager_Interview_Outcome: str = "Pending"

    Final_HR_Status: str = "Not Started"
    Final_HR_Outcome: str = "Pending"

    Offer_Status: str = "None"
    Offer_Decision: str = "Pending"

    Workflow_Next_Action: str = ""
    Workflow_Blocker: str = ""
    Last_Workflow_Event: str = ""


class BatchCandidateRequest(BaseModel):
    candidates: List[CandidateRequest]
    profile_key: str = "registered_nurse"


class SingleCandidateEnvelope(BaseModel):
    candidate: CandidateRequest
    profile_key: str = "registered_nurse"


# =========================
# Helpers
# =========================

def validate_profile_key(profile_key: str):
    if profile_key not in HEALTHCARE_ROLE_PROFILES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid profile_key: {profile_key}",
                "valid_profile_keys": list(HEALTHCARE_ROLE_PROFILES.keys()),
            },
        )


def candidate_to_df(candidate: CandidateRequest):
    return pd.DataFrame([candidate.model_dump()])


def batch_to_df(candidates: List[CandidateRequest]):
    return pd.DataFrame([c.model_dump() for c in candidates])


def safe_record(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {}
    return df.to_dict(orient="records")[0]


# =========================
# Basic Endpoints
# =========================

@app.get("/")
def root():
    return {
        "message": "AI Healthcare Recruiting API is running",
        "docs_url": "/docs",
        "endpoints": [
            "/health",
            "/profiles",
            "/resume/screen",
            "/resume/full_pipeline",
            "/resume/batch_screen",
            "/resume/batch_full_pipeline",
            "/workflow/stage_summary",
            "/workflow/action_queue",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AI Healthcare Recruiting API",
        "version": "1.0.0",
    }


@app.get("/profiles")
def get_profiles():
    return {
        "available_profile_keys": list(HEALTHCARE_ROLE_PROFILES.keys()),
        "profiles": HEALTHCARE_ROLE_PROFILES,
    }


# =========================
# Screening
# =========================

@app.post("/resume/screen")
def screen_resume(payload: SingleCandidateEnvelope):
    validate_profile_key(payload.profile_key)

    df = candidate_to_df(payload.candidate)
    screened = run_screening(df, profile_key=payload.profile_key)

    return safe_record(screened)


@app.post("/resume/full_pipeline")
def full_pipeline(payload: SingleCandidateEnvelope):
    validate_profile_key(payload.profile_key)

    df = candidate_to_df(payload.candidate)

    screened = run_screening(df, profile_key=payload.profile_key)
    final = apply_workflow_to_dataframe(screened)

    return safe_record(final)


# =========================
# Batch
# =========================

@app.post("/resume/batch_screen")
def batch_screen(payload: BatchCandidateRequest):
    validate_profile_key(payload.profile_key)

    if not payload.candidates:
        raise HTTPException(status_code=400, detail="candidates list cannot be empty")

    df = batch_to_df(payload.candidates)
    screened = run_screening(df, profile_key=payload.profile_key)

    return {
        "count": len(screened),
        "results": screened.to_dict(orient="records"),
    }


@app.post("/resume/batch_full_pipeline")
def batch_full_pipeline(payload: BatchCandidateRequest):
    validate_profile_key(payload.profile_key)

    if not payload.candidates:
        raise HTTPException(status_code=400, detail="candidates list cannot be empty")

    df = batch_to_df(payload.candidates)
    screened = run_screening(df, profile_key=payload.profile_key)
    final = apply_workflow_to_dataframe(screened)

    return {
        "count": len(final),
        "results": final.to_dict(orient="records"),
    }


# =========================
# Workflow Analytics
# =========================

@app.post("/workflow/stage_summary")
def workflow_stage_summary(payload: BatchCandidateRequest):
    validate_profile_key(payload.profile_key)

    df = batch_to_df(payload.candidates)
    screened = run_screening(df, profile_key=payload.profile_key)
    final = apply_workflow_to_dataframe(screened)

    summary = stage_summary(final)

    return {
        "count": len(summary),
        "stage_summary": summary.to_dict(orient="records"),
    }


@app.post("/workflow/action_queue")
def workflow_action_queue(payload: BatchCandidateRequest):
    validate_profile_key(payload.profile_key)

    df = batch_to_df(payload.candidates)
    screened = run_screening(df, profile_key=payload.profile_key)
    final = apply_workflow_to_dataframe(screened)

    queue = action_queue(final)

    return {
        "count": len(queue),
        "action_queue": queue.to_dict(orient="records"),
    }
