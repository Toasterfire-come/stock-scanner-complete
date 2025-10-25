// Referral tracking utilities

export function normalizeReferralCode(raw) {
  if (!raw || typeof raw !== 'string') return '';
  const trimmed = raw.trim().slice(0, 32);
  if (!/^[A-Za-z0-9_-]{2,32}$/.test(trimmed)) return '';
  const upper = trimmed.toUpperCase();
  return upper.startsWith('REF_') ? upper : `REF_${upper}`;
}

export function getReferralFromCookie() {
  try {
    const m = document.cookie.match(/(?:^|; )referral_code=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  } catch {
    return '';
  }
}

export function setReferralCookie(code) {
  try {
    const norm = normalizeReferralCode(code);
    if (!norm) return false;
    const maxAgeDays = 90;
    const maxAge = maxAgeDays * 24 * 60 * 60;
    document.cookie = `referral_code=${encodeURIComponent(norm)}; Max-Age=${maxAge}; Path=/; SameSite=Lax`;
    return true;
  } catch {
    return false;
  }
}

export function getReferralMonth() {
  try {
    return new Date().toISOString().slice(0, 7); // YYYY-MM
  } catch {
    return '';
  }
}

