// Frontend promo code parsing and validation from env

function tryParseJson(str) {
  try { return JSON.parse(str); } catch { return null; }
}

export function normalizePromoCode(raw) {
  if (!raw || typeof raw !== 'string') return '';
  const trimmed = raw.trim().slice(0, 32);
  if (!/^[A-Za-z0-9_-]{2,32}$/.test(trimmed)) return '';
  return trimmed.toUpperCase();
}

export function getEnvPromos() {
  const raw = process.env.REACT_APP_PROMO_CODES || '';
  if (!raw) return [];
  // Prefer JSON format
  const parsed = tryParseJson(raw);
  if (Array.isArray(parsed)) {
    return parsed
      .map(p => ({
        code: normalizePromoCode(p.code),
        type: (p.type || 'percent').toLowerCase(),
        amount: Number(p.amount || 0),
        applies: (p.applies || 'any').toLowerCase(), // monthly|annual|any
        plans: (Array.isArray(p.plans) ? p.plans : String(p.plans || 'any').split(',')).map(s => String(s || '').trim().toLowerCase()),
        expires: p.expires ? new Date(p.expires) : null,
        stack_with_referral: !!p.stack_with_referral,
      }))
      .filter(p => p.code && Number.isFinite(p.amount) && p.amount >= 0);
  }
  // Fallback semi-colon/comma delimited: CODE:type:amount:applies:plans:expires;...
  return String(raw).split(/[;,]/).map(item => item.trim()).filter(Boolean).map(item => {
    const parts = item.split(':').map(s => s.trim());
    const [code, type, amount, applies, plans, expires] = parts;
    return {
      code: normalizePromoCode(code),
      type: String(type || 'percent').toLowerCase(),
      amount: Number(amount || 0),
      applies: String(applies || 'any').toLowerCase(),
      plans: String(plans || 'any').split('|').map(s => s.trim().toLowerCase()),
      expires: expires ? new Date(expires) : null,
      stack_with_referral: false,
    };
  }).filter(p => p.code && Number.isFinite(p.amount) && p.amount >= 0);
}

export function matchPromo(code, promos) {
  const norm = normalizePromoCode(code);
  if (!norm) return null;
  for (const p of promos) {
    if (!p || !p.code) continue;
    if (p.code.endsWith('*')) {
      const prefix = p.code.slice(0, -1);
      if (norm.startsWith(prefix)) return p;
    } else if (p.code === norm) {
      return p;
    }
  }
  return null;
}

export function validatePromoFor(planType, cycle, promo) {
  try {
    if (!promo) return { valid: false, reason: 'not_found' };
    if (promo.expires && Number.isFinite(promo.expires.getTime())) {
      if (Date.now() > promo.expires.getTime()) return { valid: false, reason: 'expired' };
    }
    const lcPlan = String(planType || '').toLowerCase();
    const lcCycle = String(cycle || 'monthly').toLowerCase();
    if (promo.applies !== 'any' && promo.applies !== lcCycle) return { valid: false, reason: 'cycle' };
    const plans = Array.isArray(promo.plans) ? promo.plans : [];
    if (plans.length > 0 && plans[0] !== 'any' && !plans.includes(lcPlan)) return { valid: false, reason: 'plan' };
    return { valid: true };
  } catch {
    return { valid: false };
  }
}

export function computePromoFinalAmount(promo, baseAmount) {
  const amt = Number(baseAmount || 0);
  if (!Number.isFinite(amt) || amt <= 0) return null;
  if (!promo) return null;
  if (promo.type === 'fixed') {
    // Fixed today price
    return Number(promo.amount);
  }
  // Percent
  const percent = Math.max(0, Math.min(100, Number(promo.amount)));
  return Number((amt * (1 - percent / 100)).toFixed(2));
}

export function getPromoFromCookie() {
  try {
    const m = document.cookie.match(/(?:^|; )promo_code=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  } catch { return ''; }
}

export function setPromoCookie(code) {
  try {
    const norm = normalizePromoCode(code);
    if (!norm) return false;
    const maxAgeDays = 30;
    const maxAge = maxAgeDays * 24 * 60 * 60;
    document.cookie = `promo_code=${encodeURIComponent(norm)}; Max-Age=${maxAge}; Path=/; SameSite=Lax`;
    return true;
  } catch { return false; }
}

