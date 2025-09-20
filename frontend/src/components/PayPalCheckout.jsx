import React, { useState } from "react";
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { validateDiscountCode, applyDiscountCode, recordPayment } from "../api/client";

const PayPalCheckout = ({ 
  planType = "bronze", 
  billingCycle = "monthly", 
  onSuccess, 
  onError,
  onCancel 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [discountCode, setDiscountCode] = useState("");
  const [discount, setDiscount] = useState(null);
  const [error, setError] = useState("");
  const [isValidatingDiscount, setIsValidatingDiscount] = useState(false);

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
  const finalPrice = discount ? basePrice - (basePrice * discount.discount_percentage / 100) : basePrice;
  const savings = discount ? basePrice - finalPrice : 0;

  const validateDiscount = async () => {
    if (!discountCode.trim()) return;
    
    setIsValidatingDiscount(true);
    setError("");
    
    try {
      const result = await validateDiscountCode(discountCode);
      if (result.valid && result.applies_discount) {
        setDiscount(result);
      } else {
        setError(result.message || "Invalid discount code");
        setDiscount(null);
      }
    } catch (err) {
      setError("Failed to validate discount code");
      setDiscount(null);
    } finally {
      setIsValidatingDiscount(false);
    }
  };

  const createOrder = (data, actions) => {
    return actions.order.create({
      purchase_units: [{
        amount: {
          value: finalPrice.toFixed(2),
          currency_code: "USD"
        },
        description: `Trade Scan Pro ${planType.charAt(0).toUpperCase() + planType.slice(1)} Plan - ${billingCycle}`,
        custom_id: `${planType}_${billingCycle}_${Date.now()}`
      }],
      application_context: {
        brand_name: "Trade Scan Pro",
        user_action: "PAY_NOW"
      }
    });
  };

  const onApprove = async (data, actions) => {
    setIsLoading(true);
    try {
      const details = await actions.order.capture();
      
      // Apply discount if present
      let discountData = null;
      if (discount) {
        discountData = await applyDiscountCode(discountCode, basePrice);
      }
      
      // Record payment in your backend
      const paymentRecord = await recordPayment({
        user_id: 1, // This should come from auth context
        amount: finalPrice,
        discount_code: discountCode || null,
        payment_date: new Date().toISOString(),
        paypal_transaction_id: details.id,
        plan_type: planType,
        billing_cycle: billingCycle
      });

      onSuccess?.({
        paymentDetails: details,
        discountApplied: discountData,
        paymentRecord: paymentRecord,
        planType,
        billingCycle,
        finalAmount: finalPrice
      });
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

        {/* Discount Code Section */}
        <div className="space-y-3">
          <h4 className="font-semibold">Discount Code (Optional):</h4>
          <div className="flex space-x-2">
            <input
              type="text"
              value={discountCode}
              onChange={(e) => setDiscountCode(e.target.value.toUpperCase())}
              placeholder="Enter code (e.g., REF50)"
              className="flex-1 px-3 py-2 border rounded-md text-sm"
              disabled={isValidatingDiscount}
            />
            <Button 
              onClick={validateDiscount}
              disabled={!discountCode.trim() || isValidatingDiscount}
              size="sm"
              variant="outline"
            >
              {isValidatingDiscount ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Apply"
              )}
            </Button>
          </div>
          
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {discount && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>{discount.code}</strong> applied! {discount.discount_percentage}% off
              </AlertDescription>
            </Alert>
          )}
        </div>

        {/* Pricing Summary */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-2">
          <div className="flex justify-between">
            <span>Base Price:</span>
            <span>${basePrice.toFixed(2)}</span>
          </div>
          {savings > 0 && (
            <div className="flex justify-between text-green-600">
              <span>Discount:</span>
              <span>-${savings.toFixed(2)}</span>
            </div>
          )}
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
              createOrder={createOrder}
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