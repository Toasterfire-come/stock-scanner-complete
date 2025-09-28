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
import { Input } from "../../components/ui/input";

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
    const qRef = searchParams.get("ref");
    if (qRef) return sanitizeCode(String(qRef).toUpperCase());
    return "";
  }, [location.state, searchParams]);

  const [plan, setPlan] = useState(String(initialPlan).toLowerCase());
  const [isAnnual, setIsAnnual] = useState(String(initialCycle).toLowerCase() === "annual");
  const [promo, setPromo] = useState("");
  const [applied, setApplied] = useState(null);
  const [applying, setApplying] = useState(false);
  const [meta, setMeta] = useState(null);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [metaError, setMetaError] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth/sign-in?redirect=/checkout", { replace: true });
    }
  }, [isAuthenticated, navigate]);

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
                name: 'Bronze',
                monthly_price: 24.99,
                annual_list_price: bronzeAnnual,
                annual_final_price: discountAnnual(bronzeAnnual),
                paypal_plan_ids: {
                  monthly: process.env.REACT_APP_PAYPAL_PLAN_BRONZE_MONTHLY || '',
                  annual: process.env.REACT_APP_PAYPAL_PLAN_BRONZE_ANNUAL || '',
                },
              },
              silver: {
                name: 'Silver',
                monthly_price: 49.99,
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
    if (applied?.final_amount != null) return Number(applied.final_amount);
    return displayPrice != null ? Number(displayPrice) : null;
  }, [applied, displayPrice]);
  const nextPrice = useMemo(() => {
    if (!planMeta) return null;
    if (applied?.code === 'TRIAL') return Number(planMeta.monthly_price);
    if (isAnnual) return Number(planMeta.annual_final_price ?? planMeta.annual_list_price);
    return Number(planMeta.monthly_price);
  }, [planMeta, applied, isAnnual]);
  const nextDate = useMemo(() => {
    const d = new Date();
    if (applied?.code === 'TRIAL') d.setDate(d.getDate() + 7);
    else if (isAnnual) d.setDate(d.getDate() + 365);
    else d.setDate(d.getDate() + 30);
    return d;
  }, [applied, isAnnual]);

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

        <div className="grid md:grid-cols-2 gap-6">
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Plan Summary</CardTitle>
              <CardDescription>Confirm your plan and billing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">Selected Plan</div>
                <div className="font-semibold">{PLAN_NAMES[plan] || plan}</div>
              </div>
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">Billing Cycle</div>
                <div className="flex items-center gap-3">
                  <Label className={!isAnnual ? "text-gray-900 font-medium" : "text-gray-600"}>Monthly</Label>
                  <Switch checked={isAnnual} onCheckedChange={setIsAnnual} />
                  <Label className={isAnnual ? "text-gray-900 font-medium" : "text-gray-600"}>Annual</Label>
                </div>
              </div>
              <div className="mt-3 space-y-1 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Today</span>
                  <span className="font-semibold">{todayAmount != null ? `$${todayAmount.toFixed(2)}` : '-'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Next billing</span>
                  <span className="font-semibold">{nextPrice != null ? `$${nextPrice.toFixed(2)}` : '-'} on {nextDate ? nextDate.toLocaleDateString() : '-'}</span>
                </div>
              </div>
              <div>
                <Label htmlFor="promo" className="text-sm text-gray-600">Promo Code (optional)</Label>
                <Input id="promo" placeholder="PROMO2025" value={promo} onChange={(e) => setPromo(sanitizeCode(e.target.value))} />
                <div className="text-xs text-gray-500 mt-1">Letters, numbers, dash and underscore only.</div>
                <div className="mt-2 flex gap-2">
                  <Button size="sm" variant="outline" disabled={!promo || applying || !planMeta} onClick={async () => {
                    try {
                      setApplying(true);
                      const amount = isAnnual ? planMeta.annual_final_price : planMeta.monthly_price;
                      const { data } = await api.post('/billing/apply-discount/', { code: promo, billing_cycle: isAnnual ? 'annual' : 'monthly', amount });
                      if (data?.success) {
                        setApplied({
                          code: data.code,
                          final_amount: data.final_amount,
                          original_amount: data.original_amount,
                          savings_percentage: data.savings_percentage,
                          message: data.message,
                        });
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
                      <div className="text-gray-500 text-xs">Next year: ${Number(planMeta.annual_list_price).toFixed(2)} (before annual discount)</div>
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
                paypalPlanId={planMeta?.paypal_plan_ids?.[isAnnual ? 'annual' : 'monthly'] || ''}
                onSuccess={(info) => {
                  try {
                    const amount = info?.paymentDetails?.amount || info?.paymentDetails?.purchase_units?.[0]?.payments?.captures?.[0]?.amount?.value || undefined;
                    navigate('/checkout/success', { replace: true, state: { planId: plan, amount, discount: (promo || referralCode) ? { code: (promo || referralCode) } : undefined } });
                  } catch {
                    navigate('/checkout/success', { replace: true, state: { planId: plan } });
                  }
                }}
                onError={() => {
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

