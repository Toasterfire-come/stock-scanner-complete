import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Checkbox } from "../../components/ui/checkbox";
import { Badge } from "../../components/ui/badge";
import { Mail, Bell, Smartphone, CheckCircle } from "lucide-react";
import { toast } from "sonner";

const NewsSubscribe = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    categories: [],
    frequency: "daily",
    notifications: {
      email: true,
      push: false,
      sms: false
    }
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const categories = [
    { id: "breaking", label: "Breaking News", description: "Urgent market updates and major announcements" },
    { id: "earnings", label: "Earnings Reports", description: "Quarterly earnings and financial results" },
    { id: "markets", label: "Market Analysis", description: "Daily market trends and expert analysis" },
    { id: "stocks", label: "Stock Alerts", description: "Price movements and stock-specific news" },
    { id: "ipos", label: "IPOs & New Listings", description: "New public offerings and market debuts" },
    { id: "mergers", label: "M&A Activity", description: "Mergers, acquisitions, and corporate deals" }
  ];

  const subscriptionPlans = [
    {
      id: "free",
      name: "Free Newsletter",
      price: "Free",
      features: [
        "Daily market summary",
        "Weekly roundup email",
        "Basic stock alerts",
        "Access to public articles"
      ]
    },
    {
      id: "premium",
      name: "Premium Alerts",
      price: "$9.99/month",
      features: [
        "Real-time breaking news",
        "Personalized stock alerts",
        "Exclusive market analysis",
        "SMS and push notifications",
        "Priority customer support"
      ],
      recommended: true
    },
    {
      id: "pro",
      name: "Professional",
      price: "$19.99/month",
      features: [
        "All Premium features",
        "Advanced market insights",
        "Institutional-grade reports",
        "Custom alert criteria",
        "API access for alerts"
      ]
    }
  ];

  const toggleCategory = (categoryId) => {
    setFormData(prev => ({
      ...prev,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter(c => c !== categoryId)
        : [...prev.categories, categoryId]
    }));
  };

  const toggleNotification = (type) => {
    setFormData(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [type]: !prev.notifications[type]
      }
    }));
  };

  const handleSubmit = async (planId) => {
    if (!formData.email.trim()) {
      toast.error("Please enter your email address");
      return;
    }

    if (formData.categories.length === 0) {
      toast.error("Please select at least one category");
      return;
    }

    setIsSubmitting(true);
    try {
      // Simulate API call to subscribe
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast.success("Successfully subscribed to news alerts!");
      navigate("/app/news");
    } catch (error) {
      toast.error("Failed to subscribe. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Stay Informed with Market News
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get personalized news alerts and market insights delivered directly to your inbox
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-12">
          {subscriptionPlans.map((plan) => (
            <Card 
              key={plan.id} 
              className={`relative ${plan.recommended ? 'border-blue-500 shadow-lg' : ''}`}
            >
              {plan.recommended && (
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-600">
                  Recommended
                </Badge>
              )}
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <div className="text-3xl font-bold text-blue-600">{plan.price}</div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button 
                  className="w-full" 
                  variant={plan.recommended ? "default" : "outline"}
                  onClick={() => handleSubmit(plan.id)}
                  disabled={isSubmitting}
                >
                  {plan.id === "free" ? "Subscribe Free" : "Subscribe Now"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
              <CardDescription>Enter your phone number to receive news alerts via SMS</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+1234567890"
                  value={formData.phone || ''}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
                <p className="text-xs text-gray-500 mt-1">Enter with country code (e.g., +1 for US)</p>
              </div>

              <div>
                <Label className="text-base font-medium">Notification Method</Label>
                <div className="space-y-3 mt-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="sms-notifications"
                      checked={formData.notifications.sms || true}
                      onCheckedChange={() => toggleNotification("sms")}
                    />
                    <Label htmlFor="sms-notifications" className="flex items-center gap-2">
                      <Bell className="h-4 w-4" />
                      SMS Notifications (TextBelt)
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 opacity-50">
                    <Checkbox
                      id="push-notifications"
                      checked={false}
                      disabled
                    />
                    <Label htmlFor="push-notifications" className="flex items-center gap-2">
                      <Bell className="h-4 w-4" />
                      Push Notifications
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="sms-notifications"
                      checked={formData.notifications.sms}
                      onCheckedChange={() => toggleNotification("sms")}
                    />
                    <Label htmlFor="sms-notifications" className="flex items-center gap-2">
                      <Smartphone className="h-4 w-4" />
                      SMS Alerts (Premium only)
                    </Label>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Content Preferences</CardTitle>
              <CardDescription>Choose the types of news you want to receive</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {categories.map((category) => (
                  <div key={category.id} className="border rounded-lg p-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <Checkbox
                        id={category.id}
                        checked={formData.categories.includes(category.id)}
                        onCheckedChange={() => toggleCategory(category.id)}
                      />
                      <Label htmlFor={category.id} className="font-medium">
                        {category.label}
                      </Label>
                    </div>
                    <p className="text-sm text-gray-600 ml-6">
                      {category.description}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle>What You'll Get</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Bell className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="font-semibold mb-2">Real-time Alerts</h3>
                <p className="text-sm text-gray-600">
                  Get notified instantly when important market events occur
                </p>
              </div>
              <div className="text-center">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Mail className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="font-semibold mb-2">Curated Content</h3>
                <p className="text-sm text-gray-600">
                  Receive only the most relevant news for your portfolio
                </p>
              </div>
              <div className="text-center">
                <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="font-semibold mb-2">Expert Analysis</h3>
                <p className="text-sm text-gray-600">
                  Access professional insights and market commentary
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center mt-8">
          <p className="text-sm text-gray-500">
            You can unsubscribe at any time. We respect your privacy and will never share your email.
          </p>
        </div>
      </div>
    </div>
  );
};

export default NewsSubscribe;