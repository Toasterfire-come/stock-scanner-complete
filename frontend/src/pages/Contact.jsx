import React, { useState } from "react";
import SEO from "../components/SEO";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";
import { 
  Mail, 
  MessageSquare,
  Send,
  CheckCircle,
  Building,
  HelpCircle
} from "lucide-react";
import { toast } from "sonner";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    subject: "",
    message: "",
    inquiryType: "general"
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://api.retailtradescanner.com'}/api/enterprise/contact/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: formData.company || 'Individual',
          contact_email: formData.email,
          contact_name: formData.name,
          phone: '',
          message: `${formData.subject}\n\n${formData.message}`,
          solution_type: formData.inquiryType
        })
      });

      if (response.ok) {
        toast.success("Message sent successfully! We'll get back to you within 24 hours.");
        
        // Reset form
        setFormData({
          name: "",
          email: "",
          company: "",
          subject: "",
          message: "",
          inquiryType: "general"
        });
      } else {
        throw new Error('Failed to submit form');
      }
    } catch (error) {
      console.error('Contact form submission failed:', error);
      toast.error("Failed to send message. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const inquiryTypes = [
    { value: "general", label: "General Inquiry" },
    { value: "support", label: "Technical Support" },
    { value: "sales", label: "Sales & Pricing" },
    { value: "enterprise", label: "Enterprise Solutions" },
    { value: "api", label: "API Access" },
    { value: "partnership", label: "Partnership" },
    { value: "billing", label: "Billing Question" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Contact Us | Trade Scan Pro"
        description="Contact Trade Scan Pro for support, sales, enterprise solutions, and API access. We typically respond within 24 hours."
        url="https://tradescanpro.com/contact"
        jsonLdUrls={["/structured/contact.jsonld"]}
      />
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <MessageSquare className="h-4 w-4 mr-2" />
              Get in Touch
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              We're Here to
              <span className="text-blue-600 block">Help You Succeed</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              Have questions about Trade Scan Pro? Need help getting started? 
              Our team of trading experts is ready to assist you.
            </p>

            <div className="text-center mb-8">
              <p className="text-lg text-gray-600">
                Email us directly at: <span className="font-semibold text-blue-600">
                  {process.env.REACT_APP_CONTACT_EMAIL || 'noreply.retailtradescanner@gmail.com'}
                </span>
              </p>
              <p className="text-sm text-gray-500 mt-2">
                We typically respond within 24 hours
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <Card className="shadow-xl">
              <CardHeader className="text-center">
                <CardTitle className="text-3xl">Send us a Message</CardTitle>
                <p className="text-gray-600">
                  Fill out the form below and we'll get back to you within 24 hours.
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="name">Full Name *</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => handleInputChange("name", e.target.value)}
                        placeholder="John Doe"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">Email Address *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange("email", e.target.value)}
                        placeholder="john@example.com"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="company">Company (Optional)</Label>
                    <Input
                      id="company"
                      value={formData.company}
                      onChange={(e) => handleInputChange("company", e.target.value)}
                      placeholder="Your Company Name"
                    />
                  </div>

                  <div>
                    <Label htmlFor="inquiryType">Inquiry Type</Label>
                    <select
                      id="inquiryType"
                      value={formData.inquiryType}
                      onChange={(e) => handleInputChange("inquiryType", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {inquiryTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="subject">Subject *</Label>
                    <Input
                      id="subject"
                      value={formData.subject}
                      onChange={(e) => handleInputChange("subject", e.target.value)}
                      placeholder="How can we help you?"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="message">Message *</Label>
                    <Textarea
                      id="message"
                      value={formData.message}
                      onChange={(e) => handleInputChange("message", e.target.value)}
                      placeholder="Please provide details about your inquiry..."
                      rows={6}
                      required
                    />
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full text-lg py-6"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>Sending...</>
                    ) : (
                      <>
                        <Send className="h-5 w-5 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Frequently Asked Questions
              </h2>
              <p className="text-xl text-gray-600">
                Quick answers to common questions
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    How quickly do you respond to support requests?
                  </h3>
                  <p className="text-gray-600">
                    We respond to all support requests within 24 hours. 
                    Premium subscribers receive priority support with faster response times.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    What data sources do you use?
                  </h3>
                  <p className="text-gray-600">
                    We use Yahoo Finance for real-time stock data and proprietary news scraping 
                    to provide comprehensive market coverage of 7,000+ NYSE & NASDAQ stocks.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    Can you help with trading strategy?
                  </h3>
                  <p className="text-gray-600">
                    While we don't provide investment advice, our support team can help you 
                    understand how to use our screening tools and analytics effectively.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    Do you offer API access?
                  </h3>
                  <p className="text-gray-600">
                    Yes! Gold plan subscribers get full API access with developer tools, 
                    documentation, and usage statistics for custom integrations.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    What about enterprise solutions?
                  </h3>
                  <p className="text-gray-600">
                    We offer white-label solutions, custom integrations, and enterprise-grade 
                    features. Contact us to discuss your specific requirements.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    How accurate is your market data?
                  </h3>
                  <p className="text-gray-600">
                    Our data is sourced from Yahoo Finance with real-time updates. We maintain 
                    99.9% uptime and ensure data accuracy through multiple validation layers.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Enterprise CTA */}
      <section className="py-24 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <Building className="h-16 w-16 mx-auto mb-6" />
          <h2 className="text-4xl font-bold mb-6">
            Enterprise Solutions Available
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Need custom integrations, white-label solutions, or enterprise-grade features? 
            We work with institutions and large trading firms to provide tailored solutions.
          </p>
          <Button size="lg" variant="secondary" className="text-blue-600">
            <Mail className="h-5 w-5 mr-2" />
            Contact Enterprise Sales
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Contact;