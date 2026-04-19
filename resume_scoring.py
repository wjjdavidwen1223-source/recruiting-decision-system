import pandas as pd
from jd_profiles import BANK_ROLE_PROFILES


def safe_float(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def bool_flag(value) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"yes", "y", "true", "1"}


def score_education(education: str) -> int:
    if pd.isna(education):
        return 0

    education = str(education).strip().lower()

    if "master" in education:
        return 3
    if "bachelor" in education:
        return 2
    if "associate" in education:
        return 1
    if "high school" in education or "ged" in education or "diploma" in education:
        return 1

    return 0


def prettify_signal(signal: str) -> str:
    return signal.replace("_", " ").title()


def build_signal_map(row):
    skills = str(row.get("Skills", "")).lower()

    return {
        "client_service": safe_float(row.get("Customer_Service_Years", 0)) >= 1,
        "communication": "communication" in skills,
        "relationship_building": bool_flag(row.get("Relationship_Flag", "No")),
        "sales": safe_float(row.get("Sales_Years", 0)) >= 1,
        "banking_experience": str(row.get("Banking_Experience", "No")).strip().lower() == "yes",
        "cash_handling": safe_float(row.get("Cash_Handling_Years", 0)) >= 1,
        "digital_banking_education": bool_flag(row.get("Digital_Banking_Flag", "No")),
        "operations": bool_flag(row.get("Operations_Flag", "No")),
        "problem_solving": bool_flag(row.get("Problem_Solving_Flag", "No")),
        "adaptability": bool_flag(row.get("Adaptability_Flag", "No")),
        "education": score_education(row.get("Education", "")) >= 1,
    }


def score_candidate_against_profile(row, profile_key: str):
    profile = BANK_ROLE_PROFILES[profile_key]
    weights = profile["weights"]
    signal_map = build_signal_map(row)

    score = 0
    matched_signals = []
    missing_signals = []
    signal_breakdown = {}

    for signal, weight in weights.items():
        matched = signal_map.get(signal, False)

        signal_breakdown[signal] = {
            "matched": matched,
            "weight": weight,
            "points_awarded": weight if matched else 0,
        }

        if matched:
            score += weight
            matched_signals.append(signal)
        else:
            missing_signals.append(signal)

    max_score = sum(weights.values())

    return {
        "score": score,
        "max_score": max_score,
        "signal_map": signal_map,
        "matched_signals": matched_signals,
        "missing_signals": missing_signals,
        "signal_breakdown": signal_breakdown,
    }


def decision_from_profile_score(score, profile_key, signal_map):
    profile = BANK_ROLE_PROFILES[profile_key]
    must_have_signals = profile["must_have_signals"]

    must_have_hits = sum(1 for signal in must_have_signals if signal_map.get(signal, False))
    minimum_required = max(1, len(must_have_signals) - 1)

    if must_have_hits < minimum_required:
        return "Reject"

    if score >= profile["interview_threshold"]:
        return "Interview"

    if score >= profile["hold_threshold"]:
        return "Hold"

    return "Reject"


def stage_from_decision(decision):
    if decision == "Interview":
        return "Recruiter Review Queue"
    if decision == "Hold":
        return "Pipeline Hold"
    return "Closed / Reject"


def recruiter_signal(decision, score, interview_threshold):
    if decision == "Interview" and score >= interview_threshold + 2:
        return "🔥 High Priority"
    if decision == "Interview":
        return "✅ Interview Ready"
    if decision == "Hold":
        return "⚠️ Keep Warm"
    return "❌ Likely Rejected"


def follow_up_due(days_in_pipeline, decision):
    days = safe_float(days_in_pipeline)

    if decision == "Interview" and days >= 1:
        return "Yes"
    if decision == "Hold" and days >= 3:
        return "Yes"
    if decision == "Reject" and days >= 2:
        return "Yes"

    return "No"


def next_action(decision, follow_up_due_flag):
    if decision == "Interview":
        return "Send candidate to next step"
    if decision == "Hold" and follow_up_due_flag:
        return "Send pipeline update"
    if decision == "Hold":
        return "Review later / compare against pool"
    return "Send rejection note"


def priority_level(decision, score, interview_threshold):
    if decision == "Interview" and score >= interview_threshold + 2:
        return "High"
    if decision == "Interview":
        return "Medium"
    if decision == "Hold":
        return "Medium"
    return "Low"


def build_reason_and_improvement(row, profile_key, matched_signals, missing_signals, decision):
    profile = BANK_ROLE_PROFILES[profile_key]
    role_label = profile["label"]

    strong = [prettify_signal(s) for s in matched_signals[:5]]
    weak = [prettify_signal(s) for s in missing_signals[:5]]

    customer_years = safe_float(row.get("Customer_Service_Years", 0))
    sales_years = safe_float(row.get("Sales_Years", 0))
    cash_years = safe_float(row.get("Cash_Handling_Years", 0))
    banking_exp = str(row.get("Banking_Experience", "No")).strip().lower() == "yes"

    if decision == "Interview":
        reason = (
            f"Strong fit for {role_label}. Clear evidence across "
            f"{', '.join(strong) if strong else 'key role signals'}, "
            f"with role-relevant experience aligned to screening thresholds."
        )
        improvement = (
            "Keep quantified achievements, client-facing examples, and banking-related language visible."
        )
        return reason, improvement

    if decision == "Hold":
        parts = []

        if strong:
            parts.append(f"Candidate shows strength in {', '.join(strong[:3])}")
        if weak:
            parts.append(f"but is lighter in {', '.join(weak[:3])}")

        reason = f"Partial fit for {role_label}. " + " ".join(parts) if parts else f"Partial fit for {role_label}."

        improvement_items = []
        if customer_years < 1:
            improvement_items.append("customer-facing experience")
        if sales_years < 1:
            improvement_items.append("sales or referral evidence")
        if cash_years < 1:
            improvement_items.append("cash handling evidence")
        if not banking_exp:
            improvement_items.append("banking or financial-services context")
        if not improvement_items and weak:
            improvement_items.extend([w.lower() for w in weak[:3]])

        improvement = (
            "Strengthen evidence for " + ", ".join(improvement_items[:4]) + "."
            if improvement_items else
            "Strengthen role alignment with clearer banking-related signals."
        )
        return reason, improvement

    missing_core = [w.lower() for w in weak[:4]] if weak else ["multiple core requirements"]

    reason = (
        f"Currently below target match for {role_label}. Missing stronger evidence in "
        f"{', '.join(missing_core)}."
    )

    improvement_items = []
    if customer_years < 1:
        improvement_items.append("client-service experience")
    if sales_years < 1:
        improvement_items.append("sales or referral outcomes")
    if cash_years < 1:
        improvement_items.append("cash-handling responsibilities")
    if not banking_exp:
        improvement_items.append("banking, branch, or financial-services exposure")

    if not improvement_items:
        improvement_items = ["role-specific achievements", "measurable impact", "clearer skill wording"]

    improvement = "Add clearer evidence for " + ", ".join(improvement_items[:4]) + "."

    return reason, improvement


def generate_message(name, decision, role_label, next_step):
    first_name = str(name).split()[0] if str(name).strip() else "there"

    if decision == "Interview":
        return (
            f"Hi {first_name}, thank you for your interest in the {role_label} role. "
            f"We were impressed with your background and would like to move you forward. "
            f"Next step: {next_step}."
        )

    if decision == "Hold":
        return (
            f"Hi {first_name}, thank you for your interest in the {role_label} role. "
            f"We appreciate your background and would like to keep your application under consideration "
            f"while we continue the review process."
        )

    return (
        f"Hi {first_name}, thank you for your interest in the {role_label} role. "
        f"After review, we will not be moving forward at this time. "
        f"We appreciate your time and encourage you to apply again in the future."
    )


def build_score_breakdown_text(signal_breakdown: dict) -> str:
    parts = []

    for signal, details in signal_breakdown.items():
        label = prettify_signal(signal)
        points_awarded = details["points_awarded"]
        weight = details["weight"]
        matched = "Matched" if details["matched"] else "Missing"
        parts.append(f"{label}: {matched} ({points_awarded}/{weight})")

    return " | ".join(parts)


def run_screening(df, profile_key="generic_retail_banker"):
    result = df.copy()
    profile = BANK_ROLE_PROFILES[profile_key]
    role_label = profile["label"]

    defaults = {
        "Name": "",
        "Role": role_label,
        "Sales_Years": 0,
        "Customer_Service_Years": 0,
        "Cash_Handling_Years": 0,
        "Banking_Experience": "No",
        "Education": "",
        "Skills": "",
        "Days_In_Pipeline": 0,
        "Candidate_Response_Status": "No Response",
        "Customer_Facing_Evidence": "",
        "Sales_Evidence": "",
        "Cash_Evidence": "",
        "Banking_Evidence": "",
        "Digital_Banking_Flag": "No",
        "Digital_Banking_Evidence": "",
        "Relationship_Flag": "No",
        "Relationship_Evidence": "",
        "Operations_Flag": "No",
        "Operations_Evidence": "",
        "Problem_Solving_Flag": "No",
        "Problem_Solving_Evidence": "",
        "Adaptability_Flag": "No",
        "Adaptability_Evidence": "",
        "Experience_Summaries": "",
    }

    for col, default_val in defaults.items():
        if col not in result.columns:
            result[col] = default_val

    scored_rows = []

    for _, row in result.iterrows():
        scoring = score_candidate_against_profile(row, profile_key)

        score = scoring["score"]
        max_score = scoring["max_score"]
        signal_map = scoring["signal_map"]
        matched_signals = scoring["matched_signals"]
        missing_signals = scoring["missing_signals"]
        signal_breakdown = scoring["signal_breakdown"]

        decision = decision_from_profile_score(score, profile_key, signal_map)

        reason, improvement = build_reason_and_improvement(
            row=row,
            profile_key=profile_key,
            matched_signals=matched_signals,
            missing_signals=missing_signals,
            decision=decision,
        )

        follow_flag = follow_up_due(row.get("Days_In_Pipeline", 0), decision)
        next_step = next_action(decision, follow_flag == "Yes")
        priority = priority_level(decision, score, profile["interview_threshold"])
        recruiter_tag = recruiter_signal(decision, score, profile["interview_threshold"])
        match_pct = round((score / max_score) * 100, 1) if max_score else 0

        row_dict = row.to_dict()
        row_dict.update({
            "Role": role_label,
            "Score": score,
            "Max_Score": max_score,
            "Match_Score_%": match_pct,
            "Matched_Signals": ", ".join(prettify_signal(s) for s in matched_signals),
            "Missing_Signals": ", ".join(prettify_signal(s) for s in missing_signals),
            "Score_Breakdown": build_score_breakdown_text(signal_breakdown),
            "Decision": decision,
            "Pipeline_Stage": stage_from_decision(decision),
            "Recruiter_Signal": recruiter_tag,
            "Reason": reason,
            "Improvement": improvement,
            "Follow_Up_Due": follow_flag,
            "Next_Action": next_step,
            "Priority": priority,
            "Generated_Message": generate_message(
                row.get("Name", ""),
                decision,
                role_label,
                next_step,
            ),
        })

        scored_rows.append(row_dict)

    result_df = pd.DataFrame(scored_rows)

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    result_df["Priority_Order"] = result_df["Priority"].map(priority_order)

    result_df = result_df.sort_values(
        by=["Priority_Order", "Score"],
        ascending=[True, False]
    ).drop(columns=["Priority_Order"]).reset_index(drop=True)

    return result_df
