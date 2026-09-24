import os
import json

from dotenv import load_dotenv
from groq import Groq

from schemas import UnderstandingResult
from fallback import keyword_fallback


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

CONFIDENCE_THRESHOLD = 0.70

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# ALLOWED CANONICAL IDS
# ============================================================

# These IDs must match P1's scenario catalog.

ALLOWED_CANONICAL_IDS = {
    "BATTERY_EXCESSIVE_DRAIN",
    "BATTERY_NOT_CHARGING",
    "DEVICE_OVERHEATING",
    "DEVICE_SLOW_PERFORMANCE",
    "WIFI_CONNECTION_PROBLEM",
    "DISPLAY_FLICKERING",
}


# ============================================================
# GROQ CLIENT
# ============================================================

api_key = os.getenv("GROQ_API_KEY")

client = None

if api_key:
    client = Groq(api_key=api_key)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the Neural Understanding component of a Samsung
smartphone troubleshooting system.

Your ONLY job is to understand the user's complaint.

You MUST NOT:

- provide troubleshooting steps
- suggest settings
- suggest fixes
- provide Samsung support instructions
- diagnose hardware
- invent new canonical IDs

Your job is to map the user's natural-language complaint
to one of the allowed canonical IDs.

Allowed canonical IDs:

BATTERY_EXCESSIVE_DRAIN
BATTERY_NOT_CHARGING
DEVICE_OVERHEATING
DEVICE_SLOW_PERFORMANCE
WIFI_CONNECTION_PROBLEM
DISPLAY_FLICKERING


============================================================
CONFIDENCE
============================================================

Confidence must be a number between 0 and 1.

Use HIGH confidence when the complaint clearly matches
one of the supported problems.

Use LOW confidence when:

- the complaint is vague
- multiple different problems are mentioned
- the intended problem is unclear
- the complaint does not match a supported problem


============================================================
IMPORTANT CLARIFICATION RULE
============================================================

If the complaint is vague and the domain cannot be determined,
DO NOT assume a domain.

For example:

User:
"something is wrong with my phone"

Correct:

{
    "status": "need_clarification",
    "domain": null,
    "symptom": null,
    "canonical_id": null,
    "confidence": 0.30,
    "clarification_needed": true,
    "question": "What problem are you experiencing with your phone?",
    "options": [
        "Battery",
        "Performance",
        "Connectivity",
        "Display",
        "Other"
    ]
}

Do NOT ask:

"What battery problem are you experiencing?"

unless the user actually mentioned a battery-related issue.


============================================================
MULTIPLE PROBLEMS
============================================================

If the user clearly mentions multiple different problems,
do not arbitrarily choose one.

Example:

"My phone is getting very hot and the battery dies quickly"

Return:

status = need_clarification

and ask which problem should be addressed first,
or provide "Both" as an option.


============================================================
CANONICAL ID RULE
============================================================

NEVER invent a canonical ID.

Only use one of:

BATTERY_EXCESSIVE_DRAIN
BATTERY_NOT_CHARGING
DEVICE_OVERHEATING
DEVICE_SLOW_PERFORMANCE
WIFI_CONNECTION_PROBLEM
DISPLAY_FLICKERING


============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

For a confident result:

{
    "status": "ready",
    "domain": "Battery",
    "symptom": "Excessive Battery Drain",
    "canonical_id": "BATTERY_EXCESSIVE_DRAIN",
    "confidence": 0.92,
    "clarification_needed": false,
    "question": null,
    "options": []
}

For an uncertain result:

{
    "status": "need_clarification",
    "domain": null,
    "symptom": null,
    "canonical_id": null,
    "confidence": 0.40,
    "clarification_needed": true,
    "question": "What problem are you experiencing with your phone?",
    "options": [
        "Battery",
        "Performance",
        "Connectivity",
        "Display",
        "Other"
    ]
}
"""


# ============================================================
# VALIDATION
# ============================================================

def validate_result(result: dict) -> UnderstandingResult:

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    try:
        confidence = float(
            result.get("confidence", 0.0)
        )
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(
        0.0,
        min(1.0, confidence)
    )

    result["confidence"] = confidence


    # --------------------------------------------------------
    # CANONICAL ID VALIDATION
    # --------------------------------------------------------

    canonical_id = result.get(
        "canonical_id"
    )

    if canonical_id not in ALLOWED_CANONICAL_IDS:

        result["status"] = "need_clarification"

        result["domain"] = None
        result["symptom"] = None
        result["canonical_id"] = None

        result["clarification_needed"] = True

        result["question"] = (
            "What problem are you experiencing with your phone?"
        )

        result["options"] = [
            "Battery",
            "Performance",
            "Connectivity",
            "Display",
            "Other"
        ]


    # --------------------------------------------------------
    # LOW CONFIDENCE
    # --------------------------------------------------------

    if confidence < CONFIDENCE_THRESHOLD:

        result["status"] = "need_clarification"

        result["domain"] = None
        result["symptom"] = None
        result["canonical_id"] = None

        result["clarification_needed"] = True

        if not result.get("question"):

            result["question"] = (
                "What problem are you experiencing "
                "with your phone?"
            )

        if not result.get("options"):

            result["options"] = [
                "Battery",
                "Performance",
                "Connectivity",
                "Display",
                "Other"
            ]


    # --------------------------------------------------------
    # READY RESULT
    # --------------------------------------------------------

    if result.get("status") == "ready":

        result["clarification_needed"] = False

        result["question"] = None

        result["options"] = []


    # --------------------------------------------------------
    # CLARIFICATION RESULT
    # --------------------------------------------------------

    if result.get("status") == "need_clarification":

        result["domain"] = None

        result["symptom"] = None

        result["canonical_id"] = None

        result["clarification_needed"] = True


    return UnderstandingResult(
        **result
    )


# ============================================================
# LLM UNDERSTANDING
# ============================================================

def llm_understand(
    complaint: str,
    device_info: dict | None = None
):

    if client is None:

        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )


    # --------------------------------------------------------
    # DEVICE INFORMATION
    # --------------------------------------------------------

    device_model = "Unknown"

    one_ui = "Unknown"

    if device_info:

        device_model = device_info.get(
            "model",
            "Unknown"
        )

        one_ui = device_info.get(
            "one_ui",
            "Unknown"
        )


    # --------------------------------------------------------
    # USER PROMPT
    # --------------------------------------------------------

    user_prompt = f"""
User complaint:

{complaint}


Device information:

Model: {device_model}

One UI version: {one_ui}


Understand ONLY what problem the user is describing.

Do not provide troubleshooting steps.

Do not suggest fixes.

Do not invent a canonical ID.

Return only the required JSON.
"""


    # --------------------------------------------------------
    # GROQ REQUEST
    # --------------------------------------------------------

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0,

        max_completion_tokens=500,

        response_format={
            "type": "json_schema",

            "json_schema": {

                "name": "troubleshooting_understanding",

                "strict": True,

                "schema": {

                    "type": "object",

                    "properties": {

                        "status": {
                            "type": "string",
                            "enum": [
                                "ready",
                                "need_clarification"
                            ]
                        },

                        "domain": {
                            "type": [
                                "string",
                                "null"
                            ]
                        },

                        "symptom": {
                            "type": [
                                "string",
                                "null"
                            ]
                        },

                        "canonical_id": {

                            "type": [
                                "string",
                                "null"
                            ],

                            "enum": [
                                "BATTERY_EXCESSIVE_DRAIN",
                                "BATTERY_NOT_CHARGING",
                                "DEVICE_OVERHEATING",
                                "DEVICE_SLOW_PERFORMANCE",
                                "WIFI_CONNECTION_PROBLEM",
                                "DISPLAY_FLICKERING",
                                None
                            ]
                        },

                        "confidence": {
                            "type": "number"
                        },

                        "clarification_needed": {
                            "type": "boolean"
                        },

                        "question": {
                            "type": [
                                "string",
                                "null"
                            ]
                        },

                        "options": {

                            "type": "array",

                            "items": {
                                "type": "string"
                            }
                        }
                    },

                    "required": [
                        "status",
                        "domain",
                        "symptom",
                        "canonical_id",
                        "confidence",
                        "clarification_needed",
                        "question",
                        "options"
                    ],

                    "additionalProperties": False
                }
            }
        },

        include_reasoning=False
    )


    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    content = response.choices[0].message.content

    return json.loads(content)


# ============================================================
# MAIN UNDERSTAND FUNCTION
# ============================================================

def understand(
    complaint: str,
    device_info: dict | None = None
) -> dict:

    # --------------------------------------------------------
    # EMPTY COMPLAINT
    # --------------------------------------------------------

    if not complaint or not complaint.strip():

        return {
            "status": "need_clarification",

            "domain": None,

            "symptom": None,

            "canonical_id": None,

            "confidence": 0.0,

            "clarification_needed": True,

            "question": (
                "Please describe the problem "
                "with your phone."
            ),

            "options": []
        }


    # --------------------------------------------------------
    # TRY REAL LLM
    # --------------------------------------------------------

    try:

        result = llm_understand(
            complaint,
            device_info
        )

        validated = validate_result(
            result
        )

        return validated.model_dump()


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    except Exception as error:

        print(
            f"\n[WARNING] LLM failed: {error}"
        )

        print(
            "[INFO] Using keyword fallback..."
        )

        fallback_result = keyword_fallback(
            complaint
        )

        validated = validate_result(
            fallback_result
        )

        return validated.model_dump()


# ============================================================
# MANUAL TESTING
# ============================================================

if __name__ == "__main__":

    tests = [

        "My battery dies really fast",

        "bro my phone is dying in like two hours",

        "battery went crazy after the update",

        "my samsung is lagging badly",

        "why is my phone so slow",

        "wifi disconnects every few minutes",

        "my internet keeps dropping",

        "my display keeps blinking",

        "my screen is flickering",

        "my phone feels like a heater",

        "battery",

        "something is wrong with my phone",

        "phone problem",

        "My phone gets hot and the battery dies really fast"
    ]


    device_info = {

        "model": "Galaxy S24",

        "one_ui": "6.1"
    }


    for complaint in tests:

        print("\n")

        print("=" * 70)

        print("INPUT:")

        print(complaint)

        print("=" * 70)


        result = understand(

            complaint,

            device_info
        )


        print(

            json.dumps(

                result,

                indent=2
            )
        )
