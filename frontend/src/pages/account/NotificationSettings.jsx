import React, { useState, useEffect } from "react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Switch } from "../../components/ui/switch";
import { Label } from "../../components/ui/label";
import { Skeleton } from "../../components/ui/skeleton";
import { toast } from "sonner";
import { 
  Bell, 
  TrendingUp, 
  PieChart, 
  Newspaper, 
  Shield, 
  Save,
  Smartphone,
  Mail,
  Volume2
} from "lucide-react";
import { getNotificationSettings, updateNotificationSettings } from "../../api/client";

const NotificationSettings = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState({
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
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await getNotificationSettings();
        if (response.success) {
          setSettings(response.data);
        } else {
          toast.error("Failed to load notification settings");
        }
      } catch (error) {
        console.error("Failed to load settings:", error);
        // Continue with default settings
      } finally {
        setIsLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await updateNotificationSettings(settings);
      if (response.success) {
        toast.success("Notification settings updated successfully");
      } else {
        toast.error("Failed to update notification settings");
      }
    } catch (error) {
      toast.error("Failed to update notification settings");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <div className="grid gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-64" />
                </CardHeader>
                <CardContent className="space-y-4">
                  {[1, 2, 3].map((j) => (
                    <div key={j} className="flex items-center justify-between">
                      <div>
                        <Skeleton className="h-4 w-32 mb-2" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                      <Skeleton className="h-6 w-12" />
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notification Settings</h1>
          <p className="text-gray-600 mt-2">
            Customize how and when you receive notifications from Trade Scan Pro
          </p>
        </div>

        {/* Notification Methods */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Volume2 className="h-5 w-5 mr-2" />
              Delivery Methods
            </CardTitle>
            <CardDescription>
              Choose how you want to receive notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-3 p-4 border rounded-lg">
                <Mail className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="font-medium">Email</div>
                  <div className="text-sm text-gray-600">Always enabled</div>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border rounded-lg opacity-50">
                <Smartphone className="h-5 w-5 text-gray-400" />
                <div>
                  <div className="font-medium">Push Notifications</div>
                  <div className="text-sm text-gray-600">Coming soon</div>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border rounded-lg opacity-50">
                <Volume2 className="h-5 w-5 text-gray-400" />
                <div>
                  <div className="font-medium">SMS</div>
                  <div className="text-sm text-gray-600">Premium feature</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Trading Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Trading Alerts
            </CardTitle>
            <CardDescription>
              Price movements, volume changes, and market events
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="price-alerts">Price Alerts</Label>
                <p className="text-sm text-gray-600">
                  Get notified when stocks hit your target prices or move significantly
                </p>
              </div>
              <Switch
                id="price-alerts"
                checked={settings.trading.price_alerts}
                onCheckedChange={(value) => handleSettingChange("trading", "price_alerts", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="volume-alerts">Volume Alerts</Label>
                <p className="text-sm text-gray-600">
                  Unusual volume activity and trading spikes
                </p>
              </div>
              <Switch
                id="volume-alerts"
                checked={settings.trading.volume_alerts}
                onCheckedChange={(value) => handleSettingChange("trading", "volume_alerts", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="market-hours">Market Hours</Label>
                <p className="text-sm text-gray-600">
                  Market open, close, and pre/after-market session notifications
                </p>
              </div>
              <Switch
                id="market-hours"
                checked={settings.trading.market_hours}
                onCheckedChange={(value) => handleSettingChange("trading", "market_hours", value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Portfolio Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Portfolio Updates
            </CardTitle>
            <CardDescription>
              Performance reports and portfolio milestones
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="daily-summary">Daily Summary</Label>
                <p className="text-sm text-gray-600">
                  Daily portfolio performance and market summary email
                </p>
              </div>
              <Switch
                id="daily-summary"
                checked={settings.portfolio.daily_summary}
                onCheckedChange={(value) => handleSettingChange("portfolio", "daily_summary", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="weekly-report">Weekly Report</Label>
                <p className="text-sm text-gray-600">
                  Comprehensive weekly performance analysis and insights
                </p>
              </div>
              <Switch
                id="weekly-report"
                checked={settings.portfolio.weekly_report}
                onCheckedChange={(value) => handleSettingChange("portfolio", "weekly_report", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="milestone-alerts">Milestone Alerts</Label>
                <p className="text-sm text-gray-600">
                  Notifications when you reach profit/loss milestones
                </p>
              </div>
              <Switch
                id="milestone-alerts"
                checked={settings.portfolio.milestone_alerts}
                onCheckedChange={(value) => handleSettingChange("portfolio", "milestone_alerts", value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* News Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Newspaper className="h-5 w-5 mr-2" />
              News & Market Updates
            </CardTitle>
            <CardDescription>
              Breaking news, earnings, and analyst coverage
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="breaking-news">Breaking News</Label>
                <p className="text-sm text-gray-600">
                  Major market moving news and economic events
                </p>
              </div>
              <Switch
                id="breaking-news"
                checked={settings.news.breaking_news}
                onCheckedChange={(value) => handleSettingChange("news", "breaking_news", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="earnings-alerts">Earnings Alerts</Label>
                <p className="text-sm text-gray-600">
                  Earnings announcements for stocks in your watchlist
                </p>
              </div>
              <Switch
                id="earnings-alerts"
                checked={settings.news.earnings_alerts}
                onCheckedChange={(value) => handleSettingChange("news", "earnings_alerts", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="analyst-ratings">Analyst Ratings</Label>
                <p className="text-sm text-gray-600">
                  Analyst upgrades, downgrades, and price target changes
                </p>
              </div>
              <Switch
                id="analyst-ratings"
                checked={settings.news.analyst_ratings}
                onCheckedChange={(value) => handleSettingChange("news", "analyst_ratings", value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Security Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Security & Account
            </CardTitle>
            <CardDescription>
              Account security and billing notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="login-alerts">Login Alerts</Label>
                <p className="text-sm text-gray-600">
                  Notifications when your account is accessed from new devices
                </p>
              </div>
              <Switch
                id="login-alerts"
                checked={settings.security.login_alerts}
                onCheckedChange={(value) => handleSettingChange("security", "login_alerts", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="billing-updates">Billing Updates</Label>
                <p className="text-sm text-gray-600">
                  Payment confirmations, failed charges, and billing changes
                </p>
              </div>
              <Switch
                id="billing-updates"
                checked={settings.security.billing_updates}
                onCheckedChange={(value) => handleSettingChange("security", "billing_updates", value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="plan-updates">Plan Updates</Label>
                <p className="text-sm text-gray-600">
                  Subscription changes, feature updates, and service announcements
                </p>
              </div>
              <Switch
                id="plan-updates"
                checked={settings.security.plan_updates}
                onCheckedChange={(value) => handleSettingChange("security", "plan_updates", value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? (
              "Saving..."
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Settings
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings;