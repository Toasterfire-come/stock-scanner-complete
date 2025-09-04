import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Check, Star, Zap, Shield } from "lucide-react";
import { toast } from "sonner";
import { getPricingPlans, createCheckoutSession } from "../api/client";

const PricingPlans = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Check if user came from signup flow
  const isFromSignup = location.state?.fromSignup || false;

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await getPricingPlans();
      if (response.success) {
        setPlans(response.plans);
      } else {
        toast.error("Failed to load pricing plans");
      }
    } catch (error) {
      toast.error("Error loading pricing plans");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = async (plan) => {
    setSelectedPlan(plan.id);
    
    if (plan.id === 'free') {
      // For free plan, just redirect to dashboard
      toast.success("Welcome! You're on the Free plan");
      navigate('/dashboard');
    } else {
      // For paid plans, create checkout session
      try {
        const response = await createCheckoutSession(plan.id);
        if (response.success && response.checkout_url) {
          // Redirect to Stripe checkout
          window.location.href = response.checkout_url;
        } else {
          toast.error("Failed to create checkout session");
        }
      } catch (error) {
        toast.error("Error processing payment");
      }
    }
  };

  const getPlanIcon = (planName) => {
    switch(planName.toLowerCase()) {
      case 'basic':
        return <Star className="w-8 h-8" />;
      case 'pro':
        return <Zap className="w-8 h-8" />;
      case 'enterprise':
        return <Shield className="w-8 h-8" />;
      default:
        return null;
    }
  };

  const getPlanColor = (planName) => {
    switch(planName.toLowerCase()) {
      case 'basic':
        return 'border-blue-500 bg-blue-50';
      case 'pro':
        return 'border-purple-500 bg-purple-50';
      case 'enterprise':
        return 'border-orange-500 bg-orange-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {isFromSignup ? 'Choose Your Plan' : 'Pricing Plans'}
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {isFromSignup 
              ? 'Start with our free plan or unlock premium features with a paid subscription'
              : 'Select the perfect plan for your stock analysis needs'
            }
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {plans.map((plan) => (
            <Card 
              key={plan.id} 
              className={`relative p-6 hover:shadow-xl transition-all duration-300 ${
                plan.id === 'pro' ? 'ring-2 ring-purple-500 transform scale-105' : ''
              } ${getPlanColor(plan.name)}`}
            >
              {plan.id === 'pro' && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-purple-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}
              
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                  {getPlanIcon(plan.name)}
                </div>
                
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-900">
                    ${plan.price}
                  </span>
                  {plan.price > 0 && (
                    <span className="text-gray-600 ml-2">/month</span>
                  )}
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <Button 
                className={`w-full ${
                  plan.id === 'pro' 
                    ? 'bg-purple-600 hover:bg-purple-700' 
                    : plan.id === 'enterprise'
                    ? 'bg-orange-600 hover:bg-orange-700'
                    : plan.id === 'basic'
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
                onClick={() => handleSelectPlan(plan)}
                disabled={selectedPlan === plan.id}
              >
                {selectedPlan === plan.id 
                  ? 'Processing...' 
                  : plan.price === 0 
                  ? 'Start Free' 
                  : `Get ${plan.name}`
                }
              </Button>
            </Card>
          ))}
        </div>

        {/* Comparison Table */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">Feature Comparison</h2>
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Feature</th>
                  {plans.map(plan => (
                    <th key={plan.id} className="px-6 py-4 text-center text-sm font-semibold text-gray-900">
                      {plan.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-700">Stock Search</td>
                  <td className="px-6 py-4 text-center">Basic</td>
                  <td className="px-6 py-4 text-center">Advanced</td>
                  <td className="px-6 py-4 text-center">Advanced</td>
                  <td className="px-6 py-4 text-center">Advanced</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-700">Watchlist Items</td>
                  <td className="px-6 py-4 text-center">5</td>
                  <td className="px-6 py-4 text-center">Unlimited</td>
                  <td className="px-6 py-4 text-center">Unlimited</td>
                  <td className="px-6 py-4 text-center">Unlimited</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-700">Real-time Data</td>
                  <td className="px-6 py-4 text-center">❌</td>
                  <td className="px-6 py-4 text-center">❌</td>
                  <td className="px-6 py-4 text-center">✅</td>
                  <td className="px-6 py-4 text-center">✅</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-700">API Access</td>
                  <td className="px-6 py-4 text-center">❌</td>
                  <td className="px-6 py-4 text-center">❌</td>
                  <td className="px-6 py-4 text-center">Limited</td>
                  <td className="px-6 py-4 text-center">Unlimited</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-700">Support</td>
                  <td className="px-6 py-4 text-center">Community</td>
                  <td className="px-6 py-4 text-center">Email</td>
                  <td className="px-6 py-4 text-center">Priority</td>
                  <td className="px-6 py-4 text-center">24/7 Phone</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Skip option for signup flow */}
        {isFromSignup && (
          <div className="text-center mt-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-600 hover:text-gray-800 underline"
            >
              Skip for now and continue with Free plan
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PricingPlans;