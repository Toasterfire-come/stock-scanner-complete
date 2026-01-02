import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Label } from "../../components/ui/label";
import { Switch } from "../../components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Badge } from "../../components/ui/badge";
import { Separator } from "../../components/ui/separator";
import { 
  Settings as SettingsIcon,
  Palette,
  Bell,
  Globe,
  Shield,
  Monitor,
  Sun,
  Moon,
  Smartphone,
  Save,
  CheckCircle,
  Info
} from "lucide-react";
import { useTheme } from "next-themes";
import { toast } from "sonner";

const Settings = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [settings, setSettings] = useState({
    notifications: {
      sms: true,
      phoneNumber: '',
      push: false,
      priceAlerts: true,
      newsAlerts: false,
      marketOpen: true
    },
    display: {
      currency: 'USD',
      dateFormat: 'MM/DD/YYYY',
      timeFormat: '12h',
      numberFormat: 'US',
      chartTheme: 'professional'
    },
    privacy: {
      analyticsTracking: true,
      performanceTracking: false,
      crashReporting: true
    },
    advanced: {
      autoRefresh: true,
      refreshInterval: 30,
      dataCompression: true,
      debugMode: false
    }
  });

  const [isDirty, setIsDirty] = useState(false);

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
    setIsDirty(true);
  };

  const handleSave = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("Settings saved successfully!");
      setIsDirty(false);
    } catch (error) {
      toast.error("Failed to save settings. Please try again.");
    }
  };

  const ThemeSelector = () => (
    <div className="space-y-4">
      <div>
        <Label className="text-base font-medium">Theme Preference</Label>
        <p className="text-sm text-muted-foreground mb-3">
          Choose how Trade Scan Pro looks to you. Select a single theme, or sync with your system and automatically switch between day and night themes.
        </p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {[
          { value: 'light', label: 'Light', icon: Sun, description: 'Clean and bright' },
          { value: 'dark', label: 'Dark', icon: Moon, description: 'Easy on the eyes' },
          { value: 'system', label: 'System', icon: Monitor, description: 'Sync with OS' }
        ].map((option) => (
          <Card
            key={option.value}
            className={`cursor-pointer transition-all hover:shadow-md ${
              theme === option.value ? 'ring-2 ring-blue-500 bg-blue-50/50' : ''
            }`}
            onClick={() => setTheme(option.value)}
          >
            <CardContent className="p-4 text-center">
              <option.icon className={`h-8 w-8 mx-auto mb-2 ${
                theme === option.value ? 'text-blue-600' : 'text-muted-foreground'
              }`} />
              <div className="font-medium">{option.label}</div>
              <div className="text-xs text-muted-foreground">{option.description}</div>
              {theme === option.value && (
                <Badge variant="secondary" className="mt-2">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Active
                </Badge>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
      
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          Current theme: <strong>{resolvedTheme || theme}</strong>
          {theme === 'system' && ` (following system preference: ${resolvedTheme})`}
        </AlertDescription>
      </Alert>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/30 to-indigo-100/30 p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold">Settings</h1>
          </div>
          <p className="text-muted-foreground">
            Customize your Trade Scan Pro experience and preferences.
          </p>
        </div>

        <Tabs defaultValue="appearance" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="display">Display</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>

          <TabsContent value="appearance" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Palette className="h-5 w-5 text-blue-600" />
                  <CardTitle>Theme & Appearance</CardTitle>
                </div>
                <CardDescription>
                  Customize the visual appearance of your dashboard and interface.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <ThemeSelector />
                
                <Separator />
                
                <div className="space-y-4">
                  <Label className="text-base font-medium">Chart Theme</Label>
                  <Select 
                    value={settings.display.chartTheme} 
                    onValueChange={(value) => handleSettingChange('display', 'chartTheme', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="colorful">Colorful</SelectItem>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="high-contrast">High Contrast</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Bell className="h-5 w-5 text-blue-600" />
                  <CardTitle>Notification Preferences</CardTitle>
                </div>
                <CardDescription>
                  Choose what notifications you want to receive and how.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>SMS Alerts (TextBelt)</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive alerts via SMS text message
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications.sms}
                      onCheckedChange={(checked) => handleSettingChange('notifications', 'sms', checked)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Phone Number</Label>
                    <Input
                      type="tel"
                      placeholder="+1234567890"
                      value={settings.notifications.phoneNumber}
                      onChange={(e) => handleSettingChange('notifications', 'phoneNumber', e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">
                      Enter your phone number with country code for SMS alerts
                    </p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Push Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Get instant notifications in your browser
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications.push}
                      onCheckedChange={(checked) => handleSettingChange('notifications', 'push', checked)}
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Price Alerts</Label>
                      <p className="text-sm text-muted-foreground">
                        Notify when stocks hit your target prices
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications.priceAlerts}
                      onCheckedChange={(checked) => handleSettingChange('notifications', 'priceAlerts', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>News Alerts</Label>
                      <p className="text-sm text-muted-foreground">
                        Breaking news about your watched stocks
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications.newsAlerts}
                      onCheckedChange={(checked) => handleSettingChange('notifications', 'newsAlerts', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Market Open/Close</Label>
                      <p className="text-sm text-muted-foreground">
                        Daily market open and close notifications
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications.marketOpen}
                      onCheckedChange={(checked) => handleSettingChange('notifications', 'marketOpen', checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="display" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-blue-600" />
                  <CardTitle>Display & Localization</CardTitle>
                </div>
                <CardDescription>
                  Customize how data is displayed according to your preferences.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Currency</Label>
                    <Select 
                      value={settings.display.currency} 
                      onValueChange={(value) => handleSettingChange('display', 'currency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">USD ($)</SelectItem>
                        <SelectItem value="EUR">EUR (€)</SelectItem>
                        <SelectItem value="GBP">GBP (£)</SelectItem>
                        <SelectItem value="CAD">CAD ($)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Date Format</Label>
                    <Select 
                      value={settings.display.dateFormat} 
                      onValueChange={(value) => handleSettingChange('display', 'dateFormat', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                        <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                        <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Time Format</Label>
                    <Select 
                      value={settings.display.timeFormat} 
                      onValueChange={(value) => handleSettingChange('display', 'timeFormat', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="12h">12 Hour</SelectItem>
                        <SelectItem value="24h">24 Hour</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Number Format</Label>
                    <Select 
                      value={settings.display.numberFormat} 
                      onValueChange={(value) => handleSettingChange('display', 'numberFormat', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="US">US (1,234.56)</SelectItem>
                        <SelectItem value="EU">EU (1.234,56)</SelectItem>
                        <SelectItem value="IN">IN (1,23,456.78)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  <CardTitle>Advanced Settings</CardTitle>
                </div>
                <CardDescription>
                  Advanced configuration options for power users.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto Refresh Data</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically refresh market data
                      </p>
                    </div>
                    <Switch
                      checked={settings.advanced.autoRefresh}
                      onCheckedChange={(checked) => handleSettingChange('advanced', 'autoRefresh', checked)}
                    />
                  </div>

                  {settings.advanced.autoRefresh && (
                    <div className="space-y-2 ml-4">
                      <Label>Refresh Interval (seconds)</Label>
                      <Select 
                        value={settings.advanced.refreshInterval.toString()} 
                        onValueChange={(value) => handleSettingChange('advanced', 'refreshInterval', parseInt(value))}
                      >
                        <SelectTrigger className="w-48">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="15">15 seconds</SelectItem>
                          <SelectItem value="30">30 seconds</SelectItem>
                          <SelectItem value="60">1 minute</SelectItem>
                          <SelectItem value="300">5 minutes</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Data Compression</Label>
                      <p className="text-sm text-muted-foreground">
                        Reduce bandwidth usage (recommended)
                      </p>
                    </div>
                    <Switch
                      checked={settings.advanced.dataCompression}
                      onCheckedChange={(checked) => handleSettingChange('advanced', 'dataCompression', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Analytics Tracking</Label>
                      <p className="text-sm text-muted-foreground">
                        Help improve our platform with usage analytics
                      </p>
                    </div>
                    <Switch
                      checked={settings.privacy.analyticsTracking}
                      onCheckedChange={(checked) => handleSettingChange('privacy', 'analyticsTracking', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Debug Mode</Label>
                      <p className="text-sm text-muted-foreground">
                        Show additional debugging information
                      </p>
                    </div>
                    <Switch
                      checked={settings.advanced.debugMode}
                      onCheckedChange={(checked) => handleSettingChange('advanced', 'debugMode', checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {isDirty && (
          <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
            <Card className="shadow-lg border">
              <CardContent className="flex items-center gap-3 p-4">
                <p className="text-sm">You have unsaved changes</p>
                <Button onClick={handleSave} size="sm">
                  <Save className="h-4 w-4 mr-1" />
                  Save Changes
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Settings;