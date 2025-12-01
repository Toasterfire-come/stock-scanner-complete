import React, { useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { setReferralCookie, normalizeReferralCode } from "../lib/referral";
import { logClientMetric } from "../api/client";
import { buildAttributionTags } from "../lib/analytics";

const DEFAULT_REDIRECT = "/pricing";

export default function ReferralApply({ code: propCode, redirectTo = DEFAULT_REDIRECT }) {
  const navigate = useNavigate();
  const params = useParams();
  const location = useLocation();

  useEffect(() => {
    try {
      const raw = String(propCode || params.code || "");
      const base = raw.replace(/^REF_/i, "");
      const normalized = normalizeReferralCode(base);

      if (normalized) {
        try { setReferralCookie(normalized); } catch {}

        try {
          logClientMetric({
            metric: "referral_click",
            value: 1,
            tags: buildAttributionTags({ code: normalized, path: location.pathname })
          });
        } catch {}

        const nextPath = redirectTo || DEFAULT_REDIRECT;
        const target = `${nextPath}${nextPath.includes("?") ? "&" : "?"}ref=${encodeURIComponent(base)}`;
        navigate(target, { replace: true, state: { discount_code: normalized } });
        return;
      }
    } catch {}

    navigate(redirectTo || DEFAULT_REDIRECT, { replace: true });
  }, [propCode, params.code, redirectTo, navigate, location.pathname]);

  return (
    <div className="p-8 text-center">
      Applying referral…
    </div>
  );
}
