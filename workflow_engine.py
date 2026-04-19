import pandas as pd


PIPELINE_STAGES = [
    "Applied",
    "Assessment Sent",
    "Assessment Completed",
    "Assessment Passed",
    "Recruiter Phone Screen",
    "Hiring Manager Interview",
    "Interview Debrief",
    "Final HR Call",
    "Offer",
    "Hired",
    "Rejected",
]


def _normalize_text(value: str) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def is_positive(value) -> bool:
    normalized = _normalize_text(value)
    return normalized in {"yes", "y", "true", "1", "pass", "passed", "completed"}


def is_negative(value) -> bool:
    normalized = _normalize_text(value)
    return normalized in {"no", "n", "false", "0", "fail", "failed", "reject", "rejected"}


def initialize_pipeline_fields(row):
    defaults = {
        "Current_Stage": "Applied",
        "Assessment_Status": "Not Sent",
        "Assessment_Result": "Pending",
        "Cognitive_Test_Status": "Not Sent",
        "Personality_Test_Status": "Not Sent",
        "Cognitive_Score": "",
        "Personality_Match": "",
        "Recruiter_Call_Status": "Not Scheduled",
        "Recruiter_Call_Outcome": "Pending",
        "Recruiter_Notes": "",
        "Manager_Interview_Status": "Not Scheduled",
        "Manager_Interview_Outcome": "Pending",
        "Manager_Feedback": "",
        "Interview_Debrief_Status": "Pending",
        "Final_HR_Status": "Not Started",
        "Final_HR_Outcome": "Pending",
        "Offer_Status": "None",
        "Offer_Decision": "Pending",
        "Workflow_Next_Action": "",
        "Workflow_Blocker": "",
    }

    for key, default_value in defaults.items():
        if key not in row or pd.isna(row.get(key)):
            row[key] = default_value

    return row


def trigger_assessment_if_qualified(row):
    decision = str(row.get("Decision", "")).strip()
    assessment_status = str(row.get("Assessment_Status", "")).strip()

    if decision == "Interview" and assessment_status == "Not Sent":
        row["Assessment_Status"] = "Sent"
        row["Cognitive_Test_Status"] = "Sent"
        row["Personality_Test_Status"] = "Sent"
        row["Current_Stage"] = "Assessment Sent"
        row["Workflow_Next_Action"] = "Send cognitive + personality assessments"
        row["Workflow_Blocker"] = ""

    return row


def update_after_assessment(row):
    assessment_result = _normalize_text(row.get("Assessment_Result", ""))
    cognitive_status = _normalize_text(row.get("Cognitive_Test_Status", ""))
    personality_status = _normalize_text(row.get("Personality_Test_Status", ""))

    if row.get("Current_Stage") in {"Applied", "Assessment Sent"}:
        if cognitive_status == "completed" and personality_status == "completed":
            row["Assessment_Status"] = "Completed"
            row["Current_Stage"] = "Assessment Completed"
            row["Workflow_Next_Action"] = "Review assessment results"

    if assessment_result in {"pass", "passed"}:
        row["Assessment_Status"] = "Passed"
        row["Current_Stage"] = "Assessment Passed"
        row["Recruiter_Call_Status"] = "To Schedule"
        row["Workflow_Next_Action"] = "Schedule recruiter phone screen"
        row["Workflow_Blocker"] = ""

    elif assessment_result in {"fail", "failed"}:
        row["Assessment_Status"] = "Failed"
        row["Current_Stage"] = "Rejected"
        row["Offer_Status"] = "Closed"
        row["Workflow_Next_Action"] = "Send assessment rejection"
        row["Workflow_Blocker"] = "Assessment not passed"

    return row


def update_after_recruiter_call(row):
    recruiter_outcome = _normalize_text(row.get("Recruiter_Call_Outcome", ""))
    recruiter_status = _normalize_text(row.get("Recruiter_Call_Status", ""))

    if recruiter_status == "completed" and recruiter_outcome == "pass":
        row["Current_Stage"] = "Hiring Manager Interview"
        row["Manager_Interview_Status"] = "To Schedule"
        row["Workflow_Next_Action"] = "Schedule hiring manager interview"
        row["Workflow_Blocker"] = ""

    elif recruiter_status == "completed" and recruiter_outcome == "hold":
        row["Current_Stage"] = "Interview Debrief"
        row["Workflow_Next_Action"] = "Review recruiter feedback"
        row["Workflow_Blocker"] = "Waiting for recruiter review decision"

    elif recruiter_status == "completed" and recruiter_outcome in {"fail", "reject"}:
        row["Current_Stage"] = "Rejected"
        row["Offer_Status"] = "Closed"
        row["Workflow_Next_Action"] = "Send recruiter screen rejection"
        row["Workflow_Blocker"] = "Recruiter screen not passed"

    return row


def update_after_manager_interview(row):
    manager_outcome = _normalize_text(row.get("Manager_Interview_Outcome", ""))
    manager_status = _normalize_text(row.get("Manager_Interview_Status", ""))

    if manager_status == "completed" and manager_outcome == "pass":
        row["Current_Stage"] = "Final HR Call"
        row["Final_HR_Status"] = "To Schedule"
        row["Interview_Debrief_Status"] = "Completed"
        row["Workflow_Next_Action"] = "Schedule final HR call"
        row["Workflow_Blocker"] = ""

    elif manager_status == "completed" and manager_outcome == "hold":
        row["Current_Stage"] = "Interview Debrief"
        row["Workflow_Next_Action"] = "Collect and review manager feedback"
        row["Workflow_Blocker"] = "Waiting for hiring team decision"

    elif manager_status == "completed" and manager_outcome in {"fail", "reject"}:
        row["Current_Stage"] = "Rejected"
        row["Offer_Status"] = "Closed"
        row["Interview_Debrief_Status"] = "Completed"
        row["Workflow_Next_Action"] = "Send post-interview rejection"
        row["Workflow_Blocker"] = "Manager interview not passed"

    return row


def update_after_final_hr(row):
    final_hr_outcome = _normalize_text(row.get("Final_HR_Outcome", ""))
    final_hr_status = _normalize_text(row.get("Final_HR_Status", ""))

    if final_hr_status == "completed" and final_hr_outcome == "pass":
        row["Current_Stage"] = "Offer"
        row["Offer_Status"] = "Draft"
        row["Workflow_Next_Action"] = "Prepare offer package"
        row["Workflow_Blocker"] = ""

    elif final_hr_status == "completed" and final_hr_outcome in {"fail", "reject"}:
        row["Current_Stage"] = "Rejected"
        row["Offer_Status"] = "Closed"
        row["Workflow_Next_Action"] = "Send final stage rejection"
        row["Workflow_Blocker"] = "Final HR stage not passed"

    return row


def update_offer_stage(row):
    offer_status = _normalize_text(row.get("Offer_Status", ""))
    offer_decision = _normalize_text(row.get("Offer_Decision", ""))

    if row.get("Current_Stage") == "Offer" and offer_status == "draft":
        row["Workflow_Next_Action"] = "Send offer to candidate"

    elif row.get("Current_Stage") == "Offer" and offer_status == "sent":
        row["Workflow_Next_Action"] = "Await candidate decision"

    if offer_decision in {"accept", "accepted"}:
        row["Current_Stage"] = "Hired"
        row["Offer_Status"] = "Accepted"
        row["Workflow_Next_Action"] = "Start onboarding handoff"
        row["Workflow_Blocker"] = ""

    elif offer_decision in {"decline", "declined"}:
        row["Current_Stage"] = "Rejected"
        row["Offer_Status"] = "Declined"
        row["Workflow_Next_Action"] = "Close candidate record"
        row["Workflow_Blocker"] = "Offer declined"

    return row


def apply_workflow(row):
    row = initialize_pipeline_fields(row)
    row = trigger_assessment_if_qualified(row)
    row = update_after_assessment(row)
    row = update_after_recruiter_call(row)
    row = update_after_manager_interview(row)
    row = update_after_final_hr(row)
    row = update_offer_stage(row)
    return row


def apply_workflow_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result = result.apply(apply_workflow, axis=1)
    return result


def stage_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "Current_Stage" not in df.columns:
        return pd.DataFrame(columns=["Current_Stage", "Count"])

    summary = (
        df["Current_Stage"]
        .value_counts()
        .rename_axis("Current_Stage")
        .reset_index(name="Count")
    )
    return summary


def action_queue(df: pd.DataFrame) -> pd.DataFrame:
    needed_cols = [
        "Name",
        "Role",
        "Decision",
        "Current_Stage",
        "Assessment_Status",
        "Recruiter_Call_Status",
        "Manager_Interview_Status",
        "Final_HR_Status",
        "Offer_Status",
        "Workflow_Next_Action",
        "Workflow_Blocker",
    ]

    existing_cols = [col for col in needed_cols if col in df.columns]
    if not existing_cols:
        return pd.DataFrame()

    queue_df = df[existing_cols].copy()

    if "Workflow_Next_Action" in queue_df.columns:
        queue_df = queue_df.sort_values(
            by=["Current_Stage", "Workflow_Next_Action"],
            ascending=[True, True]
        ).reset_index(drop=True)

    return queue_df
