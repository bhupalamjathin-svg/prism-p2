import time
from typing import Dict, Any, Optional, List, Union
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.models import (
    P2UnderstandingPayload,
    TroubleshootingPlanResponse,
    ClarificationResponse,
    CatalogOverview,
    FixExecutionRequest,
    FixExecutionResponse,
    DeviceInfo
)
from core.planner import CatalogPlanner
from core.validator import PlanValidator
from core.cache import FastPathCache
from core.neural_bridge import p2_keyword_understand

router = APIRouter()

planner = CatalogPlanner()
validator = PlanValidator()
cache = FastPathCache()

class FlexibleTroubleshootRequest(BaseModel):
    """
    Accepts:
    1. Exact P2 Understanding Payload (status='ready' or 'need_clarification')
    2. Raw user complaint + device info
    """
    status: Optional[str] = Field(default="ready", description="P2 status: 'ready' or 'need_clarification'")
    canonical_id: Optional[str] = Field(default=None, description="P2 canonical ID (e.g., BATTERY_EXCESSIVE_DRAIN)")
    domain: Optional[str] = Field(default=None)
    symptom: Optional[str] = Field(default=None)
    confidence: Optional[float] = Field(default=0.95, ge=0.0, le=1.0)
    clarification_needed: Optional[bool] = Field(default=False)
    question: Optional[str] = Field(default=None)
    options: Optional[List[str]] = Field(default_factory=list)
    complaint: Optional[str] = Field(default=None, description="Raw colloquial user complaint")
    device_info: DeviceInfo = Field(default_factory=DeviceInfo)

@router.post(
    "/troubleshoot",
    response_model=Union[TroubleshootingPlanResponse, ClarificationResponse],
    summary="Generate Validated Troubleshooting Plan or Request Clarification",
    description="Main P1 endpoint: seamlessly receives P2 understanding (or raw complaint), handles clarification when confidence < 0.70, sequences safe steps, validates guardrails, and serves via fast-path cache."
)
async def troubleshoot(request: FlexibleTroubleshootRequest):
    start_time = time.perf_counter()

    # 1. Check if P2 already identified need for clarification
    if request.status == "need_clarification" or request.clarification_needed or (request.confidence is not None and request.confidence < 0.70 and not request.canonical_id):
        return ClarificationResponse(
            status="need_clarification",
            clarification_needed=True,
            question=request.question or "Could you clarify what issue you are experiencing with your phone?",
            options=request.options or ["Battery", "Performance", "Connectivity", "Display", "Other"],
            confidence=request.confidence or 0.30,
            domain=request.domain,
            symptom=request.symptom,
            canonical_id=request.canonical_id,
            device=request.device_info.model,
            one_ui_version=str(request.device_info.one_ui_version or request.device_info.one_ui or "6.1")
        )

    canonical_id = request.canonical_id
    domain = request.domain
    symptom = request.symptom
    confidence = request.confidence or 0.95

    # 2. If no canonical_id supplied but complaint exists, use P2 understanding bridge
    if not canonical_id and request.complaint:
        p2_result = p2_keyword_understand(request.complaint, request.device_info.model_dump())
        if p2_result.get("status") == "need_clarification":
            return ClarificationResponse(
                status="need_clarification",
                clarification_needed=True,
                question=p2_result.get("question", "What issue are you experiencing?"),
                options=p2_result.get("options", []),
                confidence=p2_result.get("confidence", 0.30),
                domain=p2_result.get("domain"),
                symptom=p2_result.get("symptom"),
                canonical_id=p2_result.get("canonical_id"),
                device=request.device_info.model,
                one_ui_version=str(request.device_info.one_ui_version or request.device_info.one_ui or "6.1")
            )
        canonical_id = p2_result.get("canonical_id")
        domain = p2_result.get("domain")
        symptom = p2_result.get("symptom")
        confidence = p2_result.get("confidence", 0.80)

    if not canonical_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'canonical_id' (from P2) or 'complaint' must be supplied."
        )

    resolved_canonical_id = planner.resolve_canonical_id(canonical_id)
    if not resolved_canonical_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canonical ID '{canonical_id}' is not in the supported catalog."
        )

    one_ui_ver = str(request.device_info.one_ui_version or request.device_info.one_ui or "6.1")

    # 3. Fast-Path Cache check (<300ms SLA, sub-millisecond in-memory)
    cached_plan = cache.get(
        canonical_id=resolved_canonical_id,
        model=request.device_info.model,
        one_ui_version=one_ui_ver
    )
    if cached_plan:
        return cached_plan

    # 4. Symbolic Planning & Sequencing
    p2_payload = P2UnderstandingPayload(
        status="ready",
        canonical_id=resolved_canonical_id,
        domain=domain,
        symptom=symptom,
        confidence=confidence,
        complaint=request.complaint,
        device_info=request.device_info
    )

    try:
        plan_dict = planner.plan(p2_payload)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Planner error: {str(e)}"
        )

    # 5. Deterministic Validation Layer
    val_result = validator.validate(plan_dict)
    if not val_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Symbolic guardrail validation failure",
                "violations": val_result.violations,
                "warnings": val_result.warnings
            }
        )

    # 6. Build Final Response
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    cache_key = cache.generate_key(
        canonical_id=resolved_canonical_id,
        model=request.device_info.model,
        one_ui_version=one_ui_ver
    )

    response = TroubleshootingPlanResponse(
        status="ready",
        plan_id=plan_dict["plan_id"],
        canonical_id=resolved_canonical_id,
        scenario_title=plan_dict["scenario_title"],
        domain=plan_dict["domain"],
        symptom=plan_dict["symptom"],
        device=plan_dict["device"],
        one_ui_version=plan_dict["one_ui_version"],
        confidence=plan_dict["confidence"],
        steps=plan_dict["steps"],
        total_steps=plan_dict["total_steps"],
        automated_fixes_count=plan_dict["automated_fixes_count"],
        validation=val_result,
        cache_hit=False,
        cache_key=cache_key,
        latency_ms=round(latency_ms, 3)
    )

    # 7. Populate Fast-Path Cache
    cache.set(
        canonical_id=resolved_canonical_id,
        model=request.device_info.model,
        one_ui_version=one_ui_ver,
        plan=response
    )

    return response

@router.get("/scenarios", response_model=CatalogOverview)
async def list_scenarios():
    scenarios_list = planner.get_supported_scenarios()
    return CatalogOverview(
        catalog_version=planner.catalog.get("catalog_version", "2.2.0"),
        supported_scenarios_count=len(scenarios_list),
        supported_canonical_ids=planner.catalog.get("supported_canonical_ids", []),
        supported_one_ui_versions=planner.catalog.get("supported_one_ui_versions", []),
        supported_devices=planner.catalog.get("supported_devices", []),
        scenarios=scenarios_list
    )

@router.get("/scenarios/{canonical_id}")
async def get_scenario_details(canonical_id: str):
    scenario = planner.get_scenario(canonical_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{canonical_id}' does not exist in catalog."
        )
    return scenario

@router.post("/fix", response_model=FixExecutionResponse, summary="Execute Semi-Automatic 'Fix for me'")
async def execute_fix(req: FixExecutionRequest):
    """
    Handles user clicking 'Fix for me' in P3 frontend.
    Verifies action is low-risk and returns execution status + deep link receipt.
    """
    matching_step = None
    for sdata in planner.scenarios.values():
        for st in sdata.get("steps", []):
            if st.get("step_id") == req.step_id or st.get("action") == req.action:
                matching_step = st
                break
        if matching_step:
            break

    if not matching_step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step '{req.step_id}' or action '{req.action}' not found in catalog."
        )

    if matching_step.get("risk_level") != "low" or not matching_step.get("fix_for_me"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action '{req.action}' has risk '{matching_step.get('risk_level')}'. "
                   f"'Fix for me' is strictly forbidden for non-low risk actions."
        )

    deeplink = matching_step.get("deeplink")
    target_screen = matching_step.get("target_screen")
    one_ui_ver = str(req.device_info.one_ui_version or req.device_info.one_ui or "6.1")

    return FixExecutionResponse(
        success=True,
        step_id=req.step_id,
        action=req.action,
        deeplink_opened=deeplink,
        target_screen=target_screen,
        status="applied_successfully",
        message=f"Settings URI dispatched to {req.device_info.model} ({one_ui_ver}). Fix applied."
    )

@router.get("/metrics")
async def get_cache_metrics():
    return cache.get_metrics()

@router.post("/cache/clear")
async def clear_cache():
    cache.clear()
    return {"message": "Fast-path cache flushed successfully"}
