from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timezone
import uuid

RiskLevel = Literal["low", "medium", "high", "critical"]

RISK_PRIORITY: Dict[RiskLevel, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}

class DeviceInfo(BaseModel):
    model: str = Field(default="Galaxy S24 Ultra", description="Samsung Galaxy device model (e.g., Galaxy S24 Ultra, Galaxy S23)")
    one_ui_version: str = Field(default="6.1", description="One UI OS Version (e.g., 5.1, 6.0, 6.1, 7.0)")
    one_ui: Optional[str] = Field(default=None, description="Alternative key used by P2 for One UI version")
    android_version: Optional[str] = Field(default="14", description="Underlying Android major version")
    carrier: Optional[str] = Field(default="Unlocked", description="Device carrier or variant")

    @model_validator(mode="before")
    @classmethod
    def sync_one_ui_keys(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # If one_ui is provided but one_ui_version is default/missing, sync them
            if "one_ui" in values and values["one_ui"]:
                if "one_ui_version" not in values or values["one_ui_version"] == "6.1":
                    values["one_ui_version"] = str(values["one_ui"])
            elif "one_ui_version" in values and values["one_ui_version"]:
                values["one_ui"] = str(values["one_ui_version"])
        return values

class P2UnderstandingPayload(BaseModel):
    """
    Fixed Handoff Contract from P2 (Neural + Confidence Lead).
    """
    status: Literal["ready", "need_clarification"] = Field(default="ready", description="P2 understanding state")
    domain: Optional[str] = Field(default=None, description="Problem domain (e.g., Battery, Performance)")
    symptom: Optional[str] = Field(default=None, description="Primary technical symptom identified")
    canonical_id: Optional[str] = Field(default=None, description="Standardized canonical ID from P2 catalog")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Confidence score from neural model (0.0 to 1.0)")
    clarification_needed: bool = Field(default=False, description="True if ambiguity was detected")
    question: Optional[str] = Field(default=None, description="Clarification prompt for user")
    options: List[str] = Field(default_factory=list, description="Clarification choices for user")
    complaint: Optional[str] = Field(default=None, description="Raw colloquial user complaint")
    device_info: DeviceInfo = Field(default_factory=DeviceInfo, description="Target device specifications")
    client_request_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

class TroubleshootingStep(BaseModel):
    step_number: int = Field(..., description="1-indexed sequence order (strict low -> critical risk order)")
    step_id: str = Field(..., description="Unique step identifier from catalog")
    action: str = Field(..., description="Standardized action code")
    title: str = Field(..., description="Human-friendly step headline")
    description: str = Field(..., description="Clear explanation of what this step does")
    risk_level: RiskLevel = Field(..., description="Risk category: low, medium, high, critical")
    fix_for_me: bool = Field(..., description="True if one-tap semi-automatic action is supported (allowed ONLY for low-risk)")
    is_destructive: bool = Field(..., description="True if personal data or credentials could be removed")
    target_screen: str = Field(..., description="Specific Samsung One UI Settings screen name")
    deeplink: str = Field(..., description="Exact Android / Samsung Settings Intent URI")
    execution_type: Literal["automated", "guided_manual", "manual_destructive"] = Field(
        ..., description="Execution path (automated for fix_for_me, guided_manual for safe manual, manual_destructive for wipe)"
    )
    version_applied: str = Field(..., description="One UI version for which this step/deeplink was resolved")

class ValidationResult(BaseModel):
    is_valid: bool = Field(default=True, description="Whether plan passed all symbolic validation constraints")
    passed_checks: List[str] = Field(default_factory=list, description="List of validated guardrail checks")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")
    violations: List[str] = Field(default_factory=list, description="Fatal rule violations detected")

class ClarificationResponse(BaseModel):
    """
    Returned to P3 Frontend when P2 indicates uncertainty or multiple complaints.
    """
    status: Literal["need_clarification"] = "need_clarification"
    clarification_needed: bool = True
    question: str
    options: List[str]
    confidence: float
    domain: Optional[str] = None
    symptom: Optional[str] = None
    canonical_id: Optional[str] = None
    device: str = "Galaxy S24 Ultra"
    one_ui_version: str = "6.1"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TroubleshootingPlanResponse(BaseModel):
    """
    Fixed Handoff Contract from P1 (Backend Lead) to P3 (Frontend Lead).
    """
    status: Literal["ready"] = "ready"
    plan_id: str = Field(..., description="Unique plan ID")
    canonical_id: str = Field(..., description="Resolved scenario identifier")
    scenario_title: str = Field(..., description="User-facing title of the scenario")
    domain: str = Field(..., description="Problem domain")
    symptom: str = Field(..., description="Technical symptom")
    device: str = Field(..., description="Resolved device model")
    one_ui_version: str = Field(..., description="Resolved One UI version")
    confidence: float = Field(..., description="Input confidence score")
    steps: List[TroubleshootingStep] = Field(..., description="Strictly sequenced safe troubleshooting steps")
    total_steps: int = Field(..., description="Total count of steps")
    automated_fixes_count: int = Field(..., description="Count of steps eligible for 'Fix for me'")
    execution_strategy: str = Field(
        default="Ascending Risk Monotonic: Non-Destructive Diagnostics -> Safe Configuration -> App Cache Clear -> System Settings Reset -> Factory Recovery",
        description="Rule engine sequencing strategy explanation"
    )
    validation: ValidationResult = Field(..., description="Symbolic guardrails validation report")
    cache_hit: bool = Field(default=False, description="True if served directly from fast-path cache")
    cache_key: Optional[str] = Field(default=None, description="Cache lookup key")
    latency_ms: float = Field(..., description="Processing time in milliseconds")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class FixExecutionRequest(BaseModel):
    step_id: str = Field(..., description="Step ID to execute")
    action: str = Field(..., description="Action code to execute")
    device_info: DeviceInfo = Field(default_factory=DeviceInfo)

class FixExecutionResponse(BaseModel):
    success: bool
    step_id: str
    action: str
    deeplink_opened: str
    target_screen: str
    status: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CatalogOverview(BaseModel):
    catalog_version: str
    supported_scenarios_count: int
    supported_canonical_ids: List[str]
    supported_one_ui_versions: List[str]
    supported_devices: List[str]
    scenarios: List[Dict[str, Any]]
