# 🤝 Samsung PRISM — P1 & P2 Full Alignment Contract
**P1 Role:** Backend + Catalog Lead  
**P2 Role:** Neural Understanding + Confidence Lead  
**Aligned Repository:** [`https://github.com/bhupalamjathin-svg/prism-p2`](https://github.com/bhupalamjathin-svg/prism-p2)  
**Backend Subdirectory:** `C:\Users\Prekshitha\.gemini\antigravity-ide\scratch\samsung-prism-backend`

---

## ⚡ 1. The P2 ➔ P1 Core Contract

P1 accepts the exact JSON output from P2's `understand()` method at `POST /troubleshoot`.

### A. When P2 is Confident (`status == "ready"`, Confidence $\ge 0.70$)
P2 posts:
```json
{
  "status": "ready",
  "domain": "Battery",
  "symptom": "Excessive Battery Drain",
  "canonical_id": "BATTERY_EXCESSIVE_DRAIN",
  "confidence": 0.95,
  "clarification_needed": false,
  "question": null,
  "options": [],
  "device_info": {
    "model": "Galaxy S24",
    "one_ui": "6.1"
  }
}
```
**P1 Action:**
1. Checks fast-path cache (`< 1 ms`).
2. Applies One UI 6.1 dynamic overrides (e.g. standalone Battery settings intent).
3. Sequences steps monotonically: `low` $\rightarrow$ `medium` $\rightarrow$ `high` $\rightarrow$ `critical`.
4. Attaches `fix_for_me: true` **only** to low-risk, non-destructive steps.
5. Returns `TroubleshootingPlanResponse` with `status: "ready"` to P3.

---

### B. When P2 Needs Clarification (`status == "need_clarification"`, Confidence $< 0.70$)
For vague complaints or multiple competing complaints (e.g. "phone gets hot and battery dies fast"):
```json
{
  "status": "need_clarification",
  "domain": null,
  "symptom": null,
  "canonical_id": null,
  "confidence": 0.45,
  "clarification_needed": true,
  "question": "Which issue should we troubleshoot first?",
  "options": [
    "Battery drains quickly",
    "Phone gets hot",
    "Both"
  ],
  "device_info": {
    "model": "Galaxy S24",
    "one_ui": "6.1"
  }
}
```
**P1 Action:**
P1 gracefully returns this clarification object directly to P3 without crashing or executing unintended actions. P3 displays the question & choice buttons to the user.

---

## 🎯 2. Complete List of All 6 Supported Canonical IDs

P1 now provides dedicated, verified, version-aware troubleshooting plans for **all 6 of P2's canonical IDs**:

| Canonical ID | Domain | Symptom / Issue | Top Deeplink Dispatched | Low-Risk "Fix for me" Available? |
|---|---|---|---|---|
| `BATTERY_EXCESSIVE_DRAIN` | Battery | Rapid battery discharge | `android.intent.action.POWER_USAGE_SUMMARY` | ✅ Yes (Power saving, Background sleep, Protect battery) |
| `BATTERY_NOT_CHARGING` | Battery | Cable / USB moisture / Charging stall | `com.samsung.android.settings.BATTERY_CHARGING_SETTINGS` | ✅ Yes (Toggle fast charging, Power sharing off) |
| `DEVICE_OVERHEATING` | Battery | Thermal throttling / Device warm | `com.samsung.android.sm.ACTION_DEVICE_CARE` | ✅ Yes (Optimize memory, Light mode profile) |
| `DEVICE_SLOW_PERFORMANCE` | Performance | Stutter / App lag / Storage full | `android.settings.INTERNAL_STORAGE_SETTINGS` | ✅ Yes (Device care quick optimize, RAM Plus, Trash bin) |
| `WIFI_CONNECTION_PROBLEM` | Connectivity | Wi-Fi drops / Disconnecting | `android.settings.WIFI_SETTINGS` | ✅ Yes (Wi-Fi toggle, Intelligent Wi-Fi switch off) |
| `DISPLAY_FLICKERING` | Display | Screen blinking / 120Hz glitch | `com.samsung.android.settings.REFRESH_RATE_SETTINGS` | ✅ Yes (Lock 60Hz standard, Adaptive brightness off) |

*(Note: Aliases such as `battery_drain`, `device_slow_performance`, `storage_full_lag` automatically resolve to their canonical counterparts).*

---

## 📱 3. The P1 ➔ P3 Contract (Troubleshooting Plan Output)

When `status == "ready"`, P1 responds with:
```json
{
  "status": "ready",
  "plan_id": "plan_9f8d1c2b4a",
  "canonical_id": "BATTERY_EXCESSIVE_DRAIN",
  "scenario_title": "Resolve Fast Battery Drain & Optimize Power Usage",
  "domain": "Battery",
  "symptom": "Excessive Battery Drain",
  "device": "Galaxy S24",
  "one_ui_version": "6.1",
  "confidence": 0.95,
  "steps": [
    {
      "step_number": 1,
      "step_id": "step_bat_01",
      "action": "check_battery_usage",
      "title": "Inspect Battery Usage & Top Draining Apps",
      "description": "View detailed per-app battery breakdown over the last 24 hours to identify background drain anomalies.",
      "risk_level": "low",
      "fix_for_me": true,
      "is_destructive": false,
      "target_screen": "Settings > Battery > Battery usage",
      "deeplink": "intent:#Intent;action=android.intent.action.POWER_USAGE_SUMMARY;package=com.android.settings;end",
      "execution_type": "automated",
      "version_applied": "One UI 6.1"
    },
    {
      "step_number": 2,
      "step_id": "step_bat_02",
      "action": "enable_power_saving",
      "title": "Enable Power Saving Mode",
      "description": "Restricts CPU speed to 70%, limits background network usage, and decreases display brightness to conserve power.",
      "risk_level": "low",
      "fix_for_me": true,
      "is_destructive": false,
      "target_screen": "Settings > Battery > Power saving",
      "deeplink": "intent:#Intent;action=android.settings.BATTERY_SAVER_SETTINGS;package=com.android.settings;end",
      "execution_type": "automated",
      "version_applied": "One UI 6.1"
    },
    {
      "step_number": 3,
      "step_id": "step_bat_05",
      "action": "clear_google_play_services_cache",
      "title": "Clear Google Play Services Cache",
      "description": "Resolves background sync loops that keep the CPU awake (wakelock battery drain).",
      "risk_level": "medium",
      "fix_for_me": false,
      "is_destructive": false,
      "target_screen": "Settings > Apps > Google Play services > Storage > Clear cache",
      "deeplink": "intent:#Intent;action=android.settings.APPLICATION_DETAILS_SETTINGS;data=package:com.google.android.gms;package=com.android.settings;end",
      "execution_type": "guided_manual",
      "version_applied": "default"
    },
    {
      "step_number": 4,
      "step_id": "step_bat_07",
      "action": "factory_data_reset",
      "title": "Factory Data Reset (Last Resort)",
      "description": "Completely erases all user data, photos, accounts, and downloaded apps to restore device to factory state.",
      "risk_level": "critical",
      "fix_for_me": false,
      "is_destructive": true,
      "target_screen": "Settings > General Management > Reset > Factory data reset",
      "deeplink": "intent:#Intent;action=android.settings.MASTER_CLEAR;package=com.android.settings;end",
      "execution_type": "manual_destructive",
      "version_applied": "default"
    }
  ],
  "total_steps": 4,
  "automated_fixes_count": 2,
  "execution_strategy": "Ascending Risk Monotonic: Non-Destructive Diagnostics -> Safe Configuration -> App Cache Clear -> System Settings Reset -> Factory Recovery",
  "validation": {
    "is_valid": true,
    "passed_checks": [
      "Plan contains non-empty sequence of troubleshooting steps.",
      "Strict monotonic risk ordering verified (low -> medium -> high -> critical).",
      "Deeplink format and intent structure validated.",
      "Fix-for-me safety boundaries verified (restricted to low-risk, non-destructive actions).",
      "Contiguous 1-indexed step sequence verified."
    ],
    "warnings": [],
    "violations": []
  },
  "cache_hit": true,
  "cache_key": "BATTERY_EXCESSIVE_DRAIN:galaxy_s24:6.1",
  "latency_ms": 0.38,
  "generated_at": "2026-09-24T23:00:00Z"
}
```

---

## 🛠️ 4. Semi-Automatic "Fix for me" Action (`POST /fix`)

When user taps "Fix for me" in P3 frontend:
- **Request:**
  ```json
  {
    "step_id": "step_bat_02",
    "action": "enable_power_saving",
    "device_info": { "model": "Galaxy S24", "one_ui": "6.1" }
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "step_id": "step_bat_02",
    "action": "enable_power_saving",
    "deeplink_opened": "intent:#Intent;action=android.settings.BATTERY_SAVER_SETTINGS;package=com.android.settings;end",
    "target_screen": "Settings > Battery > Power saving",
    "status": "applied_successfully",
    "message": "Settings URI dispatched to Galaxy S24 (6.1). Fix applied."
  }
  ```
- **Safety Guarantee:** If called on a medium or critical step, returns `403 Forbidden` (`"strictly forbidden for non-low risk actions"`).
