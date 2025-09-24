import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PayPalCheckout from "../../components/PayPalCheckout";
import { changePlan, getCurrentPlan } from "../../api/client";
import { useAuth } from "../../context/SecureAuthContext";

const Checkout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { updateUser } = useAuth();

  const planType = (location.state?.planId || "bronze").toLowerCase();
  const billingCycle = location.state?.billingCycle === "annual" ? "annual" : "monthly";

  const handleSuccess = async ({ paymentDetails, planType, billingCycle }) => {
    try {
      await changePlan({ plan_type: planType, billing_cycle: billingCycle });
      try {
        const current = await getCurrentPlan();
        if (current?.success && current.data?.plan_type) {
          updateUser({ plan: current.data.plan_type });
        } else {
          updateUser({ plan: planType });
        }
      } catch {
        updateUser({ plan: planType });
      }
    } catch {}
    navigate("/checkout/success", { state: { planId: planType, amount: paymentDetails?.amount || undefined } });
  };

  const handleError = () => {
    navigate("/checkout/failure");
  };

  const handleCancel = () => {
    navigate("/pricing");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 flex items-center justify-center p-4">
      <PayPalCheckout 
        planType={planType} 
        billingCycle={billingCycle} 
        onSuccess={handleSuccess} 
        onError={handleError} 
        onCancel={handleCancel}
      />
    </div>
  );
};

export default Checkout;

