import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { pingHealth } from "../api/client";

const BackendStatusContext = createContext({ isBackendUp: true, lastChecked: null });

export const BackendStatusProvider = ({ children, intervalMs = 15000 }) => {
  const [isBackendUp, setIsBackendUp] = useState(true);
  const [lastChecked, setLastChecked] = useState(null);

  useEffect(() => {
    let cancelled = false;
    let timer = null;

    const check = async () => {
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

  const value = useMemo(() => ({ isBackendUp, lastChecked }), [isBackendUp, lastChecked]);
  return <BackendStatusContext.Provider value={value}>{children}</BackendStatusContext.Provider>;
};

export const useBackendStatus = () => useContext(BackendStatusContext);