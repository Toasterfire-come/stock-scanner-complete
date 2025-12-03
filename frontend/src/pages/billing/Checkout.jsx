import React, { useMemo, useState, useEffect } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Label } from "../../components/ui/label";
import { Switch } from "../../components/ui/switch";
import PayPalCheckout from "../../components/PayPalCheckout";
import { useAuth } from "../../context/SecureAuthContext";
import { api } from "../../api/client";
import { setReferralCookie, normalizeReferralCode } from "../../lib/referral";
import { getEnvPromos, matchPromo, validatePromoFor, computePromoFinalAmount, getPromoFromCookie, setPromoCookie, normalizePromoCode } from "../../lib/promos";
import { Input } from "../../components/ui/input";
import { logClientMetric } from "../../api/client";
import { buildAttributionTags } from "../../lib/analytics";
import { getNextMonthFirstUTC } from "../../lib/dates";

const PLAN_NAMES = {
  free: "Free",
  bronze: "Bronze",
  silver: "Silver",
  gold: "Gold",
};

export default function Checkout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();

  const sanitizeCode = (v) => {
    if (!v || typeof v !== 'string') return '';
    const trimmed = v.trim().slice(0, 32);
    return /^[A-Za-z0-9_\-]+$/.test(trimmed) ? trimmed : '';
  };

  const initialPlan = useMemo(() => {
    const st = location.state || {};
    return st.plan || searchParams.get("plan") || "bronze";
  }, [location.state, searchParams]);

  const initialCycle = useMemo(() => {
    const st = location.state || {};
    return st.cycle || searchParams.get("cycle") || "monthly";
  }, [location.state, searchParams]);

  const referralCode = useMemo(() => {
    const st = location.state || {};
    if (st.discount_code && typeof st.discount_code === "string") return sanitizeCode(st.discount_code);
    const keysEnv = (process.env.REACT_APP_REFERRAL_QUERY_KEYS || "ref,referral,ref_code,coupon,code,campaign,utm_campaign").split(",").map(k => k.trim()).filter(Boolean);
    for (const key of keysEnv) {
      const val = searchParams.get(key);
      if (val) {
        return sanitizeCode(String(val).toUpperCase());
      }
    }
    // Fallback: try to extract from UTM-style sources like utm_source=ref-<CODE>
    const utmSource = searchParams.get("utm_source") || "";
    const m = String(utmSource).toUpperCase().match(/REF[-_]?([A-Z0-9_-]{2,32})/);
    if (m && m[1]) return sanitizeCode(m[1]);
    return "";
  }, [location.state, searchParams]);

  const [plan, setPlan] = useState(String(initialPlan).toLowerCase());
  const [isAnnual, setIsAnnual] = useState(String(initialCycle).toLowerCase() === "annual");
  const [promo, setPromo] = useState("");
  const promos = useMemo(() => getEnvPromos(), []);
  // Prefill promo with referral code when available
  useEffect(() => {
    // Load PayPal SDK only when checkout is in viewport
    const lazy = process.env.REACT_APP_LAZY_PAYPAL === 'on';
    if (!lazy) return;
    const el = document.querySelector('#paypal-section');
    if (!el || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          window.paypalLoadScript?.();
          observer.disconnect();
        }
      });
    }, { rootMargin: '200px' });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  
  useEffect(() => {
    if (!promo && referralCode) setPromo(referralCode);
  }, [referralCode, promo]);

  // Load promo from cookie if present
  useEffect(() => {
    try {
      const fromCookie = getPromoFromCookie();
      if (fromCookie && !promo) setPromo(fromCookie);
    } catch {}
  }, []);

  // Persist referral code for attribution
  useEffect(() => {
    try {
      if (referralCode) setReferralCookie(normalizeReferralCode(referralCode));
    } catch {}
  }, [referralCode]);
  const [applied, setApplied] = useState(null);
  const [applying, setApplying] = useState(false);
  const [meta, setMeta] = useState(null);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [metaError, setMetaError] = useState("");

  // Auto-apply 50% off for a valid REF_* referral on monthly cycle when server code doesn't return a discount
  useEffect(() => {
    try {
      if (!referralCode) return;
      if (isAnnual) return; // referral only for first month
      if (applied?.code) return; // server-applied or already set
      const isRef = /^REF_[A-Z0-9_-]{5,32}$/.test(referralCode);
      if (!isRef) return;
      if (!meta) return; // need pricing to compute
      const currentPlan = String(plan).toLowerCase();
      const pm = meta?.plans?.[currentPlan];
      if (!pm || pm.monthly_price == null) return;
      const amount = Number(pm.monthly_price);
      if (!Number.isFinite(amount) || amount <= 0) return;
      const finalAmount = Number((amount * 0.5).toFixed(2));
      setApplied({
        code: referralCode,
        final_amount: finalAmount,
        original_amount: amount,
        savings_percentage: 50,
        message: 'Referral (50% off first month)'
      });
    } catch {}
  }, [referralCode, isAnnual, meta, plan, applied]);

  // Allow checkout to load even if not authenticated so pricing and PayPal can initialize

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        setLoadingMeta(true);
        const { data } = await api.get('/billing/plans-meta/');
        if (isMounted) {
          if (data?.success) setMeta(data.data); else setMetaError('Failed to load pricing');
        }
      } catch (e) {
        // Fallback local meta when API is unavailable (e.g., 404)
        if (isMounted) {
          const pct = 15;
          const bronzeAnnual = 299.99, silverAnnual = 599.99, goldAnnual = 959.99;
          const discountAnnual = (v) => Number((v * 0.85).toFixed(2));
          setMeta({
            currency: 'USD',
            discounts: { annual_percent: pct },
            plans: {
              bronze: {
                name: 'Basic',
                monthly_price: 15,
                annual_list_price: bronzeAnnual,
                annual_final_price: discountAnnual(bronzeAnnual),
                paypal_plan_ids: {
                  monthly: process.env.REACT_APP_PAYPAL_PLAN_BRONZE_MONTHLY || '',
                  annual: process.env.REACT_APP_PAYPAL_PLAN_BRONZE_ANNUAL || '',
                },
              },
              silver: {
                name: 'Plus',
                monthly_price: 25,
                annual_list_price: silverAnnual,
                annual_final_price: discountAnnual(silverAnnual),
                paypal_plan_ids: {
                  monthly: process.env.REACT_APP_PAYPAL_PLAN_SILVER_MONTHLY || '',
                  annual: process.env.REACT_APP_PAYPAL_PLAN_SILVER_ANNUAL || '',
                },
              },
              gold: {
                name: 'Gold',
                monthly_price: 79.99,
                annual_list_price: goldAnnual,
                annual_final_price: discountAnnual(goldAnnual),
                paypal_plan_ids: {
                  monthly: process.env.REACT_APP_PAYPAL_PLAN_GOLD_MONTHLY || '',
                  annual: process.env.REACT_APP_PAYPAL_PLAN_GOLD_ANNUAL || '',
                },
              },
            },
          });
          setMetaError('');
        }
      } finally {
        if (isMounted) setLoadingMeta(false);
      }
    })();
    return () => { isMounted = false; };
  }, []);

  const cycle = isAnnual ? "annual" : "monthly";
  const planMeta = meta?.plans?.[plan] || null;
  const displayPrice = (() => {
    if (!planMeta) return null;
    return isAnnual ? planMeta.annual_final_price : planMeta.monthly_price;
  })();

  // Billing amounts and dates
  const todayAmount = useMemo(() => {
    // Priority: server-applied promo
    if (applied?.final_amount != null) return Number(applied.final_amount);
    // Frontend env promo application
    try {
      if (displayPrice != null) {
        const envPromo = matchPromo(promo, promos) || matchPromo(getPromoFromCookie(), promos);
        if (envPromo) {
          const { valid } = validatePromoFor(plan, isAnnual ? 'annual' : 'monthly', envPromo);
          if (valid) {
            const final = computePromoFinalAmount(envPromo, displayPrice);
            if (final != null) return Number(final);
          }
        }
      }
    } catch {}
    return displayPrice != null ? Number(displayPrice) : null;
  }, [applied, displayPrice, promo, promos, plan, isAnnual]);
  const nextPrice = useMemo(() => {
    if (!planMeta) return null;
    if (applied?.code === 'TRIAL') return Number(planMeta.monthly_price);
    if (isAnnual) return Number(planMeta.annual_final_price ?? planMeta.annual_list_price);
    return Number(planMeta.monthly_price);
  }, [planMeta, applied, isAnnual]);
  const nextDate = useMemo(() => {
    // Trial until next 1st of the month
    const d = getNextMonthFirstUTC(new Date());
    return d;
  }, []);

  // Prefer plan IDs from local env over backend meta when available
  const envPlanId = useMemo(() => {
    const envKey = `REACT_APP_PAYPAL_PLAN_${String(plan).toUpperCase()}_${(isAnnual ? 'annual' : 'monthly').toUpperCase()}`;
    return process.env[envKey] || '';
  }, [plan, isAnnual]);

  // Force Orders API (one-time) when today's amount differs from base price (e.g., TRIAL/promos)
  const useOrdersAPI = useMemo(() => {
    try {
      if (displayPrice == null || todayAmount == null) return false;
      const base = Number(displayPrice);
      const today = Number(todayAmount);
      if (!Number.isFinite(base) || !Number.isFinite(today)) return false;
      return Math.abs(today - base) > 0.009; // discount applied
    } catch { return false; }
  }, [displayPrice, todayAmount]);

  return (
    <div className="container mx-auto px-4 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <Badge variant="secondary" className="mb-3">Secure Checkout</Badge>
          <h1 className="text-3xl font-bold text-gray-900">Complete your upgrade</h1>
          {planMeta && (
            <p className="mt-2 text-gray-600">
              {planMeta.name} • {isAnnual ? 'Annual' : 'Monthly'} • ${displayPrice?.toFixed(2)} {isAnnual && meta?.discounts?.annual_percent ? <span className="text-green-600">(includes {meta.discounts.annual_percent}% off)</span> : null}
            </p>
          )}
          {referralCode && (
            <div className="mt-3 text-sm text-blue-900 bg-blue-50 border border-blue-200 inline-flex items-center px-3 py-2 rounded">
              Referral applied: {referralCode}
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6" id="paypal-section">
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Plan Summary</CardTitle>
              <CardDescription>Confirm your plan and billing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between sm:flex-nowrap flex-wrap gap-2">
                <div className="text-sm text-gray-600">Selected Plan</div>
                <div className="font-semibold">{PLAN_NAMES[plan] || plan}</div>
              </div>
              <div className="flex items-center justify-between sm:flex-nowrap flex-wrap gap-3">
                <div className="text-sm text-gray-600">Billing Cycle</div>
                <div className="flex items-center gap-3">
                  <Label className={!isAnnual ? "text-gray-900 font-medium" : "text-gray-600"}>Monthly</Label>
                  <Switch checked={isAnnual} onCheckedChange={setIsAnnual} />
                  <Label className={isAnnual ? "text-gray-900 font-medium" : "text-gray-600"}>Annual</Label>
                </div>
              </div>
              <div className="mt-3 space-y-1 text-sm">
                <div className="flex items-center justify-between sm:flex-nowrap flex-wrap gap-2">
                  <span className="text-gray-600">Today</span>
                  <span className="font-semibold">{todayAmount != null ? `$${todayAmount.toFixed(2)}` : '-'}</span>
                </div>
                <div className="flex items-center justify-between sm:flex-nowrap flex-wrap gap-2">
                  <span className="text-gray-600">Next billing</span>
                  <span className="font-semibold">{nextPrice != null ? `$${nextPrice.toFixed(2)}` : '-'} on {nextDate ? nextDate.toLocaleDateString() : '-'}</span>
                </div>
              </div>
              <div>
                <Label htmlFor="promo" className="text-sm text-gray-600">Promo Code (optional)</Label>
                <Input id="promo" placeholder="PROMO2025" value={promo} onChange={(e) => setPromo(sanitizeCode(e.target.value))} className="w-full" />
                <div className="text-xs text-gray-500 mt-1">Letters, numbers, dash and underscore only.</div>
                <div className="mt-2 flex gap-2">
                  <Button size="sm" variant="outline" disabled={!promo || applying || !planMeta} onClick={async () => {
                    try {
                      setApplying(true);
                      const amount = isAnnual ? planMeta.annual_final_price : planMeta.monthly_price;
                      // Try server validation first
                      const { data } = await api.post('/billing/apply-discount/', { code: promo, billing_cycle: isAnnual ? 'annual' : 'monthly', amount });
                      if (data?.success && data?.applies_discount) {
                        setApplied({
                          code: data.code,
                          final_amount: data.final_amount,
                          original_amount: data.original_amount,
                          savings_percentage: data.savings_percentage,
                          message: data.message,
                        });
                        try { setPromoCookie(promo); } catch {}
                      } else {
                        // Frontend env fallback
                        const envPromo = matchPromo(promo, promos);
                        const { valid } = validatePromoFor(plan, isAnnual ? 'annual' : 'monthly', envPromo);
                        if (envPromo && valid) {
                          const final = computePromoFinalAmount(envPromo, amount);
                          if (final != null) {
                            setApplied({
                              code: envPromo.code,
                              final_amount: final,
                              original_amount: amount,
                              savings_percentage: envPromo.type === 'percent' ? envPromo.amount : undefined,
                              message: 'Promo applied',
                            });
                            try { setPromoCookie(envPromo.code); } catch {}
                          } else {
                            setApplied(null);
                          }
                        } else {
                          setApplied(null);
                        }
                      }
                    } catch (e) {
                      setApplied(null);
                    } finally {
                      setApplying(false);
                    }
                  }}>Apply</Button>
                </div>
                {applied && (
                  <div className="mt-3 text-sm">
                    <div className="text-green-700">Code {applied.code} applied.</div>
                    <div className="text-gray-700">
                      Today: ${Number(applied.final_amount).toFixed(2)}{isAnnual ? ' (annual)' : ' (monthly)'}
                    </div>
                    {!isAnnual && (
                      <div className="text-gray-500 text-xs">Next month: ${Number(applied.original_amount).toFixed(2)}</div>
                    )}
                  {isAnnual && (
                    <div className="text-gray-500 text-xs">Next year: ${Number(planMeta.annual_final_price ?? planMeta.annual_list_price).toFixed(2)} on {nextDate ? nextDate.toLocaleDateString() : '-'}</div>
                  )}
                  </div>
                )}
              </div>
              <div className="text-xs text-gray-500">
                You can cancel your plan anytime from Account → Plan & Billing.
              </div>
            </CardContent>
          </Card>

          {/* Payment */}
          <Card>
            <CardHeader>
              <CardTitle>Pay with PayPal</CardTitle>
              <CardDescription>Fast, secure checkout with multiple payment options</CardDescription>
            </CardHeader>
            <CardContent>
              <PayPalCheckout
                planType={plan}
                billingCycle={cycle}
                discountCode={(applied?.code || promo || referralCode) || null}
                paypalPlanId={useOrdersAPI ? '' : (envPlanId || (planMeta?.paypal_plan_ids?.[isAnnual ? 'annual' : 'monthly'] || ''))}
                onSuccess={(info) => {
                  try {
                    const amount = info?.paymentDetails?.amount || info?.paymentDetails?.purchase_units?.[0]?.payments?.captures?.[0]?.amount?.value || undefined;
                    try { logClientMetric({ metric: 'checkout_success', value: 1, tags: buildAttributionTags({ plan, cycle, promo: (!!(promo||referralCode)).toString() }) }); } catch {}
                    navigate('/checkout/success', { replace: true, state: { planId: plan, amount, discount: (promo || referralCode) ? { code: (promo || referralCode) } : undefined } });
                  } catch {
                    try { logClientMetric({ metric: 'checkout_success', value: 1, tags: buildAttributionTags({ plan, cycle, promo: (!!(promo||referralCode)).toString(), parsing:'failed' }) }); } catch {}
                    navigate('/checkout/success', { replace: true, state: { planId: plan } });
                  }
                }}
                onError={() => {
                  try { logClientMetric({ metric: 'checkout_error', value: 1, tags: buildAttributionTags({ plan, cycle }) }); } catch {}
                  navigate('/checkout/failure', { replace: true });
                }}
                onCancel={() => {}}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

