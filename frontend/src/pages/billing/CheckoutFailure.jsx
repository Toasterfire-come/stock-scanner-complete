import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { AlertTriangle, RefreshCw, ArrowLeft, Mail } from "lucide-react";

const CheckoutFailure = () => {
  const location = useLocation();
  const { error, planId } = location.state || {};

  const commonIssues = [
    {
      title: "Insufficient Funds",
      description: "Your payment method doesn't have enough funds available.",
      solution: "Try a different payment method or add funds to your account."
    },
    {
      title: "Card Declined",
      description: "Your bank declined the transaction.",
      solution: "Contact your bank or try a different card."
    },
    {
      title: "Expired Card",
      description: "The payment method has expired.",
      solution: "Update your payment information with a valid card."
    },
    {
      title: "Network Error",
      description: "There was a connection issue during payment.",
      solution: "Check your internet connection and try again."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50/50 to-orange-50/50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Error Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="h-12 w-12 text-red-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Payment Failed
          </h1>
          <p className="text-gray-600">
            We couldn't process your payment. Don't worry, no charges were made.
          </p>
        </div>

        {/* Error Details */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Quick Actions */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Try Again</CardTitle>
            <CardDescription>
              Most payment issues can be resolved quickly
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <Button asChild className="w-full">
                <Link to="/pricing" state={{ selectedPlan: planId }}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry Payment
                </Link>
              </Button>
              
              <Button asChild variant="outline" className="w-full">
                <Link to="/account/billing">
                  Update Payment Method
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Common Issues */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Common Issues & Solutions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {commonIssues.map((issue, index) => (
                <div key={index} className="border-l-4 border-blue-500 pl-4">
                  <h4 className="font-semibold text-gray-900">{issue.title}</h4>
                  <p className="text-sm text-gray-600 mb-1">{issue.description}</p>
                  <p className="text-sm text-blue-600">{issue.solution}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Alternative Options */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Alternative Options</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Continue with Free Plan</h4>
              <p className="text-sm text-blue-700 mb-3">
                Start using Trade Scan Pro with our free features while you resolve payment issues.
              </p>
              <Button asChild variant="outline" size="sm">
                <Link to="/app/dashboard">
                  Continue with Free Plan
                </Link>
              </Button>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Need Help?</h4>
              <p className="text-sm text-gray-600 mb-3">
                Our support team can help you resolve payment issues and get you set up.
              </p>
              <div className="flex space-x-2">
                <Button asChild variant="outline" size="sm">
                  <Link to="/contact">
                    <Mail className="h-4 w-4 mr-2" />
                    Contact Support
                  </Link>
                </Button>
                <Button asChild variant="ghost" size="sm">
                  <Link to="/help/faq">
                    View FAQ
                  </Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="text-center">
          <Button asChild variant="ghost">
            <Link to="/pricing">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Pricing
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CheckoutFailure;