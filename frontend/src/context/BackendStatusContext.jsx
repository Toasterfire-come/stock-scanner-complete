import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { pingHealth } from "../api/client";

const BackendStatusContext = createContext({ isBackendUp: true, lastChecked: null, allowEmergencyAdmin: false });

const EMERGENCY_ADMIN = { email: "authadmin@auth.to", password: "12auth34" };

export const BackendStatusProvider = ({ children, intervalMs = 60000 }) => {
  const [isBackendUp, setIsBackendUp] = useState(true);
  const [lastChecked, setLastChecked] = useState(null);

  useEffect(() => {
    let cancelled = false;
    let timer = null;

    const HEALTH_KEY = 'tsp:lastHealthPingAt';

    const check = async () => {
      // Cross-tab throttle: only one tab performs the ping per minute
      try {
        const now = Date.now();
        const lastPing = Number(localStorage.getItem(HEALTH_KEY) || '0');
        if (now - lastPing < intervalMs) {
          // Too soon: schedule the next check based on remaining time
          const remaining = Math.max(0, intervalMs - (now - lastPing));
          if (!cancelled) timer = setTimeout(check, remaining + 50);
          return;
        }
        // Attempt to claim the ping window
        localStorage.setItem(HEALTH_KEY, String(now));
      } catch (_) {
        // If localStorage fails, proceed without throttle
      }

      try {
        await pingHealth();
        if (!cancelled) setIsBackendUp(true);
      } catch (e) {
        if (!cancelled) setIsBackendUp(false);
      } finally {
        if (!cancelled) setLastChecked(new Date());
        if (!cancelled) timer = setTimeout(check, intervalMs);
      }
    };

    check();
    return () => { cancelled = true; if (timer) clearTimeout(timer); };
  }, [intervalMs]);

  const value = useMemo(() => ({ isBackendUp, lastChecked, allowEmergencyAdmin: !isBackendUp, emergencyAdmin: EMERGENCY_ADMIN }), [isBackendUp, lastChecked]);
  return <BackendStatusContext.Provider value={value}>{children}</BackendStatusContext.Provider>;
};

export const useBackendStatus = () => useContext(BackendStatusContext);