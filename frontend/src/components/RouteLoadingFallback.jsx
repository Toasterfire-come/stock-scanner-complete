import React from "react";
import { Loader2 } from "lucide-react";

function usePrefersReducedMotion() {
  const [reduced, setReduced] = React.useState(false);
  React.useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = () => setReduced(!!mq.matches);
    onChange();
    if (mq.addEventListener) mq.addEventListener("change", onChange);
    else mq.addListener(onChange);
    return () => {
      if (mq.removeEventListener) mq.removeEventListener("change", onChange);
      else mq.removeListener(onChange);
    };
  }, []);
  return reduced;
}

export default function RouteLoadingFallback({ label = "Loading" }) {
  const reducedMotion = usePrefersReducedMotion();
  return (
    <div className="min-h-[60vh] w-full flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-3 text-sm text-muted-foreground">
          <Loader2 className={`h-4 w-4 ${reducedMotion ? "" : "animate-spin"}`} aria-hidden="true" />
          <span>{label}…</span>
        </div>

        <div className={`mt-8 space-y-4 ${reducedMotion ? "" : "animate-pulse"}`} aria-hidden="true">
          <div className="h-8 w-2/3 rounded bg-muted" />
          <div className="h-4 w-full rounded bg-muted" />
          <div className="h-4 w-5/6 rounded bg-muted" />
          <div className="h-4 w-4/6 rounded bg-muted" />
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="h-20 rounded bg-muted" />
            <div className="h-20 rounded bg-muted" />
          </div>
        </div>
      </div>
    </div>
  );
}

