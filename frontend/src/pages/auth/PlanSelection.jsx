import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/SecureAuthContext";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Check, Crown, Zap, Star } from "lucide-react";

const plans = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for getting started",
    features: [
      "50 API calls per month",
      "10 API calls per day",
      "Basic stock screening",
      "Email support",
    ],
    icon: Star,
    color: "gray",
  },
  {
    id: "bronze",
    name: "Bronze",
    price: "$1",
    period: "trial",
    description: "Great for individual traders",
    features: [
      "2,000 API calls per month",
      "100 API calls per day",
      "Advanced screening tools",
      "Real-time alerts",
      "Priority support",
    ],
    icon: Zap,
    color: "orange",
    popular: true,
  },
  {
    id: "silver",
    name: "Silver",
    price: "$29",
    period: "month",
    description: "Perfect for professional traders",
    features: [
      "10,000 API calls per month",
      "500 API calls per day",
      "All screening tools",
      "Custom alerts",
      "Portfolio tracking",
      "Premium support",
    ],
    icon: Crown,
    color: "blue",
  },
  {
    id: "gold",
    name: "Gold",
    price: "$99",
    period: "month",
    description: "For trading teams and institutions",
    features: [
      "Unlimited API calls",
      "All premium features",
      "Custom integrations",
      "Dedicated support",
      "Team collaboration",
      "Advanced analytics",
    ],
    icon: Crown,
    color: "yellow",
  },
];

export default function PlanSelection() {
  const navigate = useNavigate();
  const { user, updateUser } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState("bronze");
  const [isLoading, setIsLoading] = useState(false);

  const handlePlanSelect = async (planId) => {
    setIsLoading(true);
    
    try {
      if (planId === "free") {
        // Keep user on free plan and go to app
        updateUser({ plan: 'free' });
        navigate('/app/dashboard', { replace: true });
        return;
      }

      // For paid plans, send to pricing page to choose cycle and checkout
      navigate('/pricing', { state: { fromSignup: true, selectedPlan: planId } });
    } catch (error) {
      console.error("Plan selection error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-lg text-gray-600">
            Select the perfect plan for your trading needs
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const isSelected = selectedPlan === plan.id;
            
            return (
              <Card 
                key={plan.id} 
                className={`relative cursor-pointer transition-all duration-200 ${
                  isSelected ? "ring-2 ring-blue-500 shadow-lg" : "hover:shadow-md"
                } ${plan.popular ? "border-orange-200" : ""}`}
                onClick={() => setSelectedPlan(plan.id)}
              >
                {plan.popular && (
                  <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-orange-500">
                    Most Popular
                  </Badge>
                )}
                
                <CardHeader className="text-center pb-4">
                  <div className={`w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center ${
                    plan.color === "gray" ? "bg-gray-100" :
                    plan.color === "orange" ? "bg-orange-100" :
                    plan.color === "blue" ? "bg-blue-100" : "bg-yellow-100"
                  }`}>
                    <Icon className={`w-6 h-6 ${
                      plan.color === "gray" ? "text-gray-600" :
                      plan.color === "orange" ? "text-orange-600" :
                      plan.color === "blue" ? "text-blue-600" : "text-yellow-600"
                    }`} />
                  </div>
                  
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="text-3xl font-bold text-gray-900">
                    {plan.price}
                    <span className="text-sm font-normal text-gray-500">
                      /{plan.period}
                    </span>
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                
                <CardContent>
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="w-4 h-4 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Button
                    className={`w-full mt-6 ${
                      isSelected 
                        ? "bg-blue-600 hover:bg-blue-700" 
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePlanSelect(plan.id);
                    }}
                    disabled={isLoading}
                  >
                    {isSelected ? "Select This Plan" : "Choose Plan"}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="text-center mt-12">
          <p className="text-sm text-gray-500">
            You can change your plan anytime from your account settings
          </p>
        </div>
      </div>
    </div>
  );
}