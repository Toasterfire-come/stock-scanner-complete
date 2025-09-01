import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Textarea } from "../../components/ui/textarea";
import { Checkbox } from "../../components/ui/checkbox";
import { Badge } from "../../components/ui/badge";
import { Progress } from "../../components/ui/progress";
import { toast } from "sonner";
import { 
  User, 
  TrendingUp, 
  Bell, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Target,
  DollarSign,
  BarChart3,
  PieChart,
  AlertTriangle
} from "lucide-react";
import { updateProfile, updateNotificationSettings } from "../../api/client";

const OnboardingWizard = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    firstName: "",
    lastName: "",
    phone: "",
    company: "",
    
    // Step 2: Trading Profile
    experience: "",
    investmentGoals: [],
    riskTolerance: "",
    portfolioSize: "",
    
    // Step 3: Preferences
    notifications: {
      trading: {
        price_alerts: true,
        volume_alerts: false,
        market_hours: true
      },
      portfolio: {
        daily_summary: true,
        weekly_report: true,
        milestone_alerts: true
      },
      news: {
        breaking_news: true,
        earnings_alerts: true,
        analyst_ratings: false
      },
      security: {
        login_alerts: true,
        billing_updates: true,
        plan_updates: true
      }
    },
    interests: []
  });

  const totalSteps = 4;
  const progressPercent = (currentStep / totalSteps) * 100;

  const experienceLevels = [
    { value: "beginner", label: "Beginner", description: "New to trading" },
    { value: "intermediate", label: "Intermediate", description: "Some trading experience" },
    { value: "advanced", label: "Advanced", description: "Experienced trader" },
    { value: "professional", label: "Professional", description: "Professional trader/advisor" }
  ];

  const investmentGoals = [
    { value: "growth", label: "Growth", icon: <TrendingUp className="h-4 w-4" /> },
    { value: "income", label: "Income", icon: <DollarSign className="h-4 w-4" /> },
    { value: "value", label: "Value Investing", icon: <BarChart3 className="h-4 w-4" /> },
    { value: "day-trading", label: "Day Trading", icon: <Target className="h-4 w-4" /> },
    { value: "swing", label: "Swing Trading", icon: <PieChart className="h-4 w-4" /> },
    { value: "long-term", label: "Long-term Hold", icon: <CheckCircle className="h-4 w-4" /> }
  ];

  const riskLevels = [
    { value: "conservative", label: "Conservative", description: "Minimize risk, steady returns" },
    { value: "moderate", label: "Moderate", description: "Balanced risk and return" },
    { value: "aggressive", label: "Aggressive", description: "Higher risk for higher returns" }
  ];

  const portfolioSizes = [
    { value: "under-10k", label: "Under $10K" },
    { value: "10k-50k", label: "$10K - $50K" },
    { value: "50k-100k", label: "$50K - $100K" },
    { value: "100k-500k", label: "$100K - $500K" },
    { value: "over-500k", label: "Over $500K" }
  ];

  const interests = [
    "Technology", "Healthcare", "Finance", "Energy", "Consumer Goods",
    "Real Estate", "Cryptocurrency", "Commodities", "International Markets", "ESG Investing"
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayToggle = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(item => item !== value)
        : [...prev[field], value]
    }));
  };

  const handleNotificationChange = (category, setting, value) => {
    setFormData(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [category]: {
          ...prev.notifications[category],
          [setting]: value
        }
      }
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

  const skipOnboarding = () => {
    navigate("/app/dashboard");
  };

  const completeOnboarding = async () => {
    setIsLoading(true);
    try {
      // Update profile information
      await updateProfile({
        first_name: formData.firstName,
        last_name: formData.lastName,
        phone: formData.phone,
        company: formData.company
      });

      // Update notification settings
      await updateNotificationSettings(formData.notifications);

      toast.success("Welcome to Stock Scanner! Your account is set up.");
      navigate("/app/dashboard");
    } catch (error) {
      toast.error("Failed to complete setup. You can update these later in settings.");
      navigate("/app/dashboard");
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <User className="h-12 w-12 text-blue-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Tell us about yourself
              </h2>
              <p className="text-gray-600">
                Help us personalize your Stock Scanner experience
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name *</Label>
                <Input
                  id="firstName"
                  value={formData.firstName}
                  onChange={(e) => handleInputChange("firstName", e.target.value)}
                  placeholder="John"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name *</Label>
                <Input
                  id="lastName"
                  value={formData.lastName}
                  onChange={(e) => handleInputChange("lastName", e.target.value)}
                  placeholder="Doe"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                value={formData.phone}
                onChange={(e) => handleInputChange("phone", e.target.value)}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="company">Company (Optional)</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => handleInputChange("company", e.target.value)}
                placeholder="Acme Corp"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <TrendingUp className="h-12 w-12 text-blue-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Your Trading Profile
              </h2>
              <p className="text-gray-600">
                Help us understand your investment style and goals
              </p>
            </div>

            <div className="space-y-4">
              <Label>Experience Level</Label>
              <div className="grid grid-cols-2 gap-3">
                {experienceLevels.map((level) => (
                  <Card
                    key={level.value}
                    className={`cursor-pointer transition-colors ${
                      formData.experience === level.value
                        ? "ring-2 ring-blue-500 bg-blue-50"
                        : "hover:bg-gray-50"
                    }`}
                    onClick={() => handleInputChange("experience", level.value)}
                  >
                    <CardContent className="p-4">
                      <div className="font-medium">{level.label}</div>
                      <div className="text-sm text-gray-600">{level.description}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <Label>Investment Goals (Select all that apply)</Label>
              <div className="grid grid-cols-2 gap-3">
                {investmentGoals.map((goal) => (
                  <Card
                    key={goal.value}
                    className={`cursor-pointer transition-colors ${
                      formData.investmentGoals.includes(goal.value)
                        ? "ring-2 ring-blue-500 bg-blue-50"
                        : "hover:bg-gray-50"
                    }`}
                    onClick={() => handleArrayToggle("investmentGoals", goal.value)}
                  >
                    <CardContent className="p-4 flex items-center space-x-3">
                      {goal.icon}
                      <span className="font-medium">{goal.label}</span>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <Label>Risk Tolerance</Label>
              <div className="space-y-2">
                {riskLevels.map((risk) => (
                  <Card
                    key={risk.value}
                    className={`cursor-pointer transition-colors ${
                      formData.riskTolerance === risk.value
                        ? "ring-2 ring-blue-500 bg-blue-50"
                        : "hover:bg-gray-50"
                    }`}
                    onClick={() => handleInputChange("riskTolerance", risk.value)}
                  >
                    <CardContent className="p-4">
                      <div className="font-medium">{risk.label}</div>
                      <div className="text-sm text-gray-600">{risk.description}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Bell className="h-12 w-12 text-blue-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Notification Preferences
              </h2>
              <p className="text-gray-600">
                Choose how you'd like to stay informed
              </p>
            </div>

            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Trading Alerts</CardTitle>
                  <CardDescription>Price movements and market events</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Price Alerts</Label>
                      <p className="text-sm text-gray-600">Get notified when stocks hit your target prices</p>
                    </div>
                    <Checkbox
                      checked={formData.notifications.trading.price_alerts}
                      onCheckedChange={(checked) => 
                        handleNotificationChange("trading", "price_alerts", checked)
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Volume Alerts</Label>
                      <p className="text-sm text-gray-600">Unusual volume activity notifications</p>
                    </div>
                    <Checkbox
                      checked={formData.notifications.trading.volume_alerts}
                      onCheckedChange={(checked) => 
                        handleNotificationChange("trading", "volume_alerts", checked)
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Market Hours</Label>
                      <p className="text-sm text-gray-600">Market open/close notifications</p>
                    </div>
                    <Checkbox
                      checked={formData.notifications.trading.market_hours}
                      onCheckedChange={(checked) => 
                        handleNotificationChange("trading", "market_hours", checked)
                      }
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Portfolio Updates</CardTitle>
                  <CardDescription>Performance and summary reports</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Daily Summary</Label>
                      <p className="text-sm text-gray-600">Daily portfolio performance email</p>
                    </div>
                    <Checkbox
                      checked={formData.notifications.portfolio.daily_summary}
                      onCheckedChange={(checked) => 
                        handleNotificationChange("portfolio", "daily_summary", checked)
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Weekly Report</Label>
                      <p className="text-sm text-gray-600">Comprehensive weekly performance report</p>
                    </div>
                    <Checkbox
                      checked={formData.notifications.portfolio.weekly_report}
                      onCheckedChange={(checked) => 
                        handleNotificationChange("portfolio", "weekly_report", checked)
                      }
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                You're All Set!
              </h2>
              <p className="text-gray-600">
                Your Stock Scanner account is ready to go
              </p>
            </div>

            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <CardContent className="p-6">
                <h3 className="font-semibold text-blue-900 mb-3">What's Next?</h3>
                <ul className="space-y-2 text-blue-800">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Explore live market data and stock analysis
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Create your first stock screener
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Set up your watchlists and price alerts
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Track your portfolio performance
                  </li>
                </ul>
              </CardContent>
            </Card>

            <div className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                You can always update these preferences later in your account settings.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button onClick={completeOnboarding} size="lg" disabled={isLoading}>
                  {isLoading ? "Setting up..." : "Get Started"}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.firstName && formData.lastName;
      case 2:
        return formData.experience && formData.riskTolerance;
      case 3:
        return true;
      case 4:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to Stock Scanner
          </h1>
          <p className="text-gray-600">
            Let's set up your account in just a few steps
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Step {currentStep} of {totalSteps}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={skipOnboarding}
              className="text-gray-500 hover:text-gray-700"
            >
              Skip for now
            </Button>
          </div>
          <Progress value={progressPercent} className="w-full" />
        </div>

        {/* Step Content */}
        <Card className="mb-8">
          <CardContent className="p-8">
            {renderStep()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={currentStep === 1}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>

          {currentStep < totalSteps ? (
            <Button
              onClick={nextStep}
              disabled={!canProceed()}
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={completeOnboarding}
              disabled={isLoading}
            >
              {isLoading ? "Setting up..." : "Complete Setup"}
              <CheckCircle className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;