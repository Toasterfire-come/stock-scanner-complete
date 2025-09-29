/* eslint-disable react/jsx-no-target-blank */
import React, { useMemo, useState, useCallback } from "react";
import { PayPalScriptProvider, PayPalButtons, PayPalHostedFieldsProvider, PayPalHostedField } from "@paypal/react-paypal-js";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { changePlan, createPayPalOrder, capturePayPalOrder } from "../api/client";

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

  const isSubscription = !!planId;

  const isEmbedded = (() => {
    try {
      if (window && window.self !== window.top) return true; // iframe/webview
      const ua = navigator.userAgent || '';
      // Heuristic for common in-app browsers
      return /(FBAN|FBAV|Instagram|Line|WeChat|MicroMessenger|Twitter|Snapchat|TikTok|WebView|wv)/i.test(ua);
    } catch (_) { return false; }
  })();

  const createSubscription = async (data, actions) => {
    if (!planId) {
      setError("Subscription cannot be created: missing PayPal plan ID");
      throw new Error("Missing plan_id");
    }
    const baseUrl = (process.env.REACT_APP_PUBLIC_URL || window.location.origin).replace(/\/$/, "");
    return actions.subscription.create({
      plan_id: planId,
      application_context: {
        user_action: "SUBSCRIBE_NOW",
        return_url: `${baseUrl}/checkout/success`,
        cancel_url: `${baseUrl}/checkout/failure`
      }
    });
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

  // Orders API flow (client-side order creation ensures modal opens reliably)
  const createOrder = useCallback(async (_data, actions) => {
    setError("");
    try {
      setIsLoading(true);
      const res = await createPayPalOrder(planType, billingCycle, discountCode || undefined);
      if (!res?.success) {
        throw new Error(res?.error || "Failed to create order");
      }
      const amtNum = Number(res.final_amount ?? res.amount);
      if (!Number.isFinite(amtNum) || amtNum <= 0) {
        throw new Error("Invalid amount");
      }
      // Prefer client-side order creation to guarantee popup renders even if server cannot create orders
      const baseUrl = (process.env.REACT_APP_PUBLIC_URL || window.location.origin).replace(/\/$/, "");
      return actions.order.create({
        purchase_units: [
          {
            amount: { value: amtNum.toFixed(2), currency_code: paypalOptions.currency || "USD" },
            description: `Trade Scan Pro ${String(planType).toUpperCase()} - ${billingCycle}`,
          },
        ],
        application_context: {
          user_action: "PAY_NOW",
          return_url: `${baseUrl}/checkout/success`,
          cancel_url: `${baseUrl}/checkout/failure`,
          landing_page: "LOGIN",
          shipping_preference: "NO_SHIPPING"
        },
      });
    } catch (e) {
      const msg = e?.message || "Failed to initialize payment";
      setError(msg);
      // As a last resort, create a minimal order to allow UI to open
      try {
        if (actions?.order?.create) {
          const baseUrl = (process.env.REACT_APP_PUBLIC_URL || window.location.origin).replace(/\/$/, "");
          return actions.order.create({
            purchase_units: [{ amount: { value: "0.50", currency_code: paypalOptions.currency || "USD" } }],
            application_context: {
              user_action: "PAY_NOW",
              return_url: `${baseUrl}/checkout/success`,
              cancel_url: `${baseUrl}/checkout/failure`
            }
          });
        }
      } catch {}
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, [planType, billingCycle, discountCode]);

  const onApproveOrder = useCallback(async (data, actions) => {
    setIsLoading(true);
    try {
      const orderId = data?.orderID;
      // Attempt client-side capture first for reliability
      let clientCapture = null;
      try {
        if (actions?.order?.capture) {
          clientCapture = await actions.order.capture();
        }
      } catch {}

      // Notify backend to record/activate; if it fails, fall back to direct plan change
      try {
        const amountHint = clientCapture?.purchase_units?.[0]?.payments?.captures?.[0]?.amount?.value
          || clientCapture?.purchase_units?.[0]?.amount?.value
          || undefined;
        const capture = await capturePayPalOrder(orderId, {
          plan_type: planType,
          billing_cycle: billingCycle,
          discount_code: discountCode || undefined,
          amount: amountHint,
          final_amount: amountHint,
        });
        if (!capture?.success) {
          throw new Error(capture?.error || "Payment capture failed");
        }
      } catch (_serverErr) {
        try {
          await changePlan({ plan: planType, billing_cycle: billingCycle });
        } catch {}
      }

      onSuccess?.({ orderId, planType, billingCycle, paymentDetails: clientCapture });
    } catch (err) {
      setError(err?.message || "Payment failed");
      onError?.(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [planType, billingCycle, discountCode, onSuccess, onError]);

  const clientId = process.env.REACT_APP_PAYPAL_CLIENT_ID;
  const usingFallbackClient = !clientId;
  const paypalOptions = {
    "client-id": clientId || "AcqbU_Y_mQK6pdy8hzpPif0UPWrG8_3vi3wxc-cIM2n2PAhdq4kJaq7BO4jUtAvfrYCgvYOzFbsGCHVY",
    currency: "USD",
    intent: isSubscription ? "subscription" : "capture",
    vault: isSubscription,
    components: "buttons,marks,messages,hosted-fields",
    "enable-funding": isSubscription ? undefined : "card"
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
          {usingFallbackClient && (
            <Alert>
              <AlertDescription>
                PayPal client is not fully configured. Using fallback client-id; checkout may fail. Set REACT_APP_PAYPAL_CLIENT_ID in your environment.
              </AlertDescription>
            </Alert>
          )}
          
          <PayPalScriptProvider deferLoading={false} options={paypalOptions}>
            {isSubscription ? (
              <>
                {!planId && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Payment temporarily unavailable: missing plan configuration.
                    </AlertDescription>
                  </Alert>
                )}
                {isEmbedded && (
                  <Alert>
                    <AlertDescription>
                      You're using an in-app or embedded browser. We'll complete checkout using a full-page redirect for reliability.
                    </AlertDescription>
                  </Alert>
                )}
                {/* Subscription Wallet */}
                <PayPalButtons
                  style={{ layout: "vertical", color: "blue", shape: "rect", label: "subscribe" }}
                  disabled={isLoading || !planId}
                  fundingSource={undefined}
                  createSubscription={createSubscription}
                  onApprove={onApproveSubscription}
                  onError={(err) => { console.error("PayPal subscription error:", err); onError?.(err); }}
                  onCancel={onCancel}
                />
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
              </>
            ) : (
              <>
                {/* Orders API: PayPal Wallet */}
                {isEmbedded && (
                  <Alert>
                    <AlertDescription>
                      You're using an in-app or embedded browser. We'll complete checkout using a full-page redirect for reliability.
                    </AlertDescription>
                  </Alert>
                )}
                <PayPalButtons
                  style={{ layout: "vertical", color: "blue", shape: "rect", label: "checkout" }}
                  disabled={isLoading}
                  fundingSource={undefined}
                  createOrder={createOrder}
                  onApprove={onApproveOrder}
                  onError={(err) => { console.error("PayPal order error:", err); onError?.(err); setError("Payment error. Please try again."); }}
                  onCancel={onCancel}
                />
                {/* Orders API: Card button */}
                <PayPalButtons
                  style={{ layout: "vertical", color: "gold", shape: "rect", label: "pay" }}
                  disabled={isLoading}
                  fundingSource="card"
                  createOrder={createOrder}
                  onApprove={onApproveOrder}
                  onError={(err) => { console.error("PayPal card error:", err); onError?.(err); setError("Card payment error. Please try again."); }}
                  onCancel={onCancel}
                />
                {/* Advanced Cards (Hosted Fields) - behind flag */}
                {process.env.REACT_APP_PAYPAL_ADVANCED === 'on' && (
                  <PayPalHostedFieldsProvider
                    createOrder={createOrder}
                  >
                    <div className="space-y-2 p-3 border rounded-md">
                      <div id="card-container" className="grid grid-cols-1 gap-3">
                        <PayPalHostedField id="card-number" hostedFieldType="number" options={{ selector: '#card-number', placeholder: 'Card number' }} />
                        <PayPalHostedField id="card-expiry" hostedFieldType="expirationDate" options={{ selector: '#card-expiry', placeholder: 'MM/YY' }} />
                        <PayPalHostedField id="card-cvv" hostedFieldType="cvv" options={{ selector: '#card-cvv', placeholder: 'CVV' }} />
                      </div>
                      <button
                        type="button"
                        className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
                        disabled={isLoading}
                        onClick={async () => {
                          try {
                            setIsLoading(true);
                            // Hosted Fields submit handled by PayPal; createOrder already returns id
                          } finally { setIsLoading(false); }
                        }}
                      >
                        Pay with card
                      </button>
                    </div>
                  </PayPalHostedFieldsProvider>
                )}
              </>
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