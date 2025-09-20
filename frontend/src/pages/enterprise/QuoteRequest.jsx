import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Checkbox } from '../../components/ui/checkbox';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import { 
  Calculator, 
  CheckCircle, 
  DollarSign, 
  Users, 
  Database, 
  Zap,
  ArrowRight,
  Building2,
  Clock,
  Shield
} from 'lucide-react';
import { submitQuoteRequest } from '../../api/client';
import { toast } from 'sonner';

const QuoteRequest = () => {
  const [formData, setFormData] = useState({
    company_name: '',
    contact_name: '',
    contact_email: '',
    phone: '',
    requirements: '',
    estimated_users: '',
    deployment_type: '',
    timeline: '',
    budget_range: '',
    features: [],
    additional_notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const featureOptions = [
    { id: 'real_time_data', label: 'Real-time Market Data', price: 'from $500/month' },
    { id: 'portfolio_management', label: 'Portfolio Management', price: 'from $300/month' },
    { id: 'risk_analytics', label: 'Risk Analytics', price: 'from $800/month' },
    { id: 'white_label', label: 'White-label Branding', price: 'from $1,000/month' },
    { id: 'api_access', label: 'Unlimited API Access', price: 'from $1,200/month' },
    { id: 'custom_integrations', label: 'Custom Integrations', price: 'Quote required' },
    { id: 'dedicated_support', label: 'Dedicated Support', price: 'from $2,000/month' },
    { id: 'compliance_tools', label: 'Compliance & Reporting', price: 'from $1,500/month' },
    { id: 'multi_entity', label: 'Multi-entity Support', price: 'from $600/month' },
    { id: 'sso_integration', label: 'SSO Integration', price: 'from $400/month' }
  ];

  const pricingTiers = [
    {
      name: 'Professional',
      description: 'For growing teams and small institutions',
      userRange: '10-50 users',
      priceRange: '$2,000 - $8,000/month',
      features: ['Standard API access', 'Basic support', 'Core features', 'Email support']
    },
    {
      name: 'Enterprise',
      description: 'For large organizations and institutions',
      userRange: '50-500 users',
      priceRange: '$8,000 - $25,000/month',
      features: ['Priority API access', 'Phone support', 'Advanced features', 'Custom integrations']
    },
    {
      name: 'Enterprise Plus',
      description: 'For the largest institutions with custom needs',
      userRange: '500+ users',
      priceRange: 'Custom pricing',
      features: ['Unlimited access', 'Dedicated support', 'All features', 'On-premise options']
    }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFeatureToggle = (featureId) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.includes(featureId)
        ? prev.features.filter(f => f !== featureId)
        : [...prev.features, featureId]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    const requiredFields = ['company_name', 'contact_name', 'contact_email', 'phone', 'requirements'];
    const missingFields = requiredFields.filter(field => !formData[field].trim());
    
    if (missingFields.length > 0) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.contact_email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setLoading(true);

    try {
      const response = await submitQuoteRequest(formData);
      if (response.success) {
        setSubmitted(true);
        toast.success('Quote request submitted successfully!');
      } else {
        toast.error(response.message || 'Failed to submit quote request');
      }
    } catch (error) {
      console.error('Failed to submit quote request:', error);
      toast.error('Failed to submit quote request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-8">
            <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Quote Request Submitted!</h1>
            <p className="text-gray-600">
              Thank you for your interest in our enterprise solutions. Our pricing team will prepare a detailed quote based on your requirements.
            </p>
          </div>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">What's Next?</h2>
              <div className="space-y-4 text-left">
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 font-semibold text-sm">1</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Requirements Analysis</p>
                    <p className="text-sm text-gray-600">Our team will analyze your requirements and usage patterns to create an optimal solution.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 font-semibold text-sm">2</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Custom Quote Preparation</p>
                    <p className="text-sm text-gray-600">We'll prepare a detailed quote with pricing, features, and implementation timeline.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 font-semibold text-sm">3</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Proposal Delivery</p>
                    <p className="text-sm text-gray-600">Receive your comprehensive proposal within 2-3 business days via email.</p>
                  </div>
                </div>
              </div>

              <Alert className="mt-6 border-blue-200 bg-blue-50">
                <Clock className="h-4 w-4 text-blue-600" />
                <AlertDescription className="text-blue-800">
                  <strong>Expected delivery:</strong> 2-3 business days. For urgent requests, please call our enterprise team directly.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          <div className="mt-8">
            <Button asChild className="bg-blue-600 hover:bg-blue-700">
              <a href="/enterprise">Back to Enterprise Solutions</a>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Calculator className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Request a Quote</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get a customized quote for your enterprise solution. Our pricing is transparent, 
            scalable, and designed to provide maximum value for your organization.
          </p>
        </div>

        {/* Pricing Tiers Overview */}
        <div className="grid lg:grid-cols-3 gap-6 mb-12">
          {pricingTiers.map((tier, index) => (
            <Card key={index} className={index === 1 ? 'border-blue-500 shadow-lg' : ''}>
              <CardHeader className="text-center">
                <CardTitle className="flex items-center justify-center gap-2">
                  {tier.name}
                  {index === 1 && <Badge className="bg-blue-600">Popular</Badge>}
                </CardTitle>
                <CardDescription>{tier.description}</CardDescription>
                <div className="text-2xl font-bold text-gray-900 mt-2">{tier.priceRange}</div>
                <div className="text-sm text-gray-600">{tier.userRange}</div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {tier.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Quote Request Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Quote Request Form
                </CardTitle>
                <CardDescription>
                  Provide your requirements to receive a detailed, customized quote for your enterprise solution.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Company Information */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">Company Information</h3>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Company Name *
                        </label>
                        <Input
                          value={formData.company_name}
                          onChange={(e) => handleInputChange('company_name', e.target.value)}
                          placeholder="Your company name"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Contact Name *
                        </label>
                        <Input
                          value={formData.contact_name}
                          onChange={(e) => handleInputChange('contact_name', e.target.value)}
                          placeholder="Your full name"
                          required
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address *
                        </label>
                        <Input
                          type="email"
                          value={formData.contact_email}
                          onChange={(e) => handleInputChange('contact_email', e.target.value)}
                          placeholder="your.email@company.com"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Phone Number *
                        </label>
                        <Input
                          type="tel"
                          value={formData.phone}
                          onChange={(e) => handleInputChange('phone', e.target.value)}
                          placeholder="+1 (555) 123-4567"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Project Details */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">Project Details</h3>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Estimated Users
                        </label>
                        <Select onValueChange={(value) => handleInputChange('estimated_users', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select user count" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1-10">1-10 users</SelectItem>
                            <SelectItem value="11-50">11-50 users</SelectItem>
                            <SelectItem value="51-100">51-100 users</SelectItem>
                            <SelectItem value="101-500">101-500 users</SelectItem>
                            <SelectItem value="501-1000">501-1000 users</SelectItem>
                            <SelectItem value="1000+">1000+ users</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Deployment Type
                        </label>
                        <Select onValueChange={(value) => handleInputChange('deployment_type', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select deployment" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="cloud">Cloud Hosted</SelectItem>
                            <SelectItem value="on_premise">On-Premise</SelectItem>
                            <SelectItem value="hybrid">Hybrid</SelectItem>
                            <SelectItem value="not_sure">Not Sure</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Timeline
                        </label>
                        <Select onValueChange={(value) => handleInputChange('timeline', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select timeline" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="immediate">Immediate (< 1 month)</SelectItem>
                            <SelectItem value="1-3_months">1-3 months</SelectItem>
                            <SelectItem value="3-6_months">3-6 months</SelectItem>
                            <SelectItem value="6-12_months">6-12 months</SelectItem>
                            <SelectItem value="planning">Planning phase</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Budget Range (Annual)
                        </label>
                        <Select onValueChange={(value) => handleInputChange('budget_range', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select budget range" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="under_50k">Under $50,000</SelectItem>
                            <SelectItem value="50k-100k">$50,000 - $100,000</SelectItem>
                            <SelectItem value="100k-250k">$100,000 - $250,000</SelectItem>
                            <SelectItem value="250k-500k">$250,000 - $500,000</SelectItem>
                            <SelectItem value="500k+">$500,000+</SelectItem>
                            <SelectItem value="not_sure">Not Sure</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Requirements *
                      </label>
                      <Textarea
                        value={formData.requirements}
                        onChange={(e) => handleInputChange('requirements', e.target.value)}
                        placeholder="Describe your specific requirements, use cases, and any technical specifications..."
                        rows={4}
                        required
                      />
                    </div>
                  </div>

                  {/* Feature Selection */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">Feature Requirements</h3>
                    <p className="text-sm text-gray-600">Select the features you need (optional but helps with accurate pricing)</p>
                    
                    <div className="grid md:grid-cols-2 gap-3">
                      {featureOptions.map((feature) => (
                        <div key={feature.id} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                          <Checkbox
                            id={feature.id}
                            checked={formData.features.includes(feature.id)}
                            onCheckedChange={() => handleFeatureToggle(feature.id)}
                          />
                          <div className="flex-1">
                            <label
                              htmlFor={feature.id}
                              className="text-sm font-medium text-gray-900 cursor-pointer"
                            >
                              {feature.label}
                            </label>
                            <p className="text-xs text-gray-600">{feature.price}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Additional Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Notes
                    </label>
                    <Textarea
                      value={formData.additional_notes}
                      onChange={(e) => handleInputChange('additional_notes', e.target.value)}
                      placeholder="Any additional information, special requirements, or questions..."
                      rows={3}
                    />
                  </div>

                  <Button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Submitting Request...
                      </>
                    ) : (
                      <>
                        Request Detailed Quote
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Quote Information */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Pricing Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Users className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-900">User-based Pricing</p>
                    <p className="text-sm text-gray-600">Starting at $40/user/month with volume discounts for larger teams</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Database className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-900">Data & API Access</p>
                    <p className="text-sm text-gray-600">Real-time market data and unlimited API access included in enterprise plans</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-900">Enterprise Security</p>
                    <p className="text-sm text-gray-600">Advanced security features and compliance certifications available</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Zap className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-900">Custom Development</p>
                    <p className="text-sm text-gray-600">Tailored features and integrations quoted separately based on requirements</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Alert className="border-blue-200 bg-blue-50">
              <Clock className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>Quote Delivery:</strong> Most quotes are delivered within 2-3 business days. 
                Complex requirements may take up to 5 business days for thorough analysis.
              </AlertDescription>
            </Alert>

            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Need Help?</h3>
                <p className="text-gray-600 mb-4">
                  Our enterprise team is available to discuss your requirements and help you get the most accurate quote.
                </p>
                <div className="space-y-2 text-sm">
                  <p><strong>Enterprise Sales:</strong> +1 (555) 123-4567</p>
                  <p><strong>Email:</strong> enterprise@retailtradescanner.com</p>
                  <p><strong>Hours:</strong> Monday-Friday, 9 AM - 6 PM ET</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuoteRequest;