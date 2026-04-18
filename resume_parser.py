import pandas as pd

SKILL_KEYWORDS = [
    "sales",
    "communication",
    "customer service",
    "banking",
    "financial",
    "relationship management",
    "crm",
    "client service",
    "cross-selling",
    "upselling",
]


def extract_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Unknown"
    return lines[0][:80]


def extract_education(text: str) -> str:
    lower = text.lower()

    if "master" in lower:
        return "Master"
    if "bachelor" in lower:
        return "Bachelor"
    if "high school" in lower or "diploma" in lower:
        return "High School"

    return ""


def detect_banking_experience(text: str) -> str:
    lower = text.lower()
    banking_terms = [
        "bank",
        "banking",
        "teller",
        "relationship banker",
        "branch banker",
        "financial services",
        "credit union",
        "loan",
        "deposit",
    ]
    return "Yes" if any(term in lower for term in banking_terms) else "No"


def extract_skills(text: str) -> str:
    lower = text.lower()
    matched = [skill for skill in SKILL_KEYWORDS if skill in lower]
    return ", ".join(matched)


def estimate_years_from_keywords(text: str, keywords: list[str]) -> float:
    lower = text.lower()
    hits = sum(1 for kw in keywords if kw in lower)

    if hits >= 5:
        return 3
    if hits >= 3:
        return 2
    if hits >= 1:
        return 1

    return 0


def extract_sales_years(text: str) -> float:
    return estimate_years_from_keywords(
        text,
        ["sales", "quota", "upselling", "cross-selling", "revenue", "client acquisition"],
    )


def extract_customer_service_years(text: str) -> float:
    return estimate_years_from_keywords(
        text,
        ["customer service", "client service", "customer support", "front desk", "guest service"],
    )


def parse_resume_to_dataframe(text: str, role: str = "Relationship Banker") -> pd.DataFrame:
    row = {
        "Name": extract_name(text),
        "Role": role,
        "Sales_Years": extract_sales_years(text),
        "Customer_Service_Years": extract_customer_service_years(text),
        "Banking_Experience": detect_banking_experience(text),
        "Education": extract_education(text),
        "Skills": extract_skills(text),
        "Days_In_Pipeline": 0,
        "Candidate_Response_Status": "New Applicant",
    }

    return pd.DataFrame([row])
