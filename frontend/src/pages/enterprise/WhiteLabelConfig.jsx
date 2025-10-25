import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Switch } from '../../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import { Separator } from '../../components/ui/separator';
import { 
  Palette, 
  Globe, 
  Upload, 
  Eye, 
  Save, 
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Monitor,
  Smartphone,
  Settings,
  Crown
} from 'lucide-react';
import { useAuth } from '../../context/SecureAuthContext';
import { api } from '../../api/client';
import { toast } from 'sonner';

const WhiteLabelConfig = () => {
  const { user } = useAuth();
  const [config, setConfig] = useState({
    enabled: false,
    brand_name: '',
    primary_color: '#3b82f6',
    secondary_color: '#1e40af',
    logo_url: '',
    favicon_url: '',
    custom_domain: '',
    footer_text: '',
    support_email: '',
    support_phone: '',
    terms_url: '',
    privacy_url: '',
    hide_powered_by: false,
    custom_css: '',
    custom_js: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [previewMode, setPreviewMode] = useState('desktop');

  // Check if user has Gold plan
  const hasGoldPlan = user?.plan === 'gold';

  useEffect(() => {
    if (hasGoldPlan) {
      loadWhiteLabelConfig();
    } else {
      setLoading(false);
    }
  }, [hasGoldPlan]);

  const loadWhiteLabelConfig = async () => {
    try {
      const { data } = await api.get('/white-label/configurations/');
      if (data.success) {
        setConfig({ ...config, ...data.config });
      }
    } catch (error) {
      console.error('Failed to load white-label configuration:', error);
      toast.error('Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { data } = await api.post('/white-label/configurations/create/', config);
      if (data.success) {
        setConfig({ ...config, ...data.config });
        toast.success('White-label configuration saved successfully');
      } else {
        toast.error('Failed to save configuration');
      }
    } catch (error) {
      console.error('Failed to save white-label configuration:', error);
      toast.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const handleColorChange = (field, value) => {
    // Ensure hex color format
    if (value && !value.startsWith('#')) {
      value = '#' + value;
    }
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const previewConfig = {
    brandName: config.brand_name || 'Your Brand',
    primaryColor: config.primary_color,
    secondaryColor: config.secondary_color,
    logoUrl: config.logo_url,
    customDomain: config.custom_domain
  };

  if (!hasGoldPlan) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">White-label Configuration</h1>
            <p className="text-gray-600">Customize the platform with your brand identity</p>
          </div>

          <Alert className="border-amber-200 bg-amber-50">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <AlertDescription className="text-amber-800">
              <div className="font-semibold mb-2">Gold Plan Required</div>
              <p className="mb-4">
                White-label configuration and branding customization are available exclusively for Gold plan subscribers. 
                Create a fully branded trading platform with your company's identity.
              </p>
              <a href="/account/plan" className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-700 hover:to-yellow-700 text-white rounded-md font-medium" rel="noopener noreferrer">
                <Crown className="h-4 w-4 mr-2" />
                Upgrade to Gold Plan
              </a>
            </AlertDescription>
          </Alert>

          {/* Preview of what's available */}
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">White-label Features</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="opacity-75">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Palette className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Custom Branding</h3>
                      <p className="text-sm text-gray-600">Logo, colors, fonts, and complete visual identity customization</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="opacity-75">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <Globe className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Custom Domain</h3>
                      <p className="text-sm text-gray-600">Host the platform on your own domain with SSL certificates</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="opacity-75">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Settings className="h-6 w-6 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Custom Code</h3>
                      <p className="text-sm text-gray-600">Add custom CSS/JS for advanced customizations</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="opacity-75">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
                      <Eye className="h-6 w-6 text-red-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">White-label Ready</h3>
                      <p className="text-sm text-gray-600">Remove all Trade Scan Pro branding and make it yours</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading white-label configuration...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">White-label Configuration</h1>
              <p className="text-gray-600">Customize the platform with your brand identity</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge className="bg-gradient-to-r from-amber-500 to-yellow-500 text-white">
                <Crown className="h-4 w-4 mr-1" />
                Gold Feature
              </Badge>
              <Button 
                onClick={handleSave}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {saving ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Configuration
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Status Alert */}
        {config.enabled ? (
          <Alert className="mb-8 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              <strong>White-label branding is active.</strong> Your custom configuration is live and visible to users.
              {config.custom_domain && (
                <span> Available at: <a href={`https://${config.custom_domain}`} className="underline font-medium" target="_blank" rel="noopener noreferrer">{config.custom_domain}</a></span>
              )}
            </AlertDescription>
          </Alert>
        ) : (
          <Alert className="mb-8 border-gray-200 bg-gray-50">
            <AlertTriangle className="h-4 w-4 text-gray-600" />
            <AlertDescription className="text-gray-700">
              <strong>White-label branding is disabled.</strong> Enable below to activate your custom branding configuration.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="branding" className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="branding">Branding</TabsTrigger>
                <TabsTrigger value="domain">Domain</TabsTrigger>
                <TabsTrigger value="content">Content</TabsTrigger>
                <TabsTrigger value="advanced">Advanced</TabsTrigger>
              </TabsList>

              <TabsContent value="branding" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Palette className="h-5 w-5" />
                      Brand Identity
                    </CardTitle>
                    <CardDescription>Configure your brand colors, logo, and visual identity</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Enable White-label */}
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="enabled" className="text-base font-medium">Enable White-label Branding</Label>
                        <p className="text-sm text-gray-600">Activate custom branding across the platform</p>
                      </div>
                      <Switch
                        id="enabled"
                        checked={config.enabled}
                        onCheckedChange={(checked) => handleInputChange('enabled', checked)}
                      />
                    </div>

                    <Separator />

                    {/* Brand Name */}
                    <div className="space-y-2">
                      <Label htmlFor="brand_name">Brand Name</Label>
                      <Input
                        id="brand_name"
                        value={config.brand_name}
                        onChange={(e) => handleInputChange('brand_name', e.target.value)}
                        placeholder="Your Company Name"
                      />
                    </div>

                    {/* Colors */}
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="primary_color">Primary Color</Label>
                        <div className="flex gap-2">
                          <Input
                            id="primary_color"
                            value={config.primary_color}
                            onChange={(e) => handleColorChange('primary_color', e.target.value)}
                            placeholder="#3b82f6"
                          />
                          <input
                            type="color"
                            value={config.primary_color}
                            onChange={(e) => handleColorChange('primary_color', e.target.value)}
                            className="w-12 h-10 rounded border border-gray-300"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="secondary_color">Secondary Color</Label>
                        <div className="flex gap-2">
                          <Input
                            id="secondary_color"
                            value={config.secondary_color}
                            onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                            placeholder="#1e40af"
                          />
                          <input
                            type="color"
                            value={config.secondary_color}
                            onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                            className="w-12 h-10 rounded border border-gray-300"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Logo Upload */}
                    <div className="space-y-2">
                      <Label htmlFor="logo_url">Logo URL</Label>
                      <div className="flex gap-2">
                        <Input
                          id="logo_url"
                          value={config.logo_url}
                          onChange={(e) => handleInputChange('logo_url', e.target.value)}
                          placeholder="https://yoursite.com/logo.png"
                        />
                        <Button variant="outline" size="icon">
                          <Upload className="h-4 w-4" />
                        </Button>
                      </div>
                      <p className="text-xs text-gray-600">Recommended: 200x50px PNG or SVG with transparent background</p>
                    </div>

                    {/* Favicon */}
                    <div className="space-y-2">
                      <Label htmlFor="favicon_url">Favicon URL</Label>
                      <Input
                        id="favicon_url"
                        value={config.favicon_url}
                        onChange={(e) => handleInputChange('favicon_url', e.target.value)}
                        placeholder="https://yoursite.com/favicon.ico"
                      />
                      <p className="text-xs text-gray-600">Recommended: 32x32px ICO or PNG format</p>
                    </div>

                    {/* Hide Powered By */}
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="hide_powered_by" className="text-base font-medium">Hide "Powered by Trade Scan Pro"</Label>
                        <p className="text-sm text-gray-600">Remove Trade Scan Pro branding from footer</p>
                      </div>
                      <Switch
                        id="hide_powered_by"
                        checked={config.hide_powered_by}
                        onCheckedChange={(checked) => handleInputChange('hide_powered_by', checked)}
                      />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="domain" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Globe className="h-5 w-5" />
                      Custom Domain
                    </CardTitle>
                    <CardDescription>Configure your custom domain and SSL settings</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="custom_domain">Custom Domain</Label>
                      <Input
                        id="custom_domain"
                        value={config.custom_domain}
                        onChange={(e) => handleInputChange('custom_domain', e.target.value)}
                        placeholder="trading.yourcompany.com"
                      />
                      <p className="text-xs text-gray-600">Point your domain's CNAME record to: platform.retailtradescanner.com</p>
                    </div>

                    <Alert className="border-blue-200 bg-blue-50">
                      <Globe className="h-4 w-4 text-blue-600" />
                      <AlertDescription className="text-blue-800">
                        <strong>Domain Setup Instructions:</strong>
                        <ol className="list-decimal list-inside mt-2 space-y-1 text-sm">
                          <li>Add a CNAME record in your DNS settings</li>
                          <li>Point your subdomain to: platform.retailtradescanner.com</li>
                          <li>SSL certificates will be automatically provisioned</li>
                          <li>Contact support if you need help with DNS configuration</li>
                        </ol>
                      </AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="content" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Content & Support</CardTitle>
                    <CardDescription>Customize footer content and support information</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="footer_text">Footer Text</Label>
                      <Input
                        id="footer_text"
                        value={config.footer_text}
                        onChange={(e) => handleInputChange('footer_text', e.target.value)}
                        placeholder="© 2024 Your Company. All rights reserved."
                      />
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="support_email">Support Email</Label>
                        <Input
                          id="support_email"
                          type="email"
                          value={config.support_email}
                          onChange={(e) => handleInputChange('support_email', e.target.value)}
                          placeholder="support@yourcompany.com"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="support_phone">Support Phone</Label>
                        <Input
                          id="support_phone"
                          value={config.support_phone}
                          onChange={(e) => handleInputChange('support_phone', e.target.value)}
                          placeholder="+1 (555) 123-4567"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="terms_url">Terms of Service URL</Label>
                        <Input
                          id="terms_url"
                          value={config.terms_url}
                          onChange={(e) => handleInputChange('terms_url', e.target.value)}
                          placeholder="https://yourcompany.com/terms"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="privacy_url">Privacy Policy URL</Label>
                        <Input
                          id="privacy_url"
                          value={config.privacy_url}
                          onChange={(e) => handleInputChange('privacy_url', e.target.value)}
                          placeholder="https://yourcompany.com/privacy"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="advanced" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Advanced Customization</CardTitle>
                    <CardDescription>Add custom CSS and JavaScript for advanced branding</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="custom_css">Custom CSS</Label>
                      <textarea
                        id="custom_css"
                        value={config.custom_css}
                        onChange={(e) => handleInputChange('custom_css', e.target.value)}
                        placeholder="/* Add your custom CSS here */"
                        className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                      />
                      <p className="text-xs text-gray-600">Add custom styles to override default styling</p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="custom_js">Custom JavaScript</Label>
                      <textarea
                        id="custom_js"
                        value={config.custom_js}
                        onChange={(e) => handleInputChange('custom_js', e.target.value)}
                        placeholder="// Add your custom JavaScript here"
                        className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                      />
                      <p className="text-xs text-gray-600">Add analytics tracking, custom functionality, etc.</p>
                    </div>

                    <Alert className="border-amber-200 bg-amber-50">
                      <AlertTriangle className="h-4 w-4 text-amber-600" />
                      <AlertDescription className="text-amber-800">
                        <strong>Advanced Features:</strong> Custom CSS/JS modifications can affect platform functionality. 
                        Test thoroughly before applying to production.
                      </AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Preview Panel */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5" />
                    Live Preview
                  </CardTitle>
                  <div className="flex border rounded-lg">
                    <Button
                      size="sm"
                      variant={previewMode === 'desktop' ? 'default' : 'ghost'}
                      onClick={() => setPreviewMode('desktop')}
                      className="px-3"
                    >
                      <Monitor className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant={previewMode === 'mobile' ? 'default' : 'ghost'}
                      onClick={() => setPreviewMode('mobile')}
                      className="px-3"
                    >
                      <Smartphone className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div 
                  className={`border rounded-lg overflow-hidden ${
                    previewMode === 'mobile' ? 'max-w-sm mx-auto' : ''
                  }`}
                  style={{ backgroundColor: '#f8fafc' }}
                >
                  {/* Preview Header */}
                  <div 
                    className="p-4 border-b"
                    style={{ backgroundColor: previewConfig.primaryColor }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {previewConfig.logoUrl ? (
                          <img 
                            src={previewConfig.logoUrl} 
                            alt="Logo" 
                            className="h-8"
                            onError={(e) => { e.target.style.display = 'none'; }}
                          />
                        ) : (
                          <div className="text-white font-bold text-lg">
                            {previewConfig.brandName}
                          </div>
                        )}
                      </div>
                      <div className="text-white text-sm">
                        {previewConfig.customDomain || 'platform.example.com'}
                      </div>
                    </div>
                  </div>

                  {/* Preview Content */}
                  <div className="p-4 space-y-4">
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    </div>
                    
                    <div 
                      className="p-3 rounded"
                      style={{ backgroundColor: previewConfig.primaryColor + '20' }}
                    >
                      <div className="h-3 bg-gray-300 rounded w-full mb-2"></div>
                      <div className="h-3 bg-gray-300 rounded w-2/3"></div>
                    </div>

                    <div className="flex gap-2">
                      <div 
                        className="px-3 py-1 rounded text-sm text-white flex-1 text-center"
                        style={{ backgroundColor: previewConfig.primaryColor }}
                      >
                        Primary
                      </div>
                      <div 
                        className="px-3 py-1 rounded text-sm text-white flex-1 text-center"
                        style={{ backgroundColor: previewConfig.secondaryColor }}
                      >
                        Secondary
                      </div>
                    </div>
                  </div>

                  {/* Preview Footer */}
                  <div className="p-3 border-t bg-gray-50 text-xs text-gray-600 text-center">
                    {config.footer_text || `© 2024 ${previewConfig.brandName}. All rights reserved.`}
                    {!config.hide_powered_by && (
                      <div className="mt-1 text-gray-400">
                        Powered by Trade Scan Pro
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-4 text-xs text-gray-600">
                  <strong>Note:</strong> This is a simplified preview. Changes will be reflected across the entire platform once saved and activated.
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhiteLabelConfig;