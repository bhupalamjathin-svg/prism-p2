/**
 * PRISM API service layer.
 *
 * This is the ONLY file the UI imports for backend communication.
 * It adapts the PRISM backend response to the format expected by the UI.
 */

const API_BASE_URL = (
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, code, status) {
    super(message);
    this.name = "ApiError";
    this.code = code || "REQUEST_FAILED";
    this.status = status || null;
  }
}

export function isBackendConfigured() {
  return Boolean(API_BASE_URL);
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

async function request(method, path, body) {
  let res;

  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new ApiError(
      "Couldn't reach the PRISM backend. Make sure the backend is running.",
      "NETWORK"
    );
  }

  if (!res.ok) {
    let detail = "";

    try {
      const data = await res.json();
      detail = data?.detail || data?.message || "";
    } catch (_) {
      // Ignore JSON parsing errors
    }

    throw new ApiError(
      detail || `Request failed with status ${res.status}`,
      "HTTP_ERROR",
      res.status
    );
  }

  if (res.status === 204) return null;

  return res.json();
}


/**
 * POST /troubleshoot
 *
 * Converts the frontend's device fields into the PRISM request format,
 * then adapts the PRISM response into the format expected by the UI.
 */
export async function diagnose({
  complaint,
  device_model,
  one_ui_version,
  clarification_answer = null,
}) {
  let finalComplaint = complaint;

  // If the user answered a clarification question, include that answer
  // as additional context for P2.
  if (clarification_answer) {
    finalComplaint = `${complaint}. Clarification: ${clarification_answer}`;
  }

  const result = await request("POST", "/troubleshoot", {
    complaint: finalComplaint,
    device_info: {
      model: device_model,
      one_ui: one_ui_version,
    },
  });

  // PRISM asks for clarification
  if (
    result?.status === "need_clarification" ||
    result?.clarification_needed === true
  ) {
    return {
      diagnosis: null,
      needs_clarification: true,
      clarification_question:
        result.question ||
        "What problem are you experiencing with your phone?",
      clarification_options: result.options || [],
      steps: [],
      served_from_cache: result.cache_hit || false,
      confidence: result.confidence,
      canonical_id: result.canonical_id,
      domain: result.domain,
      symptom: result.symptom,
    };
  }

  // PRISM returned a ready troubleshooting plan
  return {
    diagnosis:
      result.scenario_title ||
      result.symptom ||
      result.canonical_id ||
      "Troubleshooting Plan",

    needs_clarification: false,

    clarification_question: null,

    steps: Array.isArray(result.steps)
      ? result.steps
      : [],

    served_from_cache: result.cache_hit || false,

    confidence: result.confidence,

    canonical_id: result.canonical_id,

    domain: result.domain,

    symptom: result.symptom,

    validation: result.validation,

    plan_id: result.plan_id,
  };
}


/**
 * POST /fix
 *
 * PRISM expects:
 * {
 *   plan_id,
 *   step_id,
 *   action
 * }
 */
export function applyFix({
  step_id,
  device_model,
  one_ui_version,
  plan_id,
}) {
  return request("POST", "/fix", {
    plan_id,
    step_id,
    action: "execute",
  });
}


/*
 * History is intentionally kept local in the current frontend.
 *
 * The PRISM backend does not expose the old /history API.
 * GalaxyCareApp already maintains its own in-memory history.
 */

export function getHistory() {
  return Promise.resolve([]);
}

export function saveHistory(plan) {
  return Promise.resolve(plan);
}

export function clearHistory() {
  return Promise.resolve(null);
}
