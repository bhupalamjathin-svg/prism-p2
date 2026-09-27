import os
import re
from typing import Dict, Any, Optional

# Match P2's exact keyword rules from prism-p2
FALLBACK_RULES = [
    {
        "keywords": [
            "battery drain",
            "battery drains",
            "battery dying",
            "battery dies",
            "dies fast",
            "drains fast",
            "battery life",
            "battery draining",
        ],
        "domain": "Battery",
        "symptom": "Excessive Battery Drain",
        "canonical_id": "BATTERY_EXCESSIVE_DRAIN",
        "confidence": 0.80,
    },
    {
        "keywords": [
            "battery not charging",
            "not charging",
            "won't charge",
            "doesn't charge",
            "charging problem",
            "charging issue",
        ],
        "domain": "Battery",
        "symptom": "Battery Not Charging",
        "canonical_id": "BATTERY_NOT_CHARGING",
        "confidence": 0.80,
    },
    {
        "keywords": [
            "phone hot",
            "phone overheating",
            "phone gets hot",
            "device hot",
            "overheating",
            "heating",
        ],
        "domain": "Battery",
        "symptom": "Device Overheating",
        "canonical_id": "DEVICE_OVERHEATING",
        "confidence": 0.80,
    },
    {
        "keywords": [
            "phone slow",
            "phone is slow",
            "device slow",
            "device is slow",
            "very slow",
            "lagging",
            "lags",
            "performance slow",
            "storage full",
            "stutter",
            "freezing"
        ],
        "domain": "Performance",
        "symptom": "Device Slow Performance",
        "canonical_id": "DEVICE_SLOW_PERFORMANCE",
        "confidence": 0.80,
    },
    {
        "keywords": [
            "wifi disconnects",
            "wifi disconnecting",
            "wifi keeps disconnecting",
            "wifi not working",
            "wifi issue",
            "wifi problem",
            "disconnecting",
        ],
        "domain": "Connectivity",
        "symptom": "Wi-Fi Connection Problem",
        "canonical_id": "WIFI_CONNECTION_PROBLEM",
        "confidence": 0.80,
    },
    {
        "keywords": [
            "screen flickering",
            "display flickering",
            "screen flashing",
            "display flashing",
            "screen is flickering",
            "display is flickering",
            "flickering",
            "flicker",
            "blinking",
        ],
        "domain": "Display",
        "symptom": "Screen Flickering",
        "canonical_id": "DISPLAY_FLICKERING",
        "confidence": 0.80,
    },
]

def p2_keyword_understand(complaint: str, device_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    P2's exact deterministic understanding and confidence logic.
    Identifies single issues, vague inputs, and multiple problem conflicts.
    """
    text = complaint.lower().strip() if complaint else ""

    if not text:
        return {
            "status": "need_clarification",
            "domain": None,
            "symptom": None,
            "canonical_id": None,
            "confidence": 0.0,
            "clarification_needed": True,
            "question": "Please describe the problem with your phone.",
            "options": ["Battery", "Performance", "Connectivity", "Display", "Other"]
        }

    matches = []
    for rule in FALLBACK_RULES:
        score = 0
        for keyword in rule["keywords"]:
            if keyword in text:
                score += 1
        if score > 0:
            matches.append((score, rule))

    if not matches:
        return {
            "status": "need_clarification",
            "domain": None,
            "symptom": None,
            "canonical_id": None,
            "confidence": 0.30,
            "clarification_needed": True,
            "question": "What problem are you experiencing with your phone?",
            "options": [
                "Battery",
                "Performance",
                "Connectivity",
                "Display",
                "Other"
            ]
        }

    matches.sort(key=lambda x: x[0], reverse=True)
    best_score, best_rule = matches[0]

    # Multiple distinct problems detected with equal weight (e.g. phone hot and battery dies fast)
    if len(matches) > 1 and matches[0][0] == matches[1][0] and matches[0][1]["canonical_id"] != matches[1][1]["canonical_id"]:
        return {
            "status": "need_clarification",
            "domain": None,
            "symptom": None,
            "canonical_id": None,
            "confidence": 0.45,
            "clarification_needed": True,
            "question": "Which issue should we troubleshoot first?",
            "options": [
                matches[0][1]["symptom"],
                matches[1][1]["symptom"],
                "Both"
            ]
        }

    return {
        "status": "ready",
        "domain": best_rule["domain"],
        "symptom": best_rule["symptom"],
        "canonical_id": best_rule["canonical_id"],
        "confidence": best_rule["confidence"],
        "clarification_needed": False,
        "question": None,
        "options": []
    }
