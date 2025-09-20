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
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Notification Settings</h1>
      {/* content */}
    </div>
  );
};

export default NotificationSettings;