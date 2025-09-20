import React, { useEffect, useState } from 'react';

export default function LatencyIndicator() {
  const [pending, setPending] = useState(0);
  const [slow, setSlow] = useState(null);
  const [noBackend, setNoBackend] = useState(false);

  useEffect(() => {
    const bus = window.__NET;
    if (!bus) return;
    const onStart = () => setPending((p) => p + 1);
    const onEnd = () => setPending((p) => Math.max(0, p - 1));
    const onSlow = (e) => { setSlow({ ts: Date.now(), ...e }); };
    bus.on('start', onStart);
    bus.on('end', onEnd);
    bus.on('slow', onSlow);
    return () => { bus.off('start', onStart); bus.off('end', onEnd); bus.off('slow', onSlow); };
  }, []);

  useEffect(() => {
    try {
      const base = (process.env.REACT_APP_BACKEND_URL || '').trim();
      setNoBackend(!base);
    } catch { setNoBackend(true); }
  }, []);

  const showBar = pending > 0;
  const showSlow = slow && Date.now() - slow.ts < 5000; // show last 5s

  return (
    <>
      {showBar && <div className="fixed top-0 left-0 right-0 h-0.5 bg-primary animate-pulse z-50" />}
      {showSlow && (
        <div className="fixed top-1 right-2 z-50 text-[11px] px-2 py-1 rounded bg-yellow-100 text-yellow-800 border border-yellow-200 shadow">
          Slow API: {Math.round(slow.duration)}ms
        </div>
      )}
      {noBackend && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
          <div className="px-3 py-1 rounded bg-red-600 text-white text-xs shadow">Backend URL not configured</div>
        </div>
      )}
    </>
  );
}