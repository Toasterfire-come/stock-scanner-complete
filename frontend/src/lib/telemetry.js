import { logClientMetric } from "../api/client";

export function trackEvent(eventName, payload = {}) {
  try {
    logClientMetric({ event: eventName, ...payload });
  } catch {}
}

export function trackError(eventName, error, extra = {}) {
  try {
    const message = error?.message || String(error || 'Unknown error');
    logClientMetric({ event: eventName, level: 'error', message, ...extra });
  } catch {}
}

