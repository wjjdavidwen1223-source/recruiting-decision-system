def _first_name(name: str) -> str:
    cleaned = str(name).strip()
    if not cleaned:
        return "there"
    return cleaned.split()[0]


def generate_stage_message(row):
    first_name = _first_name(row.get("Name", ""))
    role = row.get("Role", "the role")
    stage = str(row.get("Current_Stage", "")).strip()
    next_action = str(row.get("Workflow_Next_Action", "")).strip()

    if stage == "Assessment Sent":
        return (
            f"Hi {first_name}, thank you for your interest in the {role} position. "
            f"As the next step in the process, we’d like to invite you to complete a cognitive and personality assessment. "
            f"Please complete the assessments at your earliest convenience."
        )

    if stage == "Assessment Completed":
        return (
            f"Hi {first_name}, thank you for completing the assessment for the {role} position. "
            f"Our team is currently reviewing your results. "
            f"We’ll be in touch soon with the next steps."
        )

    if stage == "Assessment Passed":
        return (
            f"Hi {first_name}, thank you for completing the assessment for the {role} position. "
            f"We’d like to move you forward to a recruiter phone screen. "
            f"Next step: {next_action or 'Schedule recruiter phone screen'}."
        )

    if stage == "Recruiter Phone Screen":
        return (
            f"Hi {first_name}, thank you for your continued interest in the {role} position. "
            f"We’d like to invite you to a recruiter phone screen as the next step in the process."
        )

    if stage == "Hiring Manager Interview":
        return (
            f"Hi {first_name}, we’re excited to move you forward in the process for the {role} position. "
            f"The next step is a hiring manager interview."
        )

    if stage == "Interview Debrief":
        return (
            f"Hi {first_name}, thank you again for speaking with our team regarding the {role} position. "
            f"We are currently reviewing interview feedback and will follow up with next steps soon."
        )

    if stage == "Final HR Call":
        return (
            f"Hi {first_name}, thank you for progressing through the interview process for the {role} position. "
            f"We’d like to schedule a final HR conversation as the next step."
        )

    if stage == "Offer":
        return (
            f"Hi {first_name}, thank you for your time throughout the process for the {role} position. "
            f"We are preparing the next stage of your candidacy and will follow up shortly regarding the offer process."
        )

    if stage == "Hired":
        return (
            f"Hi {first_name}, congratulations! We’re excited to have you moving forward for the {role} position. "
            f"Our team will be in touch with onboarding details shortly."
        )

    if stage == "Rejected":
        return (
            f"Hi {first_name}, thank you for your interest in the {role} position and for your time throughout the process. "
            f"After careful review, we will not be moving forward at this time. "
            f"We appreciate your interest and encourage you to apply again in the future if relevant opportunities arise."
        )

    return (
        f"Hi {first_name}, thank you for your interest in the {role} position. "
        f"We’ll follow up soon with the next steps in the process."
    )


def generate_internal_recruiter_note(row):
    name = row.get("Name", "Unknown Candidate")
    role = row.get("Role", "Unknown Role")
    stage = row.get("Current_Stage", "")
    decision = row.get("Decision", "")
    score = row.get("Score", "")
    match_pct = row.get("Match_Score_%", "")
    matched_signals = row.get("Matched_Signals", "")
    missing_signals = row.get("Missing_Signals", "")
    blocker = row.get("Workflow_Blocker", "")
    next_action = row.get("Workflow_Next_Action", "")

    return (
        f"Candidate: {name} | Role: {role} | Stage: {stage} | Screening Decision: {decision} | "
        f"Score: {score} | Match: {match_pct}% | "
        f"Matched Signals: {matched_signals or 'N/A'} | "
        f"Missing Signals: {missing_signals or 'N/A'} | "
        f"Blocker: {blocker or 'None'} | "
        f"Next Action: {next_action or 'None'}"
    )


def attach_messages(df):
    result = df.copy()
    result["Stage_Message"] = result.apply(generate_stage_message, axis=1)
    result["Recruiter_Note"] = result.apply(generate_internal_recruiter_note, axis=1)
    return result
