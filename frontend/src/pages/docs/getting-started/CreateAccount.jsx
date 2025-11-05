import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Alert, AlertDescription } from "../../../components/ui/alert";
import { 
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  Mail,
  Shield,
  Clock,
  AlertCircle,
  UserPlus,
  CreditCard
} from "lucide-react";
import { Link } from "react-router-dom";

const CreateAccount = () => {
  const steps = [
    {
      number: "01",
      title: "Visit the Sign-Up Page",
      description: "Navigate to our registration page and choose your preferred sign-up method.",
      details: [
        "Click 'Try Now for Free' from any page on our website",
        "You'll be redirected to our secure registration form",
        "Choose between email registration or social login options"
      ],
      tips: "We recommend using your primary email address for account notifications and security updates."
    },
    {
      number: "02", 
      title: "Enter Your Information",
      description: "Provide your basic details and create a secure password.",
      details: [
        "Enter your full name and email address",
        "Create a strong password (8+ characters with mixed case, numbers, symbols)",
        "Confirm your password to ensure accuracy",
        "Agree to our Terms of Service and Privacy Policy"
      ],
      tips: "Use a unique password that you don't use for other accounts. Consider using a password manager."
    },
    {
      number: "03",
      title: "Verify Your Email",
      description: "Check your inbox for a verification email and click the confirmation link.",
      details: [
        "Check your email inbox (and spam folder) for our verification message",
        "Click the 'Verify Email' button in the email",
        "You'll be redirected back to Trade Scan Pro to continue setup",
        "If you don't receive the email within 5 minutes, check your spam folder"
      ],
      tips: "Email verification is required for account security and to receive important alerts."
    },
    {
      number: "04",
      title: "Choose Your Plan",
      description: "Select the subscription plan that best fits your trading needs.",
      details: [
        "Review our available plans: Bronze, Silver, and Gold",
        "Compare features, API call limits, and pricing",
        "Start a free trial (until next 1st) to explore the platform",
        "Upgrade anytime as your needs grow"
      ],
      tips: "Trials are free until the next 1st of the month. You can cancel anytime before billing begins."
    },
    {
      number: "05",
      title: "Complete Your Profile",
      description: "Add optional profile information to personalize your experience.",
      details: [
        "Add your trading experience level (Beginner, Intermediate, Advanced)",
        "Set your preferred markets and sectors of interest",
        "Configure notification preferences",
        "Upload a profile picture (optional)"
      ],
      tips: "This information helps us provide more relevant market insights and educational content."
    }
  ];

  const planComparison = [
    // Free plan removed per policy
    {
      name: "Bronze", 
      price: "$24.99",
      period: "/month",
      features: ["1,500 API calls/month", "10 Screeners", "100 Email alerts", "Real-time data"],
      recommended: true
    },
    {
      name: "Silver",
      price: "$49.99", 
      period: "/month",
      features: ["5,000 API calls/month", "20 Screeners", "500 Alerts", "Advanced analytics"],
      recommended: false
    },
    {
      name: "Gold",
      price: "$79.99",
      period: "/month", 
      features: ["Unlimited everything", "API access", "Priority support", "White-label options"],
      recommended: false
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" asChild>
              <Link to="/docs">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Documentation
              </Link>
            </Button>
            <span className="text-gray-400">/</span>
            <Badge variant="outline">Getting Started</Badge>
          </div>
        </div>
      </div>

      {/* Header */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <Badge className="mb-4 bg-green-100 text-green-800">
                <UserPlus className="h-4 w-4 mr-2" />
                Getting Started
              </Badge>
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                Creating Your First Account
              </h1>
              <p className="text-xl text-gray-700 leading-relaxed">
                Get started with Trade Scan Pro in less than 5 minutes. This comprehensive guide
                will walk you through creating your account and choosing the right plan for your trading needs.
              </p>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600 mb-8">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-2" />
                3 min read
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                Updated Dec 2024
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start Alert */}
      <section className="pb-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <Alert className="border-blue-200 bg-blue-50">
              <AlertCircle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>Quick Start:</strong> Already have an account? <Link to="/auth/sign-in" className="underline font-medium">Sign in here</Link> to access your dashboard immediately.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </section>

      {/* Step by Step Guide */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-12">Step-by-Step Guide</h2>
            
            <div className="space-y-8">
              {steps.map((step, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                        {step.number}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-xl text-gray-900">{step.title}</CardTitle>
                        <p className="text-gray-600 mt-1">{step.description}</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <ul className="space-y-3 mb-6">
                      {step.details.map((detail, detailIndex) => (
                        <li key={detailIndex} className="flex items-start">
                          <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{detail}</span>
                        </li>
                      ))}
                    </ul>
                    <Alert>
                      <Shield className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Pro Tip:</strong> {step.tips}
                      </AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Plan Comparison */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Choose Your Plan</h2>
              <p className="text-xl text-gray-600">
                All plans include a 7-day free trial. Upgrade or downgrade anytime.
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {planComparison.map((plan, index) => (
                <Card key={index} className={`relative ${plan.recommended ? 'ring-2 ring-blue-500 scale-105' : ''}`}>
                  {plan.recommended && (
                    <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">
                      Most Popular
                    </Badge>
                  )}
                  <CardContent className="p-6 text-center">
                    <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                    <div className="mb-4">
                      <span className="text-3xl font-bold">{plan.price}</span>
                      <span className="text-gray-600">{plan.period}</span>
                    </div>
                    <ul className="space-y-2 mb-6 text-left">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-center text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button asChild className="w-full">
                      <Link to="/auth/sign-up">
                        Get Started
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">What's Next?</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-3">Understanding Your Dashboard</h3>
                  <p className="text-gray-600 mb-4">
                    Learn how to navigate your main dashboard and customize it for your trading style.
                  </p>
                  <Button asChild variant="outline">
                    <Link to="/docs/getting-started/dashboard">
                      Read Next
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-3">Setting Up Your First Screener</h3>
                  <p className="text-gray-600 mb-4">
                    Create your first stock screener to find trading opportunities that match your criteria.
                  </p>
                  <Button asChild variant="outline">
                    <Link to="/docs/getting-started/first-screener">
                      Learn How
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Support */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Need Help Getting Started?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            Our support team is here to help you set up your account and get the most out of Trade Scan Pro.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link to="/contact">
                <Mail className="h-5 w-5 mr-2" />
                Contact Support
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-700" asChild>
              <Link to="/help">
                Browse FAQ
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CreateAccount;