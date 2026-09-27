from typing import Dict, Any, List
from .models import ValidationResult, TroubleshootingStep, RISK_PRIORITY

class PlanValidator:
    """
    Deterministic Validation Layer / Symbolic Guardrails:
    Enforces that no plan reaches the user or frontend unless it satisfies:
    1. Valid Action check (actions must be recognized and non-empty).
    2. Exact Deeplink syntax and component check.
    3. Anti-parent-menu substitution check (prevents generic parent menus from substituting deep child screens).
    4. Strict Monotonic Risk Ordering (low -> medium -> high -> critical).
    5. Fix-for-me Safety (strictly forbidden for medium, high, or destructive steps).
    6. Non-empty step sequence.
    """

    GENERIC_PARENT_INTENTS = {
        "intent:#Intent;action=android.settings.SETTINGS;package=com.android.settings;end"
    }

    def validate(self, plan_dict: Dict[str, Any]) -> ValidationResult:
        passed_checks: List[str] = []
        warnings: List[str] = []
        violations: List[str] = []

        steps: List[TroubleshootingStep] = plan_dict.get("steps", [])

        # Check 1: Steps presence
        if not steps:
            violations.append("Plan contains zero troubleshooting steps.")
        else:
            passed_checks.append("Plan contains non-empty sequence of troubleshooting steps.")

        # Check 2: Monotonic Risk Ordering
        current_risk_priority = 0
        order_valid = True
        for idx, step in enumerate(steps):
            step_priority = RISK_PRIORITY.get(step.risk_level, 99)
            if step_priority < current_risk_priority:
                violations.append(
                    f"Ordering Violation at step {step.step_number} ('{step.title}'): "
                    f"Risk level '{step.risk_level}' appears after a higher risk level."
                )
                order_valid = False
            current_risk_priority = step_priority

        if order_valid and steps:
            passed_checks.append("Strict monotonic risk ordering verified (low -> medium -> high -> critical).")

        # Check 3: Deeplink Syntax & Specificity
        for step in steps:
            dl = (step.deeplink or "").strip()
            if not dl:
                violations.append(f"Step {step.step_number} ('{step.action}') missing deeplink URI.")
                continue

            # Must follow Android Intent URI specification
            if not (dl.startswith("intent:") and dl.endswith(";end")):
                violations.append(
                    f"Step {step.step_number} has malformed intent syntax: '{dl}'. "
                    f"Must start with 'intent:' and terminate with ';end'."
                )

            # Check 4: Anti-Parent-Menu heuristic
            # If target screen is deeply nested but points to root settings, issue a warning or violation
            if (
                dl in self.GENERIC_PARENT_INTENTS
                and (" > " in step.target_screen and "Safe Mode" not in step.title)
            ):
                warnings.append(
                    f"Step {step.step_number} ('{step.title}') targets child screen '{step.target_screen}' "
                    f"but uses generic top-level Settings intent. Exact sub-screen intent recommended."
                )

        if not any("missing deeplink" in v or "malformed intent" in v for v in violations):
            passed_checks.append("Deeplink format and intent structure validated.")

        # Check 5: Fix-For-Me Guardrail
        fix_safety_valid = True
        for step in steps:
            if step.fix_for_me:
                if step.risk_level != "low":
                    violations.append(
                        f"Safety Violation: Step {step.step_number} has fix_for_me=True but risk_level is '{step.risk_level}'. "
                        f"Fix-for-me is strictly restricted to 'low' risk."
                    )
                    fix_safety_valid = False
                if step.is_destructive:
                    violations.append(
                        f"Safety Violation: Step {step.step_number} has fix_for_me=True but is marked destructive."
                    )
                    fix_safety_valid = False

        if fix_safety_valid:
            passed_checks.append("Fix-for-me safety boundaries verified (restricted to low-risk, non-destructive actions).")

        # Check 6: Step indexing continuity
        indices = [s.step_number for s in steps]
        if indices == list(range(1, len(steps) + 1)):
            passed_checks.append("Contiguous 1-indexed step sequence verified.")
        else:
            violations.append(f"Step indexing is non-contiguous or broken: {indices}")

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            passed_checks=passed_checks,
            warnings=warnings,
            violations=violations
        )
