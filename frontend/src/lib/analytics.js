import { getReferralFromCookie, normalizeReferralCode, getReferralMonth } from "./referral";

export function buildAttributionTags(extra = {}) {
  try {
    const raw = getReferralFromCookie();
    const ref = normalizeReferralCode(raw);
    const month = getReferralMonth();
    const tags = { ...extra };
    if (ref) tags.referral = ref;
    if (month) tags.month = month;
    return tags;
  } catch {
    return { ...extra };
  }
}

/* Lightweight GA4 loader and helpers (idempotent) */

let initialized = false;
let gaId = null;

export function getGaMeasurementId() {
  return (
    process.env.REACT_APP_GA_MEASUREMENT_ID ||
    process.env.REACT_APP_GA4_ID ||
    process.env.REACT_APP_GA_ID ||
    ''
  ).trim();
}

export function initAnalytics() {
  if (initialized) return gaId;
  gaId = getGaMeasurementId();
  if (!gaId) return '';

  try {
    if (!window.dataLayer) window.dataLayer = [];
    if (!window.gtag) {
      window.gtag = function(){ window.dataLayer.push(arguments); };
    }

    // Inject script if not present
    const src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(gaId)}`;
    const exists = Array.from(document.scripts || []).some(s => (s.src || '').includes('/gtag/js'));
    if (!exists) {
      const s = document.createElement('script');
      s.async = true; s.src = src; document.head.appendChild(s);
    }

    // Configure with manual page_view
    window.gtag('js', new Date());
    window.gtag('config', gaId, { send_page_view: false });
    initialized = true;
  } catch {}
  return gaId;
}

export function trackPageView(path, title) {
  if (!gaId) gaId = getGaMeasurementId();
  if (!gaId || typeof window.gtag !== 'function') return;
  try {
    const location = `${window.location.origin}${path || window.location.pathname}`;
    window.gtag('event', 'page_view', {
      page_location: location,
      page_path: path || window.location.pathname,
      page_title: title || document.title,
    });
  } catch {}
}

export function trackEvent(name, params = {}) {
  if (!gaId) gaId = getGaMeasurementId();
  if (!gaId || typeof window.gtag !== 'function') return;
  try { window.gtag('event', name, params); } catch {}
}

