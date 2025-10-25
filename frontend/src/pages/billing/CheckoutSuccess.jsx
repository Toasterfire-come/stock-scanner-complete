import React, { useEffect } from "react";
import { trackEvent } from "../../lib/analytics";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { CheckCircle, ArrowRight, Download, Mail } from "lucide-react";
import { toast } from "sonner";
// Removed recordPayment; relying on backend capture
import { useAuth } from "../../context/SecureAuthContext";

const CheckoutSuccess = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { updateUser } = useAuth();
  
  const { planId, amount, originalAmount, discount } = location.state || {};
  const numericAmount = typeof amount === 'number' ? amount : Number(amount || 0);
  const numericOriginal = typeof originalAmount === 'number' ? originalAmount : Number(originalAmount || 0);
  const hasSavings = Number.isFinite(numericOriginal) && Number.isFinite(numericAmount) && numericOriginal > numericAmount;
  const discountAmount = hasSavings ? (numericOriginal - numericAmount) : 0;

  useEffect(() => {
    if (planId && planId !== 'free') {
      updateUser({ plan: planId });
    }
    toast.success("Payment successful! Welcome to your new plan.");
    try {
      if (planId) {
        trackEvent('purchase', {
          transaction_id: `plan_${planId}_${Date.now()}`,
          value: Number.isFinite(numericAmount) ? Number(numericAmount) : undefined,
          currency: 'USD',
          items: [{ item_id: planId, item_name: planNames[planId] || planId }]
        });
      }
    } catch {}
  }, [planId]);

  // Redirect if no payment data
  useEffect(() => {
    if (!planId || !amount) {
      navigate("/pricing");
    }
  }, [planId, amount, navigate]);

  const planNames = {
    pro: "Professional",
    enterprise: "Enterprise",
    free: "Free",
    bronze: "Bronze",
    silver: "Silver",
    gold: "Gold",
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50/50 to-blue-50/50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Payment Successful!
          </h1>
          <p className="text-gray-600">
            Thank you for upgrading to Trade Scan Pro {planNames[planId] || 'Premium'}
          </p>
        </div>

        {/* Payment Details Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Payment Summary
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Completed
              </Badge>
            </CardTitle>
            <CardDescription>
              Payment processed on {new Date().toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Plan:</span>
              <span className="font-semibold">Trade Scan Pro {planNames[planId]}</span>
            </div>
            
            {(discount || hasSavings) && (
              <>
                {hasSavings && (
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-gray-600">Original Amount:</span>
                    <span className="line-through text-gray-500">${numericOriginal.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between items-center py-2 border-b">
                  <span className="text-gray-600">Discount{discount?.code ? ` (${discount.code})` : ''}:</span>
                  <span className="text-green-600">-${hasSavings ? discountAmount.toFixed(2) : (discount?.discount_amount || '0.00')}</span>
                </div>
              </>
            )}
            
            <div className="flex justify-between items-center py-2 text-lg font-semibold">
              <span>Total Paid:</span>
              <span className="text-green-600">${amount}</span>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg mt-4">
              <p className="text-sm text-blue-800">
                <Mail className="h-4 w-4 inline mr-2" />
                A receipt has been sent to your email address.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Next Steps */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>What's Next?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <p className="font-medium">Your account has been upgraded</p>
                <p className="text-sm text-gray-600">All premium features are now available</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <p className="font-medium">Access to real-time data</p>
                <p className="text-sm text-gray-600">Live market feeds and advanced analytics</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <p className="font-medium">Premium support</p>
                <p className="text-sm text-gray-600">Priority email and chat support</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="grid sm:grid-cols-2 gap-4 mb-6">
          <Button asChild className="w-full">
            <Link to="/app/screeners/new?template=getting-started">
              Run Getting Started Screener
              <ArrowRight className="h-4 w-4 ml-2" />
            </Link>
          </Button>
          
          <Button asChild variant="outline" className="w-full">
            <Link to="/account/billing">
              <Download className="h-4 w-4 mr-2" />
              Download Receipt
            </Link>
          </Button>
        </div>

        {/* Help Section */}
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">
            Need help getting started?
          </p>
          <div className="flex justify-center space-x-4">
            <Button asChild variant="ghost" size="sm">
              <Link to="/docs">View Documentation</Link>
            </Button>
            <Button asChild variant="ghost" size="sm">
              <Link to="/contact">Contact Support</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutSuccess;