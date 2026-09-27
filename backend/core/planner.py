import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

from .models import (
    P2UnderstandingPayload,
    TroubleshootingStep,
    RiskLevel,
    RISK_PRIORITY
)

class CatalogPlanner:
    def __init__(self, catalog_path: Optional[Path] = None):
        if catalog_path is None:
            catalog_path = Path(__file__).resolve().parent.parent / "data" / "scenarios.json"
        self.catalog_path = catalog_path
        self._load_catalog()

    def _load_catalog(self) -> None:
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Scenario catalog not found at: {self.catalog_path}")
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        self.scenarios = self.catalog.get("scenarios", {})
        self.aliases = self.catalog.get("canonical_id_aliases", {})

    def resolve_canonical_id(self, raw_id: str) -> Optional[str]:
        if not raw_id:
            return None
        clean_id = raw_id.strip()
        # Direct match (e.g. BATTERY_EXCESSIVE_DRAIN)
        if clean_id in self.scenarios:
            return clean_id
        # Uppercase match
        upper_id = clean_id.upper()
        if upper_id in self.scenarios:
            return upper_id
        # Lowercase alias lookup
        lower_id = clean_id.lower()
        if lower_id in self.aliases:
            return self.aliases[lower_id]
        if lower_id in self.scenarios:
            return lower_id
        return None

    def get_supported_scenarios(self) -> List[Dict[str, Any]]:
        result = []
        for sid, sdata in self.scenarios.items():
            result.append({
                "canonical_id": sid,
                "domain": sdata.get("domain"),
                "symptom": sdata.get("symptom"),
                "title": sdata.get("title"),
                "summary": sdata.get("summary"),
                "step_count": len(sdata.get("steps", []))
            })
        return result

    def get_scenario(self, raw_id: str) -> Optional[Dict[str, Any]]:
        resolved_id = self.resolve_canonical_id(raw_id)
        if resolved_id:
            return self.scenarios.get(resolved_id)
        return None

    def plan(self, payload: P2UnderstandingPayload) -> Dict[str, Any]:
        """
        Symbolic Planner:
        1. Resolves canonical scenario from catalog (supporting exact P2 IDs + aliases).
        2. Applies device model & One UI version overrides.
        3. Enforces monotonic safe ordering (low-risk first -> critical last).
        4. Guardrails 'fix_for_me': strictly forbidden for medium/high/critical steps.
        """
        raw_id = payload.canonical_id
        if not raw_id:
            raise KeyError("P2 payload did not provide a canonical_id")

        resolved_id = self.resolve_canonical_id(raw_id)
        if not resolved_id:
            raise KeyError(f"Canonical scenario '{raw_id}' not found in catalog")

        scenario = self.scenarios[resolved_id]
        device_info = payload.device_info
        one_ui_version = str(device_info.one_ui_version or device_info.one_ui or "6.1").strip()

        raw_steps = scenario.get("steps", [])
        resolved_steps: List[TroubleshootingStep] = []

        # Sort raw steps deterministically by risk level first, preserving catalog order within risk
        sorted_raw_steps = sorted(
            raw_steps,
            key=lambda step: RISK_PRIORITY.get(step.get("risk_level", "critical"), 99)
        )

        for idx, s in enumerate(sorted_raw_steps, start=1):
            risk: RiskLevel = s.get("risk_level", "low")
            
            # Version resolution: check version_overrides
            target_screen = s.get("target_screen", "")
            deeplink = s.get("deeplink", "")
            version_applied = "default"

            overrides = s.get("version_overrides", {})
            # Look for exact or prefix match (e.g., '6.1' or '6')
            matched_override = None
            if one_ui_version in overrides:
                matched_override = overrides[one_ui_version]
                version_applied = f"One UI {one_ui_version}"
            else:
                major_version = one_ui_version.split(".")[0] if "." in one_ui_version else one_ui_version
                if major_version in overrides:
                    matched_override = overrides[major_version]
                    version_applied = f"One UI {major_version}.x"

            if matched_override:
                target_screen = matched_override.get("target_screen", target_screen)
                deeplink = matched_override.get("deeplink", deeplink)

            # Symbolic Guardrail 1: 'fix_for_me' ONLY allowed for low risk
            raw_fix_for_me = s.get("fix_for_me", False)
            safe_fix_for_me = bool(raw_fix_for_me and risk == "low" and not s.get("is_destructive", False))

            # Symbolic Guardrail 2: execution_type derivation
            is_destructive = bool(s.get("is_destructive", False))
            if safe_fix_for_me:
                exec_type = "automated"
            elif is_destructive or risk in ["high", "critical"]:
                exec_type = "manual_destructive"
            else:
                exec_type = "guided_manual"

            step_obj = TroubleshootingStep(
                step_number=idx,
                step_id=s.get("step_id", f"step_{idx}"),
                action=s.get("action", "unknown_action"),
                title=s.get("title", ""),
                description=s.get("description", ""),
                risk_level=risk,
                fix_for_me=safe_fix_for_me,
                is_destructive=is_destructive,
                target_screen=target_screen,
                deeplink=deeplink,
                execution_type=exec_type,
                version_applied=version_applied
            )
            resolved_steps.append(step_obj)

        plan_data = {
            "status": "ready",
            "plan_id": f"plan_{uuid.uuid4().hex[:10]}",
            "canonical_id": resolved_id,
            "scenario_title": scenario.get("title", ""),
            "domain": scenario.get("domain", payload.domain or "General"),
            "symptom": scenario.get("symptom", payload.symptom or ""),
            "device": device_info.model,
            "one_ui_version": one_ui_version,
            "confidence": payload.confidence,
            "steps": resolved_steps,
            "total_steps": len(resolved_steps),
            "automated_fixes_count": sum(1 for st in resolved_steps if st.fix_for_me),
        }
        return plan_data
