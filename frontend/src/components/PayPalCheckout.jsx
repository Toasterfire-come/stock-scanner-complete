/* eslint-disable react/jsx-no-target-blank */
import React, { useState } from "react";
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { createPayPalOrder, capturePayPalOrder } from "../api/client";

const PayPalCheckout = ({ 
  planType = "bronze", 
  billingCycle = "monthly", 
  discountCode = null,
  onSuccess, 
  onError,
  onCancel 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const planPrices = {
    bronze: { monthly: 24.99, annual: 249.99 },
    silver: { monthly: 39.99, annual: 399.99 },
    gold: { monthly: 89.99, annual: 899.99 }
  };

  const planFeatures = {
    bronze: ["1,500 API calls/month", "Basic alerts", "Email support", "Portfolio tracking"],
    silver: ["5,000 API calls/month", "Advanced alerts", "Priority support", "Custom watchlists"],
    gold: ["Unlimited API calls", "Real-time alerts", "Phone support", "Full API access"]
  };

  const basePrice = planPrices[planType]?.[billingCycle] || 24.99;
  const finalPrice = basePrice;
  const savings = 0;

  // No discount handling in current API contract

  const createOrder = async () => {
    setIsLoading(true);
    try {
      const res = await createPayPalOrder(planType, billingCycle, discountCode || null);
      setIsLoading(false);
      return res?.id || res?.order_id;
    } catch (e) {
      setIsLoading(false);
      setError("Failed to create PayPal order");
      throw e;
    }
  };

  const onApprove = async (data) => {
    setIsLoading(true);
    try {
      const res = await capturePayPalOrder(data.orderID, {});
      onSuccess?.({ paymentDetails: res, planType, billingCycle, finalAmount: finalPrice });
    } catch (err) {
      console.error("Payment processing error:", err);
      onError?.(err);
    } finally {
      setIsLoading(false);
    }
  };

  const paypalOptions = {
    "client-id": process.env.REACT_APP_PAYPAL_CLIENT_ID || "sb-test-client-id-placeholder",
    currency: "USD",
    intent: "capture",
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

        {/* Pricing Summary */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-2">
          <div className="flex justify-between">
            <span>Base Price:</span>
            <span>${basePrice.toFixed(2)}</span>
          </div>
          {/* No discount lines in current contract */}
          <hr />
          <div className="flex justify-between font-bold text-lg">
            <span>Total:</span>
            <span>${finalPrice.toFixed(2)}</span>
          </div>
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
            {/* Default (smart) buttons */}
            <PayPalButtons
              fundingSource={undefined}
              createOrder={() => createOrder()}
              onApprove={onApprove}
              onError={(err) => { console.error("PayPal error:", err); onError?.(err); }}
              onCancel={onCancel}
              disabled={isLoading}
              style={{ layout: "vertical", color: "blue", shape: "rect", label: "paypal" }}
            />

            {/* Pay Later if available */}
            <PayPalButtons
              fundingSource="paylater"
              createOrder={() => createOrder()}
              onApprove={onApprove}
              onError={(err) => { console.error("PayPal PayLater error:", err); onError?.(err); }}
              onCancel={onCancel}
              disabled={isLoading}
              style={{ layout: "vertical", color: "blue", shape: "rect", label: "pay" }}
            />

            {/* Venmo (US only, if eligible) */}
            <PayPalButtons
              fundingSource="venmo"
              createOrder={() => createOrder()}
              onApprove={onApprove}
              onError={(err) => { console.error("Venmo error:", err); onError?.(err); }}
              onCancel={onCancel}
              disabled={isLoading}
              style={{ layout: "vertical", color: "silver", shape: "rect", label: "pay" }}
            />

            {/* Card funding button */}
            <PayPalButtons
              fundingSource="card"
              createOrder={() => createOrder()}
              onApprove={onApprove}
              onError={(err) => { console.error("Card funding error:", err); onError?.(err); }}
              onCancel={onCancel}
              disabled={isLoading}
              style={{ layout: "vertical", color: "silver", shape: "rect", label: "pay" }}
            />
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
            Secure payment processed by PayPal.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default PayPalCheckout;