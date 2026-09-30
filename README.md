# 🧠 Samsung PRISM


## Demo Video

[Watch the Samsung PRISM Demo Video](https://drive.google.com/file/d/1Fycq6SgYgQpwuYQLcsMfIaL8aThC7XMw/view?usp=sharing)
- 📊 [Project Presentation](submission/MSRIT_TechSage_Submission.pptx)


### Smart Guided Troubleshooting Engine

> Turning vague device complaints into safe, personalized, step-by-step troubleshooting actions.

<p align="center">

**Neural Understanding × Symbolic Reasoning × Risk-Aware Automation**

</p>

---

## 🚀 Overview

Samsung PRISM is an intelligent troubleshooting system that understands natural-language device complaints and transforms them into structured, validated troubleshooting plans.

Instead of forcing users to navigate through complicated support menus, PRISM allows them to simply describe their problem in natural language.

### Example

**User:**

> "My phone is getting really slow and laggy."

**PRISM:**

```text
Natural Language Complaint
            ↓
     Neural Understanding
            ↓
      Problem Detection
            ↓
     Canonical Problem ID
            ↓
      Scenario Catalog
            ↓
       Risk-Aware Planner
            ↓
          Validator
            ↓
   Guided Troubleshooting Plan
            ↓
       Safe "Fix for Me"



✨ Key Idea
PRISM combines AI-based natural-language understanding with a deterministic troubleshooting engine.
The neural layer understands what the user means.
The symbolic backend determines what should be done.
The validator ensures that automated actions remain within predefined safety boundaries.
🎯 Supported Problems
PRISM currently supports:
- 🔋 Excessive Battery Drain
- 🔌 Battery Not Charging
- 🌡️ Device Overheating
- ⚡ Device Slow Performance
- 📶 Wi-Fi Connection Problems
- 🖥️ Display Flickering





## 🏗️ Architecture

PRISM follows a hybrid **Neural + Symbolic** architecture.

```text
                    ┌─────────────────────┐
                    │       User          │
                    │ Natural Language    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   P2 Neural Layer   │
                    │                     │
                    │ GPT-OSS-20B        │
                    │ Complaint           │
                    │ Understanding      │
                    │ Confidence          │
                    │ Clarification       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Canonical Problem   │
                    │       ID            │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   P1 Backend        │
                    │                     │
                    │ Scenario Catalog    │
                    │ Planner             │
                    │ Validator           │
                    │ Cache               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Validated           │
                    │ Troubleshooting     │
                    │ Plan                │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             ┌─────────────┐      ┌─────────────┐
             │ Guided      │      │ Fix for Me  │
             │ Manual     │      │ Low Risk    │
             │ Steps      │      │ Only        │
             └─────────────┘      └──────┬──────┘
                                         │
                                         ▼
                                  Samsung Deeplink






🧠 Neural Layer
The neural layer is responsible for understanding the user's complaint.
It determines:
- The problem domain
- The detected symptom
- The canonical problem ID
- Confidence score
- Whether clarification is required
The neural layer does not generate troubleshooting instructions.
⚙️ Symbolic Layer
The symbolic backend maps the canonical problem to a predefined troubleshooting scenario.
It is responsible for:
- Selecting the appropriate scenario
- Ordering troubleshooting steps
- Applying device and One UI context
- Validating the generated plan
- Enforcing safety boundaries
This separation keeps the system flexible at the language-understanding layer while keeping troubleshooting behavior deterministic and controlled.




## 🔄 System Flow

PRISM processes a troubleshooting request through a controlled pipeline.

### 1️⃣ User Complaint

The user describes the issue naturally.

```text
"My phone keeps getting really hot and laggy."

2️⃣ Neural Understanding
The P2 neural layer analyzes the complaint and converts it into a structured understanding result.
Example:


{
  "status": "ready",
  "domain": "Performance",
  "symptom": "Device Slow Performance",
  "canonical_id": "DEVICE_SLOW_PERFORMANCE",
  "confidence": 0.95,
  "clarification_needed": false
}


The neural layer is restricted to understanding the complaint. It does not generate troubleshooting steps.


3️⃣ Confidence & Clarification
PRISM does not blindly trust an uncertain interpretation.
If confidence is below the configured threshold, the system requests clarification.
Example:
User:
"Something is wrong with my phone."

PRISM:
"What problem are you experiencing with your phone?"

[ Battery ]
[ Performance ]
[ Connectivity ]
[ Display ]
[ Other ]
This prevents the system from arbitrarily selecting a troubleshooting scenario.




4️⃣ Scenario Selection
Once a canonical problem is identified, the backend maps it to a predefined troubleshooting scenario.
For example:
DEVICE_SLOW_PERFORMANCE
          ↓
Free Up Storage Space & Eliminate Performance Stutter


5️⃣ Risk-Aware Planning
The planner generates an ordered sequence of troubleshooting actions.
Actions are organized by risk:
LOW
 ↓
MEDIUM
 ↓
HIGH
 ↓
CRITICAL
This allows safer diagnostic and configuration actions to be presented before destructive recovery actions.




6️⃣ Plan Validation
Before a plan is returned to the frontend, the validator checks:
- Step sequence
- Risk ordering
- Deeplink structure
- Fix-for-me safety boundaries
- Destructive action restrictions
- Required troubleshooting steps
Only validated plans are returned as usable troubleshooting plans.
7️⃣ Fix for Me
Low-risk, non-destructive actions may be executed automatically.
Low Risk
   ↓
Fix for me → Allowed ✅
Higher-risk or destructive actions remain manual:
Critical / Destructive
   ↓
Fix for me → Blocked 🔒
8️⃣ Samsung Deeplink
Validated actions can contain Samsung/Android intent deeplinks that take the user directly to the relevant settings screen.
Example:
Settings > Device Care > Optimize now
The frontend can dispatch the corresponding deeplink when the user chooses Fix for me.



## ✨ Key Features

### 🧠 Natural Language Understanding
Users can describe device problems naturally instead of navigating through technical troubleshooting menus.

### 🎯 Canonical Problem Detection
User complaints are mapped to a controlled set of canonical troubleshooting scenarios.

### 📊 Confidence-Aware Decisions
PRISM uses confidence to determine whether it has enough information to proceed or should ask the user for clarification.

### 📱 Device & One UI Awareness
Troubleshooting plans can take device model and One UI version into account.

### 🧩 Hybrid Neural + Symbolic Architecture
Neural understanding handles ambiguity in natural language, while deterministic backend logic controls troubleshooting behavior.

### 🛠️ Guided Troubleshooting
Each scenario contains an ordered sequence of actionable troubleshooting steps.

### ⚡ Fix for Me
Low-risk, non-destructive actions can be triggered automatically through validated Samsung/Android deeplinks.

### 🔒 Risk-Aware Safety
PRISM prevents high-risk and destructive actions from being automatically executed.

### 💾 Fast Path Cache
Previously processed troubleshooting requests can be served through the backend cache to reduce unnecessary processing.

---

## 🔒 Safety Model

Safety is a core part of the PRISM architecture.

PRISM separates **understanding** from **action execution**.

The neural model identifies the user's problem, but it does not decide which device settings should be changed.

The symbolic planner selects predefined actions, and the validator checks the resulting plan before it reaches the frontend.

### Fix-for-Me Rules

| Risk Level | Automatic Execution |
|------------|---------------------|
| 🟢 Low | ✅ Allowed when non-destructive |
| 🟡 Medium | ❌ Manual |
| 🟠 High | ❌ Manual |
| 🔴 Critical | ❌ Manual |

Destructive actions such as factory reset are explicitly prevented from being executed through **Fix for Me**.

---
## 🧰 Tech Stack

| Component | Technology |
|-----------|------------|
| 🧠 Neural Understanding | GPT-OSS-20B via Groq |
| ⚙️ Backend | Python + FastAPI |
| 📋 Data Validation | Pydantic |
| 🧩 Planning | Deterministic Scenario Planner |
| 🔒 Safety | Rule-based Plan Validator |
| 💾 Caching | Backend Fast Path Cache |
| 📱 Actions | Samsung / Android Intent Deeplinks |
| 🎨 Frontend | Streamlit |
| 🧪 Testing | Python Test Suite |
| 🔧 Version Control | Git + GitHub |

---

## 📁 Project Structure

```text
prism-p2/
│
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── models.py
│   │   ├── neural_bridge.py
│   │   ├── planner.py
│   │   └── validator.py
│   │
│   ├── data/
│   │   └── scenarios.json
│   │
│   ├── fallback.py
│   ├── understand.py
│   ├── schemas.py
│   ├── main.py
│   ├── README.md
│   └── CONTRACTS_AND_HANDOFF.md
│
├── frontend/
│
├── tests/
│   ├── __init__.py
│   └── test_understand.py
│
├── requirements.txt
├── .gitignore
└── README.md

Component Responsibilities
P2 — Neural Understanding
backend/understand.py
backend/fallback.py
backend/schemas.py
Responsible for understanding natural-language complaints, confidence estimation, clarification, and canonical problem identification.
P1 — Backend & Catalog
backend/core/
backend/api/
backend/data/
Responsible for scenario selection, troubleshooting planning, validation, caching, API routing, and safety enforcement.
P3 — Frontend
frontend/
Responsible for the user-facing troubleshooting experience and interaction with the backend APIs.

Step 6 — API Documentation
Paste this next:
## 📡 API

The backend exposes a REST API for interacting with the troubleshooting engine.

### Base URL

When running locally:

```text
http://127.0.0.1:8000
Interactive API documentation is available at:
http://127.0.0.1:8000/docs
POST /troubleshoot
Analyzes a user's complaint and returns either a validated troubleshooting plan or a clarification request.
Request
{
  "complaint": "My phone is very slow",
  "device_info": {
    "model": "Galaxy S24",
    "one_ui": "6.1"
  }
}
Response
{
  "status": "ready",
  "canonical_id": "DEVICE_SLOW_PERFORMANCE",
  "domain": "Performance",
  "symptom": "Device Slow Performance",
  "confidence": 0.95,
  "steps": []
}
The actual response contains the complete validated troubleshooting plan.
POST /fix
Requests execution of a specific troubleshooting action.
Request
{
  "plan_id": "plan_7d35b43b06",
  "step_id": "step_str_01",
  "action": "execute"
}
Successful Response
{
  "success": true,
  "step_id": "step_str_01",
  "action": "execute",
  "status": "applied_successfully"
}
Only actions permitted by the safety validator can be executed automatically.
GET /scenarios
Returns the supported troubleshooting scenarios.
GET /scenarios/{canonical_id}
Returns information about a specific troubleshooting scenario.
Example:
/scenarios/DEVICE_SLOW_PERFORMANCE
GET /metrics
Returns backend/cache metrics.
GET /health
Checks whether the backend service is running.
API Documentation
FastAPI automatically provides interactive Swagger documentation:
/docs
This allows developers to test endpoints without requiring the frontend.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bhupalamjathin-svg/prism-p2.git
cd prism-p2
2. Create a virtual environment
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables
Create a .env file:
GROQ_API_KEY=your_api_key_here
5. Start the backend
python -m backend.main
Open:
http://127.0.0.1:8000/docs
🧪 Testing
Run the neural understanding tests:
python -m tests.test_understand
Expected:
Passed: 9/9
👥 Team
Role	Responsibility
P1	Backend, Scenario Catalog & Planning
P2	Neural Understanding & Confidence
P3	Frontend & User Experience
P4	Integration, Testing & Documentation


🔮 Future Scope
- Expanded device and One UI coverage
- More troubleshooting scenarios
- Improved clarification conversations
- Richer device diagnostics
- Production-grade Samsung integrations
- Advanced telemetry and analytics
📄 License
Developed as part of the Samsung PRISM project.
