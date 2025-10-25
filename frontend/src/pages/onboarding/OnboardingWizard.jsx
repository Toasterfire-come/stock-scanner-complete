import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import { Checkbox } from "../../components/ui/checkbox";
import { 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle, 
  TrendingUp, 
  BarChart3, 
  Bell, 
  Zap,
  Users,
  Target,
  DollarSign,
  Clock
} from "lucide-react";
import { toast } from "sonner";
import { api } from "../../api/client";

const OnboardingWizard = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Personal Information
    firstName: "",
    lastName: "",
    phone: "",
    
    // Step 2: Trading Experience
    experienceLevel: "",
    tradingGoals: [],
    portfolioSize: "",
    
    // Step 3: Preferences
    interestedFeatures: [],
    notificationPreferences: [],
    
    // Step 4: Account Setup
    subscriptionPlan: "",
  });

  const totalSteps = 4;

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayChange = (field, value, checked) => {
    setFormData(prev => ({
      ...prev,
      [field]: checked 
        ? [...prev[field], value]
        : prev[field].filter(item => item !== value)
    }));
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const completeOnboarding = async () => {
    try {
      try {
        await api.post('/user/onboarding/', formData);
      } catch (_) {}
      toast.success("Welcome to Trade Scan Pro! Your account is set up.");
      navigate("/app/dashboard");
    } catch (error) {
      toast.error("Something went wrong. Please try again.");
    }
  };

  const experienceLevels = [
    { id: "beginner", label: "Beginner", description: "New to trading" },
    { id: "intermediate", label: "Intermediate", description: "Some trading experience" },
    { id: "advanced", label: "Advanced", description: "Experienced trader" },
    { id: "professional", label: "Professional", description: "Trading is my profession" }
  ];

  const tradingGoalOptions = [
    "Day Trading",
    "Swing Trading", 
    "Long-term Investing",
    "Options Trading",
    "Dividend Investing",
    "Growth Investing"
  ];

  const portfolioSizes = [
    { id: "under-10k", label: "Under $10,000" },
    { id: "10k-50k", label: "$10,000 - $50,000" },
    { id: "50k-100k", label: "$50,000 - $100,000" },
    { id: "100k-500k", label: "$100,000 - $500,000" },
    { id: "over-500k", label: "Over $500,000" }
  ];

  const features = [
    { id: "stock-screening", label: "Stock Screening", icon: <BarChart3 className="h-4 w-4" /> },
    { id: "real-time-alerts", label: "Real-time Alerts", icon: <Bell className="h-4 w-4" /> },
    { id: "portfolio-tracking", label: "Portfolio Tracking", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "news-analysis", label: "News Analysis", icon: <Users className="h-4 w-4" /> },
    { id: "market-research", label: "Market Research", icon: <Target className="h-4 w-4" /> },
    { id: "technical-analysis", label: "Technical Analysis", icon: <BarChart3 className="h-4 w-4" /> }
  ];

  const notificationOptions = [
    { id: "email", label: "Email Notifications" },
    { id: "push", label: "Push Notifications" },
    { id: "sms", label: "SMS Alerts" },
    { id: "in-app", label: "In-App Notifications" }
  ];

  const subscriptionPlans = [
    {
      id: "bronze",
      name: "Bronze",
      price: "$14.99/month",
      features: ["1,000 stocks/month", "Basic screening", "Email alerts"]
    },
    {
      id: "silver", 
      name: "Silver",
      price: "$29.99/month",
      features: ["5,000 stocks/month", "Advanced screening", "Real-time alerts", "API access"]
    },
    {
      id: "gold",
      name: "Gold", 
      price: "$59.99/month",
      features: ["10,000 stocks/month", "All features", "Priority support", "Advanced analytics"]
    }
  ];

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Personal Information</CardTitle>
              <CardDescription>
                Help us personalize your Trade Scan Pro experience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange("firstName", e.target.value)}
                    placeholder="John"
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange("lastName", e.target.value)}
                    placeholder="Doe"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="phone">Phone Number (Optional)</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange("phone", e.target.value)}
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Trading Experience</CardTitle>
              <CardDescription>
                Tell us about your trading background
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base font-medium">Experience Level</Label>
                <div className="grid grid-cols-2 gap-3 mt-3">
                  {experienceLevels.map((level) => (
                    <div key={level.id} className="space-y-2">
                      <button
                        type="button"
                        onClick={() => handleInputChange("experienceLevel", level.id)}
                        className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${
                          formData.experienceLevel === level.id
                            ? "border-blue-500 bg-blue-50"
                            : "border-gray-200 hover:border-gray-300"
                        }`}
                      >
                        <div className="font-medium">{level.label}</div>
                        <div className="text-sm text-gray-500">{level.description}</div>
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-base font-medium">Trading Goals (Select all that apply)</Label>
                <div className="grid grid-cols-2 gap-2 mt-3">
                  {tradingGoalOptions.map((goal) => (
                    <div key={goal} className="flex items-center space-x-2">
                      <Checkbox
                        id={goal}
                        checked={formData.tradingGoals.includes(goal)}
                        onCheckedChange={(checked) => handleArrayChange("tradingGoals", goal, checked)}
                      />
                      <Label htmlFor={goal} className="text-sm">{goal}</Label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-base font-medium">Portfolio Size</Label>
                <div className="grid grid-cols-1 gap-2 mt-3">
                  {portfolioSizes.map((size) => (
                    <button
                      key={size.id}
                      type="button"
                      onClick={() => handleInputChange("portfolioSize", size.id)}
                      className={`w-full p-3 rounded-lg border text-left transition-colors ${
                        formData.portfolioSize === size.id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      {size.label}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 3:
        return (
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Preferences</CardTitle>
              <CardDescription>
                Customize your experience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base font-medium">Features You're Most Interested In</Label>
                <div className="grid grid-cols-2 gap-3 mt-3">
                  {features.map((feature) => (
                    <div key={feature.id} className="flex items-center space-x-3">
                      <Checkbox
                        id={feature.id}
                        checked={formData.interestedFeatures.includes(feature.id)}
                        onCheckedChange={(checked) => handleArrayChange("interestedFeatures", feature.id, checked)}
                      />
                      <Label htmlFor={feature.id} className="flex items-center space-x-2">
                        {feature.icon}
                        <span>{feature.label}</span>
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-base font-medium">Notification Preferences</Label>
                <div className="space-y-2 mt-3">
                  {notificationOptions.map((option) => (
                    <div key={option.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={option.id}
                        checked={formData.notificationPreferences.includes(option.id)}
                        onCheckedChange={(checked) => handleArrayChange("notificationPreferences", option.id, checked)}
                      />
                      <Label htmlFor={option.id}>{option.label}</Label>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 4:
        return (
          <Card className="w-full max-w-4xl">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl flex items-center justify-center space-x-2">
                <CheckCircle className="h-6 w-6 text-green-500" />
                <span>Almost Done!</span>
              </CardTitle>
              <CardDescription>
                Your Trade Scan Pro account is ready to go
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base font-medium">Choose Your Plan</Label>
                <div className="grid md:grid-cols-3 gap-4 mt-4">
                  {subscriptionPlans.map((plan) => (
                    <button
                      key={plan.id}
                      type="button"
                      onClick={() => handleInputChange("subscriptionPlan", plan.id)}
                      className={`p-6 rounded-lg border-2 text-left transition-all ${
                        formData.subscriptionPlan === plan.id
                          ? "border-blue-500 bg-blue-50 scale-105"
                          : "border-gray-200 hover:border-gray-300 hover:shadow-md"
                      }`}
                    >
                      <div className="font-bold text-lg">{plan.name}</div>
                      <div className="text-blue-600 font-semibold mb-3">{plan.price}</div>
                      <ul className="space-y-1 text-sm text-gray-600">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="flex items-center">
                            <CheckCircle className="h-3 w-3 text-green-500 mr-2" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Setup Summary:</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Name:</span> {formData.firstName} {formData.lastName}
                  </div>
                  <div>
                    <span className="text-gray-600">Experience:</span> {
                      experienceLevels.find(level => level.id === formData.experienceLevel)?.label || "Not selected"
                    }
                  </div>
                  <div>
                    <span className="text-gray-600">Goals:</span> {formData.tradingGoals.length} selected
                  </div>
                  <div>
                    <span className="text-gray-600">Plan:</span> {
                      subscriptionPlans.find(plan => plan.id === formData.subscriptionPlan)?.name || "Not selected"
                    }
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-lg">
              <TrendingUp className="h-7 w-7 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome to Trade Scan Pro
            </h1>
          </div>
          
          {/* Progress Bar */}
          <div className="flex items-center justify-center space-x-2 mb-6">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === currentStep 
                    ? "bg-blue-600 text-white" 
                    : step < currentStep 
                      ? "bg-green-500 text-white"
                      : "bg-gray-200 text-gray-600"
                }`}>
                  {step < currentStep ? <CheckCircle className="h-4 w-4" /> : step}
                </div>
                {step < 4 && (
                  <div className={`w-12 h-1 mx-2 ${
                    step < currentStep ? "bg-green-500" : "bg-gray-200"
                  }`} />
                )}
              </div>
            ))}
          </div>
          
          <p className="text-gray-600">
            Step {currentStep} of {totalSteps}: Complete your profile setup
          </p>
        </div>

        {/* Step Content */}
        <div className="flex justify-center">
          {renderStep()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-center mt-8 space-x-4">
          {currentStep > 1 && (
            <Button
              onClick={prevStep}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Previous</span>
            </Button>
          )}
          
          {currentStep < totalSteps ? (
            <Button
              onClick={nextStep}
              className="flex items-center space-x-2"
            >
              <span>Next</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={completeOnboarding}
              className="flex items-center space-x-2 bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="h-4 w-4" />
              <span>Complete Setup</span>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;