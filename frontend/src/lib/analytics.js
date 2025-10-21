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

// Matomo minimal integration (idempotent). Set REACT_APP_MATOMO_URL and REACT_APP_MATOMO_SITE_ID
let matomoBooted = false;
export function initMatomo() {
  try {
    const baseUrl = (process.env.REACT_APP_MATOMO_URL || '').trim();
    const siteId = (process.env.REACT_APP_MATOMO_SITE_ID || '').trim();
    if (!baseUrl || !siteId || matomoBooted) return false;
    window._paq = window._paq || [];
    window._paq.push(['trackPageView']);
    window._paq.push(['enableLinkTracking']);
    (function() {
      const u = baseUrl.endsWith('/') ? baseUrl : (baseUrl + '/');
      window._paq.push(['setTrackerUrl', u + 'matomo.php']);
      window._paq.push(['setSiteId', siteId]);
      const d = document, g = d.createElement('script'), s = d.getElementsByTagName('script')[0];
      g.async = true; g.src = u + 'matomo.js'; s.parentNode.insertBefore(g, s);
    })();
    matomoBooted = true; return true;
  } catch { return false; }
}

export function matomoTrackEvent(category, action, name, value) {
  try {
    window._paq = window._paq || [];
    window._paq.push(['trackEvent', category, action, name, value]);
  } catch {}
}

export function matomoTrackPageView(title) {
  try {
    window._paq = window._paq || [];
    if (title) window._paq.push(['setDocumentTitle', title]);
    window._paq.push(['trackPageView']);
  } catch {}
}

