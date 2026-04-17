import pandas as pd

# Bank frontline resume screening criteria
REQUIRED_SKILLS = [
    "sales",
    "communication",
    "customer service",
    "banking",
    "financial",
    "relationship management"
]

INTERVIEW_THRESHOLD = 10
HOLD_THRESHOLD = 6

def score_sales_experience(years):
    years = float(years)
    if years >= 2:
        return 3
    elif years >= 1:
        return 2
    return 0

def score_education(education):
    if pd.isna(education):
        return -999  # fail minimum requirement

    education = str(education).lower()

    if "master" in education:
        return 3
    elif "bachelor" in education:
        return 2
    elif "high school" in education or "diploma" in education:
        return 0
    else:
        return -999  # fail minimum requirement

def score_skills(skills_text):
    if pd.isna(skills_text):
        return 0, []

    skills_text = str(skills_text).lower()
    matched = []

    for skill in REQUIRED_SKILLS:
        if skill in skills_text:
            matched.append(skill)

    # scoring logic
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

    return score, matched

def decision_from_score(score, education_score, matched_skills):
    # minimum requirements
    if education_score == -999:
        return "Reject"

    # must show at least some core relevant experience
    must_have = {"sales", "communication", "customer service"}
    if not must_have.intersection(set(matched_skills)):
        return "Reject"

    if score >= INTERVIEW_THRESHOLD:
        return "Interview"
    elif score >= HOLD_THRESHOLD:
        return "Hold"
    else:
        return "Reject"

def run_screening(df):
    result = df.copy()

    if "Name" not in result.columns:
        result["Name"] = ""
    if "Sales_Years" not in result.columns:
        result["Sales_Years"] = 0
    if "Education" not in result.columns:
        result["Education"] = ""
    if "Skills" not in result.columns:
        result["Skills"] = ""

    result["Sales_Score"] = result["Sales_Years"].apply(score_sales_experience)
    result["Education_Score"] = result["Education"].apply(score_education)

    skills_output = result["Skills"].apply(score_skills)
    result["Skills_Score"] = skills_output.apply(lambda x: x[0])
    result["Matched_Skills"] = skills_output.apply(lambda x: ", ".join(x[1]))

    result["Score"] = (
        result["Sales_Score"] +
        result["Education_Score"] +
        result["Skills_Score"]
    )

    result["Decision"] = result.apply(
        lambda row: decision_from_score(
            row["Score"],
            row["Education_Score"],
            row["Matched_Skills"].split(", ") if row["Matched_Skills"] else []
        ),
        axis=1
    )

    return result
