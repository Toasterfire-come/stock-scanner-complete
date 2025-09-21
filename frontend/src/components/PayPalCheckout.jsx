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
      const res = await createPayPalOrder(planType, billingCycle);
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
    intent: "capture"
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="capitalize">{planType} Plan</span>
          <Badge variant="secondary" className="capitalize">{billingCycle}</Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Plan Features */}
        <div>
          <h4 className="font-semibold mb-3">Plan Features:</h4>
          <ul className="space-y-2">
            {planFeatures[planType]?.map((feature, index) => (
              <li key={index} className="flex items-center text-sm">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                {feature}
              </li>
            ))}
          </ul>
        </div>

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
          {billingCycle === "annual" && (
            <p className="text-sm text-gray-600 text-center">
              Save {Math.round((1 - (planPrices[planType].annual / (planPrices[planType].monthly * 12))) * 100)}% with annual billing
            </p>
          )}
        </div>

        {/* PayPal Buttons */}
        <div className="space-y-3">
          {isLoading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              <span>Processing payment...</span>
            </div>
          )}
          
          <PayPalScriptProvider options={paypalOptions}>
            <PayPalButtons
              createOrder={() => createOrder()}
              onApprove={onApprove}
              onError={(err) => {
                console.error("PayPal error:", err);
                onError?.(err);
              }}
              onCancel={onCancel}
              disabled={isLoading}
              style={{
                layout: "vertical",
                color: "blue",
                shape: "rect",
                label: "paypal"
              }}
            />
          </PayPalScriptProvider>
        </div>

        {/* Trust Indicators */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
              7-Day Money Back
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
              Cancel Anytime
            </div>
          </div>
          <p className="text-xs text-gray-500">
            Secure payment processed by PayPal
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default PayPalCheckout;