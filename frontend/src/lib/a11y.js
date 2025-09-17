export function initLiveRegion() {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  const ensure = () => document.getElementById('sr-live-region');
  const region = ensure();
  if (!region) return;
  // Expose global announcer
  window.announce = function announce(message) {
    try {
      const r = ensure();
      if (!r) return;
      // Clear then set to trigger screen reader announcement
      r.textContent = '';
      setTimeout(() => { r.textContent = String(message || ''); }, 10);
    } catch {}
  };
}

export function announce(message) {
  try {
    if (typeof window !== 'undefined' && typeof window.announce === 'function') {
      window.announce(message);
    }
  } catch {}
}

