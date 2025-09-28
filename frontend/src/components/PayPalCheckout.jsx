/* eslint-disable react/jsx-no-target-blank */
import React, { useMemo, useState } from "react";
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { changePlan } from "../api/client";

const PayPalCheckout = ({ 
  planType = "bronze", 
  billingCycle = "monthly", 
  discountCode = null,
  paypalPlanId, // optional explicit PayPal subscription plan id
  onSuccess, 
  onError,
  onCancel 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const planId = useMemo(() => {
    if (paypalPlanId) return paypalPlanId;
    const key = `REACT_APP_PAYPAL_PLAN_${String(planType).toUpperCase()}_${billingCycle.toUpperCase()}`;
    return process.env[key];
  }, [planType, billingCycle, paypalPlanId]);

  const createSubscription = async (data, actions) => {
    if (!planId) {
      setError("Subscription cannot be created: missing PayPal plan ID");
      throw new Error("Missing plan_id");
    }
    return actions.subscription.create({ plan_id: planId });
  };

  const onApproveSubscription = async (data, _actions) => {
    setIsLoading(true);
    try {
      // Notify backend about the new subscription to update user plan immediately
      try {
        await changePlan({ plan: planType, billing_cycle: billingCycle, subscription_id: data.subscriptionID, discount_code: discountCode || undefined });
      } catch {}
      onSuccess?.({ subscriptionId: data.subscriptionID, planType, billingCycle });
    } catch (err) {
      onError?.(err);
    } finally {
      setIsLoading(false);
    }
  };

  const paypalOptions = {
    "client-id": process.env.REACT_APP_PAYPAL_CLIENT_ID || "AcqbU_Y_mQK6pdy8hzpPif0UPWrG8_3vi3wxc-cIM2n2PAhdq4kJaq7BO4jUtAvfrYCgvYOzFbsGCHVY",
    currency: "USD",
    intent: "subscription",
    vault: true,
    components: "buttons,marks,messages"
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="capitalize">{planType} Plan</span>
          <Badge variant="secondary" className="capitalize">{billingCycle}</Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Error Section */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Renewal Notice */}
        <div className="bg-blue-50 p-4 rounded-lg text-sm text-blue-900">
          Subscriptions auto‑renew each {billingCycle === 'annual' ? 'year' : 'month'}. You can cancel anytime in Account → Plan & Billing.
        </div>

        {/* PayPal Buttons and alternative funding sources */}
        <div className="space-y-3">
          {isLoading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              <span>Processing payment...</span>
            </div>
          )}
          
          <PayPalScriptProvider options={paypalOptions}>
            {!planId && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Payment temporarily unavailable: missing plan configuration.
                </AlertDescription>
              </Alert>
            )}
            {/* Default subscription button (PayPal Wallet) */}
            <PayPalButtons
              style={{ layout: "vertical", color: "blue", shape: "rect", label: "subscribe" }}
              disabled={isLoading || !planId}
              fundingSource={undefined}
              createSubscription={createSubscription}
              onApprove={onApproveSubscription}
              onError={(err) => { console.error("PayPal subscription error:", err); onError?.(err); }}
              onCancel={onCancel}
            />

            {/* Pay Later if available */}
            {billingCycle === 'annual' && (
              <PayPalButtons
                style={{ layout: "vertical", color: "blue", shape: "rect", label: "pay" }}
                disabled={isLoading || !planId}
                fundingSource="paylater"
                createSubscription={createSubscription}
                onApprove={onApproveSubscription}
                onError={(err) => { console.error("PayPal PayLater subscription error:", err); onError?.(err); }}
                onCancel={onCancel}
              />
            )}
          </PayPalScriptProvider>
        </div>

        {/* Trust Indicators */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center">
              <CheckCircle className="h-3.5 w-3.5 text-green-500 mr-1" />
              7-Day Money Back
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-3.5 w-3.5 text-green-500 mr-1" />
              Cancel Anytime
            </div>
          </div>
          <p className="text-xs text-gray-500">
            By subscribing you agree to automatic renewal per our Terms & Billing Policy.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default PayPalCheckout;