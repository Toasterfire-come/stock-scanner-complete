import React, { useEffect, useMemo, useState } from "react";
import Joyride, { STATUS, EVENTS } from "react-joyride";
import { useLocation, useNavigate } from "react-router-dom";

const TOUR_COMPLETED_KEY = "tsp_product_tour_completed_v1";

export default function ProductTour({ run, onRunChange, autoRunEnabled = true }) {
  const location = useLocation();
  const navigate = useNavigate();

  const isAppRoute = location.pathname.startsWith("/app");

  const [stepIndex, setStepIndex] = useState(0);
  const [autoRun, setAutoRun] = useState(false);

  const steps = useMemo(
    () => [
      {
        target: "body",
        placement: "center",
        title: "Welcome to Trade Scan Pro",
        content: "Here’s a quick tour of the key areas so you can get value fast.",
      },
      {
        target: '[data-testid="quick-actions-button"]',
        title: "Quick Actions",
        content: "Open this menu anytime to jump to the most common actions.",
      },
      {
        target: 'nav[aria-label="Primary"]',
        title: "Mobile Navigation",
        content: "Use the bottom nav to move between key app pages.",
      },
      {
        target: 'a[aria-label="Screeners"]',
        title: "Screeners",
        content: "Scan thousands of stocks using technical and fundamental filters.",
      },
      {
        target: 'a[aria-label="Watchlists"]',
        title: "Watchlists",
        content: "Track your favorite tickers and sets of ideas.",
      },
    ],
    []
  );

  useEffect(() => {
    // Auto-run once on first app visit (can be overridden by the run prop).
    if (!isAppRoute) return;
    if (!autoRunEnabled) return;
    try {
      const completed = localStorage.getItem(TOUR_COMPLETED_KEY) === "true";
      if (!completed) setAutoRun(true);
    } catch {
      // Ignore storage errors.
    }
  }, [autoRunEnabled, isAppRoute]);

  const shouldRun = isAppRoute && (typeof run === "boolean" ? run : (autoRunEnabled && autoRun));

  return (
    <Joyride
      steps={steps}
      run={shouldRun}
      stepIndex={stepIndex}
      continuous
      showSkipButton
      scrollToFirstStep
      disableOverlayClose
      styles={{
        options: {
          primaryColor: "#2563eb",
          zIndex: 10000,
        },
      }}
      callback={(data) => {
        const { status, type, index } = data;

        if (type === EVENTS.STEP_AFTER) {
          setStepIndex(index + 1);
        }

        if (type === EVENTS.TARGET_NOT_FOUND) {
          // Skip steps when the UI element isn't present on the current route/device.
          setStepIndex(index + 1);
        }

        if (type === EVENTS.STEP_BEFORE) {
          // Ensure user is on a sensible app route for steps (especially when started from elsewhere).
          if (!location.pathname.startsWith("/app")) {
            navigate("/app/dashboard");
          }
        }

        if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
          setStepIndex(0);
          setAutoRun(false);
          try {
            localStorage.setItem(TOUR_COMPLETED_KEY, "true");
          } catch {
            // ignore
          }
          if (typeof onRunChange === "function") onRunChange(false);
        }
      }}
    />
  );
}

