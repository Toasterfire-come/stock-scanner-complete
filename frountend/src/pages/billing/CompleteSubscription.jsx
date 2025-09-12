import React, { Suspense, useEffect, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Gift, ArrowLeft } from "lucide-react";
import { initializeDiscountCodes } from "../../api/client";

const PayPalCheckout = React.lazy(() => import("../../components/PayPalCheckout"));

const CompleteSubscription = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Read selected plan and cycle from router state or query params
  const statePlan = location.state?.planType;
  const stateCycle = location.state?.billingCycle;
  const searchParams = new URLSearchParams(location.search);
  const planTypeFromQuery = searchParams.get("plan") || undefined;
  const cycleFromQuery = searchParams.get("cycle") || undefined;

  const planType = (statePlan || planTypeFromQuery || "bronze").toLowerCase();
  const billingCycle = (stateCycle || cycleFromQuery || "monthly").toLowerCase();

  useEffect(() => {
    // Ensure discount codes exist on backend (idempotent)
    (async () => { try { await initializeDiscountCodes(); } catch {} })();
  }, []);

  const title = useMemo(() => {
    const planName = planType.charAt(0).toUpperCase() + planType.slice(1);
    const cycleLabel = billingCycle === "annual" ? "Annual" : "Monthly";
    return `Complete Your Subscription · ${planName} · ${cycleLabel}`;
  }, [planType, billingCycle]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-10">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-6">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" /> Back to pricing
          </Button>
        </div>

        <div className="text-center mb-8">
          <div className="inline-flex items-center bg-yellow-100 text-yellow-800 px-5 py-2 rounded-full font-medium text-base border border-yellow-200">
            <Gift className="h-4 w-4 mr-2" />
            Use code TRIAL for a 7‑day $1 trial · REF50 for 50% off first month
          </div>
          <h1 className="mt-5 text-3xl md:text-4xl font-bold text-gray-900">{title}</h1>
          <p className="mt-3 text-gray-600">Secure checkout powered by PayPal</p>
        </div>

        <Card className="shadow-xl">
          <CardContent className="p-6">
            <Suspense fallback={<div className="py-10 text-center">Loading checkout…</div>}>
              <PayPalCheckout
                planType={planType}
                billingCycle={billingCycle}
                onSuccess={() => navigate("/checkout/success")}
                onError={() => {}}
                onCancel={() => navigate("/pricing")}
              />
            </Suspense>
            <div className="mt-6">
              <Alert>
                <AlertDescription>
                  You can change plans or cancel anytime. Discounts are applied during checkout when valid.
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CompleteSubscription;

