// REQUIREMENT: REQ-OWASP-001, REQ-HIPAA-002 — Client utilities with input validation and secure transport
/**
 * VitalSync Client Utilities — browser/Node.js helper for API consumers.
 *
 * This small JS module is included to demonstrate Sentrik's multi-language
 * scanning capability (OWASP rules apply to JS as well).
 */

// FINDING: Hardcoded API endpoint (should be configurable)
const API_BASE = "http://localhost:8080/api";

// FINDING: No HTTPS — using HTTP for medical data
async function fetchPatientVitals(patientId, token) {
  const response = await fetch(`${API_BASE}/vitals/patient/${patientId}`, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// FINDING: eval() usage (OWASP — injection)
function applyDynamicFilter(data, filterExpression) {
  return data.filter((item) => eval(filterExpression));
}

// FINDING: innerHTML usage (OWASP — XSS)
function renderAlert(alert, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = `
    <div class="alert alert-${alert.severity}">
      <strong>${alert.metric}:</strong> ${alert.message}
    </div>
  `;
}

// Safe utility functions
function formatVitalValue(metric, value) {
  const units = {
    heart_rate: "bpm",
    systolic_bp: "mmHg",
    diastolic_bp: "mmHg",
    spo2: "%",
    temperature: "°C",
    respiratory_rate: "/min",
    blood_glucose: "mg/dL",
  };
  return `${value} ${units[metric] || ""}`;
}

function classifyAlertSeverity(alerts) {
  const counts = { critical: 0, warning: 0, info: 0 };
  for (const alert of alerts) {
    const sev = alert.severity || "info";
    counts[sev] = (counts[sev] || 0) + 1;
  }
  return counts;
}

module.exports = {
  fetchPatientVitals,
  applyDynamicFilter,
  renderAlert,
  formatVitalValue,
  classifyAlertSeverity,
};
