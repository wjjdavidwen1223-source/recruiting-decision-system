import pandas as pd

# =========================
# CONFIG
# =========================
INTERVIEW_THRESHOLD = 14
HOLD_THRESHOLD = 10

REQUIRED_SKILLS = [
    "sales",
    "communication",
    "customer service",
    "banking",
    "financial",
    "relationship management",
]

CORE_SKILLS = {"sales", "communication", "customer service"}


# =========================
# SCORING FUNCTIONS
# =========================
def score_sales_experience(years):
    years = float(years)
    if years >= 2:
        return 3
    elif years >= 1:
        return 2
    return 0


def score_customer_service_experience(years):
    years = float(years)
    if years >= 2:
        return 2
    return 0


def score_banking_experience(banking_exp):
    if pd.isna(banking_exp):
        return 0
    banking_exp = str(banking_exp).strip().lower()
    if banking_exp in ["yes", "y", "true", "1"]:
        return 3
    return 0


def score_education(education):
    if pd.isna(education):
        return -999

    education = str(education).lower()

    if "master" in education:
        return 3
    elif "bachelor" in education:
        return 2
    elif "high school" in education or "diploma" in education:
        return 0
    else:
        return -999


def score_skills(skills_text):
    if pd.isna(skills_text):
        return 0, []

    skills_text = str(skills_text).lower()
    matched = []

    for skill in REQUIRED_SKILLS:
        if skill in skills_text:
            matched.append(skill)

    score = 0
    if "sales" in matched:
        score += 2
    if "communication" in matched:
        score += 2
    if "customer service" in matched:
        score += 2
    if "banking" in matched or "financial" in matched:
        score += 2
    if "relationship management" in matched:
        score += 1

    # cap skill score to avoid keyword stuffing
    return min(score, 5), matched


# =========================
# DECISION LOGIC
# =========================
def decision_with_reason(
    total_score,
    education_score,
    matched_skills,
    banking_exp_score,
    sales_years,
    customer_service_years,
):
    matched_set = set(matched_skills)
    core_skill_count = len(CORE_SKILLS.intersection(matched_set))

    # 1) Minimum education requirement
    if education_score == -999:
        return "Reject", "Does not meet minimum education requirement"

    # 2) Hard reject: no customer-facing signal at all
    if core_skill_count == 0 and customer_service_years < 1 and sales_years < 1:
        return "Reject", "No meaningful customer-facing or sales-related signal"

    # 3) Strict interview rule (very selective)
    # To get Interview, candidate must satisfy ALL of these:
    # - Bachelor's or Master's
    # - Banking exposure = Yes
    # - Sales experience >= 2 years
    # - Customer service experience >= 2 years
    # - Must show both sales and communication in skills
    # - Total score >= interview threshold
    if (
        education_score >= 2
        and banking_exp_score == 3
        and sales_years >= 2
        and customer_service_years >= 2
        and "sales" in matched_set
        and "communication" in matched_set
        and total_score >= INTERVIEW_THRESHOLD
    ):
        return "Interview", "Strong fit across banking exposure, sales, communication, and service experience"

    # 4) Hold rules
    # Candidate is not strong enough for Interview, but still worth keeping in pipeline
    # Examples:
    # - Has banking background but misses one key interview criterion
    # - Has strong customer-facing profile but lacks banking experience
    # - Has decent total score but not enough to move directly to interview
    if (
        total_score >= HOLD_THRESHOLD
        and education_score >= 0
        and (
            banking_exp_score == 3
            or core_skill_count >= 2
            or sales_years >= 2
            or customer_service_years >= 2
        )
    ):
        if banking_exp_score == 0:
            return "Hold", "Strong customer-facing profile but lacks banking/financial exposure"
        if sales_years < 2:
            return "Hold", "Relevant background, but sales experience is below direct interview threshold"
        if customer_service_years < 2:
            return "Hold", "Relevant background, but customer service experience is below direct interview threshold"
        if "communication" not in matched_set:
            return "Hold", "Relevant background, but communication signal is not strong enough for direct interview"
        return "Hold", "Potential candidate, but not strong enough for direct interview"

    # 5) Default reject
    return "Reject", "Below threshold for further progression"


# =========================
# MAIN SCREENING FUNCTION
# =========================
def run_screening(df):
    result = df.copy()

    # required columns
    if "Name" not in result.columns:
        result["Name"] = ""
    if "Sales_Years" not in result.columns:
        result["Sales_Years"] = 0
    if "Customer_Service_Years" not in result.columns:
        result["Customer_Service_Years"] = 0
    if "Banking_Experience" not in result.columns:
        result["Banking_Experience"] = "No"
    if "Education" not in result.columns:
        result["Education"] = ""
    if "Skills" not in result.columns:
        result["Skills"] = ""

    # scores
    result["Sales_Score"] = result["Sales_Years"].apply(score_sales_experience)
    result["Customer_Service_Score"] = result["Customer_Service_Years"].apply(score_customer_service_experience)
    result["Banking_Score"] = result["Banking_Experience"].apply(score_banking_experience)
    result["Education_Score"] = result["Education"].apply(score_education)

    skills_output = result["Skills"].apply(score_skills)
    result["Skills_Score"] = skills_output.apply(lambda x: x[0])
    result["Matched_Skills"] = skills_output.apply(lambda x: ", ".join(x[1]))
    result["Core_Skill_Count"] = skills_output.apply(lambda x: len(CORE_SKILLS.intersection(set(x[1]))))

    result["Score"] = (
        result["Sales_Score"]
        + result["Customer_Service_Score"]
        + result["Banking_Score"]
        + result["Education_Score"]
        + result["Skills_Score"]
    )

    decisions = result.apply(
        lambda row: decision_with_reason(
            total_score=row["Score"],
            education_score=row["Education_Score"],
            matched_skills=row["Matched_Skills"].split(", ") if row["Matched_Skills"] else [],
            banking_exp_score=row["Banking_Score"],
            sales_years=float(row["Sales_Years"]),
            customer_service_years=float(row["Customer_Service_Years"]),
        ),
        axis=1,
    )

    result["Decision"] = decisions.apply(lambda x: x[0])
    result["Decision_Reason"] = decisions.apply(lambda x: x[1])

    # sort by score descending
    result = result.sort_values(by="Score", ascending=False).reset_index(drop=True)

    return result
