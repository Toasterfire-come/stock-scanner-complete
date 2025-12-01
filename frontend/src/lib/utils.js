import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// Common null/empty checks shared across components
export function isMissing(value) {
  if (value === null || value === undefined) return true;
  if (typeof value === 'number') return !Number.isFinite(value);
  if (typeof value === 'string') {
    const s = value.trim().toLowerCase();
    return s === '' || s === 'na' || s === 'n/a' || s === 'null' || s === 'undefined';
  }
  return false;
}

export function formatCurrencySafe(value, currency = 'USD', fallback = '—') {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(n);
}

export function formatNumberSafe(value, decimals = 2, fallback = '—') {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return n.toFixed(decimals);
}

// If value in [0,1], treat as fraction; if >1 and <1000, treat as percent
export function formatPercentMaybe(value, fallback = '—') {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  const pct = n > 1 && n < 1000 ? n : n * 100;
  return `${pct.toFixed(2)}%`;
}

