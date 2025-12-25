import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import { 
  Building2, 
  Users, 
  Shield, 
  Zap, 
  CheckCircle, 
  Mail, 
  Phone, 
  Globe,
  ArrowRight,
  Star
} from 'lucide-react';
import { submitEnterpriseContact } from '../../api/client';
import { toast } from 'sonner';
import logger from '../../lib/logger';

const EnterpriseContact = () => {
  const [formData, setFormData] = useState({
    company_name: '',
    contact_name: '',
    contact_email: '',
    phone: '',
    message: '',
    solution_type: ''
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    const requiredFields = ['company_name', 'contact_name', 'contact_email', 'phone', 'message', 'solution_type'];
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
      const response = await submitEnterpriseContact(formData);
      if (response.success) {
        setSubmitted(true);
        toast.success('Enterprise inquiry submitted successfully!');
      } else {
        toast.error(response.message || 'Failed to submit inquiry');
      }
    } catch (error) {
      logger.error('Failed to submit contact form:', error);
      toast.error('Failed to submit inquiry. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const enterpriseFeatures = [
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Advanced security features including SSO, audit logs, and compliance certifications'
    },
    {
      icon: Users,
      title: 'Team Management',
      description: 'Multi-user accounts with role-based access control and team collaboration tools'
    },
    {
      icon: Zap,
      title: 'Priority Support',
      description: 'Dedicated support team with SLA guarantees and direct access to engineering'
    },
    {
      icon: Globe,
      title: 'White-label Solutions',
      description: 'Fully customizable platform with your branding and domain integration'
    }
  ];

  const solutions = [
    {
      title: 'Financial Institutions',
      description: 'Complete trading platform solutions for banks and investment firms',
      features: ['Custom branding', 'API integration', 'Compliance tools', 'Multi-entity support']
    },
    {
      title: 'Wealth Management',
      description: 'Portfolio management tools for advisors and wealth management firms',
      features: ['Client portals', 'Risk assessment', 'Reporting suite', 'Performance analytics']
    },
    {
      title: 'Fintech Startups',
      description: 'Scalable infrastructure and data feeds for emerging financial technology companies',
      features: ['Real-time data', 'Scalable APIs', 'Developer tools', 'Fast deployment']
    },
    {
      title: 'Educational Platforms',
      description: 'Trading simulators and educational tools for schools and training programs',
      features: ['Virtual trading', 'Course integration', 'Progress tracking', 'Safe environment']
    }
  ];

  if (submitted) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-8">
            <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Thank You!</h1>
            <p className="text-gray-600">
              Your enterprise inquiry has been submitted successfully. Our team will review your requirements and get back to you within 24 hours.
            </p>
          </div>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">What Happens Next?</h2>
              <div className="space-y-4 text-left">
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 font-semibold text-sm">1</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Initial Review</p>
                    <p className="text-sm text-gray-600">Our enterprise team will review your requirements and prepare a tailored response.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 font-semibold text-sm">2</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Discovery Call</p>
                    <p className="text-sm text-gray-600">We'll schedule a call to discuss your specific needs and demonstrate relevant solutions.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 font-semibold text-sm">3</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Custom Proposal</p>
                    <p className="text-sm text-gray-600">Receive a detailed proposal with pricing, timeline, and implementation plan.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="mt-8">
            <Button asChild className="bg-blue-600 hover:bg-blue-700">
              <Link to="/">Return to Homepage</Link>
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
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Enterprise Solutions</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Powerful, scalable trading platforms and market data solutions designed for institutional clients, 
            financial service providers, and large organizations.
          </p>
        </div>

        {/* Enterprise Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {enterpriseFeatures.map((feature, index) => (
            <Card key={index}>
              <CardContent className="p-6 text-center">
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Get Started with Enterprise
                </CardTitle>
                <CardDescription>
                  Tell us about your organization and requirements. Our enterprise team will create a customized solution for you.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
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

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Solution Type *
                    </label>
                    <Select onValueChange={(value) => handleInputChange('solution_type', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select the type of solution you need" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="financial_institution">Financial Institution Platform</SelectItem>
                        <SelectItem value="wealth_management">Wealth Management Solution</SelectItem>
                        <SelectItem value="fintech_startup">Fintech Infrastructure</SelectItem>
                        <SelectItem value="educational">Educational Platform</SelectItem>
                        <SelectItem value="white_label">White-label Solution</SelectItem>
                        <SelectItem value="api_access">Enterprise API Access</SelectItem>
                        <SelectItem value="custom">Custom Solution</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Project Details *
                    </label>
                    <Textarea
                      value={formData.message}
                      onChange={(e) => handleInputChange('message', e.target.value)}
                      placeholder="Please describe your requirements, expected number of users, timeline, and any specific features you need..."
                      rows={5}
                      required
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
                        Submitting...
                      </>
                    ) : (
                      <>
                        Submit Enterprise Inquiry
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Solutions Overview */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Industry Solutions</h2>
              <p className="text-gray-600 mb-6">
                We've developed specialized solutions for various industries and use cases.
              </p>
            </div>

            <div className="space-y-4">
              {solutions.map((solution, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <h3 className="font-semibold text-gray-900 mb-2">{solution.title}</h3>
                    <p className="text-gray-600 mb-3">{solution.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {solution.features.map((feature, featureIndex) => (
                        <Badge key={featureIndex} variant="secondary" className="text-xs">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Contact Information */}
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Direct Contact</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Mail className="h-4 w-4 text-gray-600" />
                    <span className="text-gray-900">enterprise@retailtradescanner.com</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-gray-600" />
                    <span className="text-gray-900">+1 (555) 123-4567</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Globe className="h-4 w-4 text-gray-600" />
                    <span className="text-gray-900">Available 24/7 for enterprise clients</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Trusted by Industry Leaders</h2>
            <p className="text-gray-600">Join hundreds of organizations that rely on our enterprise solutions</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">500+</div>
              <p className="text-gray-600">Enterprise Clients</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <p className="text-gray-600">Uptime SLA</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
              <p className="text-gray-600">Enterprise Support</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseContact;