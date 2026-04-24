# 🏥 AI Healthcare Recruiting Copilot

**Built by JiaJun (David) Wen (文家俊)**

An end-to-end AI-powered recruiting decision system designed for healthcare and clinical roles, including Registered Nurses (RN), Medical Assistants, and Clinical Research Coordinators.

---

## 🚀 Overview

This project simulates a real-world healthcare recruiting pipeline by combining resume parsing, structured scoring logic, workflow automation, and recruiter decision support.

The system is designed to replicate how healthcare organizations evaluate, screen, and move candidates through a hiring process that requires strict validation of certifications, clinical experience, and compliance standards.

Unlike generic resume screening tools, this system focuses on **domain-specific decision logic**, incorporating healthcare requirements such as licensing, patient care, EMR systems, and regulatory awareness.

---

## 🔥 Key Features

### 🧠 AI Screening Engine

The scoring engine evaluates candidates using structured signals extracted from resumes.

#### Core Evaluation Dimensions

- Certifications (RN license, BLS, ACLS, CPR)
- Clinical experience (hospital, ICU, ER, outpatient)
- Patient care exposure
- EMR/EHR systems (Epic, Cerner)
- HIPAA compliance awareness
- Communication and teamwork
- Education level (ADN, BSN, MSN, PhD)

---

### 🎓 Education Handling (Important Design Choice)

Education is modeled as a **graded signal**, not a binary filter.

#### Education Mapping

| Degree | Score |
|------|------|
| Associate (ADN) | 1 |
| Bachelor (BSN) | 2 |
| Master (MSN) | 3 |
| PhD / Doctorate | 4 |

#### Scoring Logic

- Education contributes as a **supporting signal**
- Higher degrees provide incremental advantage
- Education does **not override core requirements** (e.g., RN license)

#### Design Rationale

Healthcare hiring prioritizes:

1. Certifications (RN license)
2. Clinical experience
3. Compliance awareness

Education is used to differentiate candidates **after core qualifications are met**

---

### ⚠️ Risk Detection

The system identifies potential risks in candidate profiles:

- Missing RN license
- Limited clinical experience
- Lack of hospital exposure
- Missing compliance indicators

#### Example Risk Flags

- ❗ Missing RN license  
- ⚠️ No hospital experience  
- ⚠️ No HIPAA/compliance signal  

---

### 📄 Resume Parsing Engine

The system includes a rule-based NLP parser that extracts structured data from raw resumes.

#### Supported Formats

- PDF
- DOCX
- Plain text

#### Extracted Fields

- Name
- Certifications
- Clinical experience level
- Skills
- Education
- Experience summaries

#### Healthcare Signal Detection

The parser identifies:

- RN and certification keywords
- Clinical environment terms (ICU, ER, hospital)
- EMR/EHR mentions
- Compliance language (HIPAA)
- Patient care terminology

---

### ⚙️ Workflow Engine (ATS Simulation)

This system includes a full recruiting workflow engine that simulates an Applicant Tracking System (ATS).

#### Pipeline Stages

- Applied
- Assessment Sent
- Assessment Completed
- Assessment Passed
- Recruiter Screening
- Clinical Interview
- Interview Debrief
- Final HR Review
- Offer
- Hired / Rejected

#### Features

- State-based stage transitions
- Automated workflow progression
- Recruiter action queue
- Blocker detection
- Follow-up reminders
- Priority assignment

---

### 📊 Recruiter Dashboard (Streamlit)

The Streamlit UI enables interactive candidate management.

#### Features

- Batch screening interface
- Candidate ranking and prioritization
- Pipeline visualization
- Stage-based workflow controls
- Real-time decision updates

---

### 🔌 FastAPI Backend

The system includes a production-style backend API.

#### API Capabilities

- Single candidate screening
- Batch candidate processing
- Full pipeline execution
- Workflow analytics
- Action queue generation

#### Core Endpoints

GET /health
GET /profiles
POST /resume/screen
POST /resume/full_pipeline
POST /resume/batch_screen
POST /resume/batch_full_pipeline
POST /workflow/stage_summary
POST /workflow/action_queue

---

## 🧩 System Architecture

Streamlit Frontend
↓
Resume Parser (NLP)
↓
Healthcare Scoring Engine
↓
Workflow Engine (State Machine)
↓
FastAPI Backend

---

## 🔄 Domain Adaptation (Key Highlight)

This system was originally built for **banking recruiting** and later refactored into a healthcare-focused decision engine.

### Key Transformations

#### 1. Signal Redesign
- Removed sales and banking-related features
- Introduced clinical signals and certifications

#### 2. Scoring Logic Upgrade
- Prioritized RN license and clinical experience
- Added must-have signals
- Introduced risk flagging
- Added education as graded signal

#### 3. Resume Parser Refactor
- Replaced business keywords with healthcare terminology
- Added clinical evidence detection

#### 4. Workflow Adaptation
- Updated pipeline stages for healthcare hiring
- Added clinical assessments and compliance checks

---

## 📂 Project Structure
.
├── app.py
├── main.py
├── resume_parser.py
├── resume_scoring.py
├── workflow_engine.py
├── jd_profiles.py
├── communications.py
├── file_parsers.py
└── README.md


---

## 📊 Example Workflow

1. Upload resume or CSV file
2. Parse candidate information
3. Extract healthcare-specific signals
4. Score candidate against job profile
5. Generate decision (Interview / Hold / Reject)
6. Move candidate through workflow pipeline
7. Manage via dashboard or API

---

## 💡 Why This Project Matters

This project demonstrates:

- End-to-end AI system design
- Domain-specific decision modeling
- Workflow automation
- Backend + frontend integration
- Domain adaptation (banking → healthcare)
- Realistic hiring logic simulation

---

## 🛠 Tech Stack

- Python
- Streamlit
- FastAPI
- Pandas
- Pydantic
- Regex-based NLP parsing

---

## 💼 Resume Bullet

Built and deployed an AI-powered healthcare recruiting system using Streamlit and FastAPI to automate resume parsing, clinical signal extraction, candidate scoring, and hiring workflow decisions.

---

## 🔮 Future Improvements

- LLM-based resume parsing
- Explainable AI scoring (decision reasoning)
- ML-based candidate ranking
- ATS integration
- Multi-role hiring models




