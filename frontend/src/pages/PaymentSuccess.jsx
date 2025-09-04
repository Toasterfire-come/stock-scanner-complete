import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { CheckCircle, Loader } from "lucide-react";
import { toast } from "sonner";
import { confirmPayment } from "../api/client";
import { Button } from "../components/ui/button";

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  
  const sessionId = searchParams.get('session_id');
  const plan = searchParams.get('plan');

  useEffect(() => {
    if (sessionId && plan) {
      confirmPurchase();
    } else {
      toast.error("Invalid payment session");
      navigate('/pricing');
    }
  }, [sessionId, plan]);

  const confirmPurchase = async () => {
    try {
      const response = await confirmPayment(sessionId, plan);
      if (response.success) {
        setSuccess(true);
        toast.success(`Successfully upgraded to ${plan} plan!`);
      } else {
        toast.error("Failed to confirm payment. Please contact support.");
      }
    } catch (error) {
      toast.error("Error confirming payment");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-lg text-gray-600">Confirming your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-green-50 to-white">
      <div className="max-w-md w-full mx-auto p-8">
        <div className="bg-white rounded-lg shadow-xl p-8 text-center">
          {success ? (
            <>
              <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
              <p className="text-lg text-gray-600 mb-6">
                Your subscription to the <span className="font-semibold capitalize">{plan}</span> plan is now active.
              </p>
              
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">What's Next?</h3>
                <ul className="text-left text-sm text-gray-600 space-y-2">
                  <li>• Access all {plan} plan features immediately</li>
                  <li>• Check your email for payment confirmation</li>
                  <li>• Explore advanced tools in your dashboard</li>
                </ul>
              </div>
              
              <Button 
                className="w-full"
                onClick={() => navigate('/dashboard')}
              >
                Go to Dashboard
              </Button>
            </>
          ) : (
            <>
              <div className="text-red-500 mb-4">
                <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Confirmation Failed</h1>
              <p className="text-gray-600 mb-6">
                We couldn't confirm your payment. This might be temporary. Please try again or contact support if the issue persists.
              </p>
              
              <div className="space-y-3">
                <Button 
                  className="w-full"
                  onClick={() => navigate('/pricing')}
                >
                  Try Again
                </Button>
                <Button 
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate('/support')}
                >
                  Contact Support
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccess;