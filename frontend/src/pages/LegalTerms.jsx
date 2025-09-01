import React from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { ArrowLeft, Mail, MapPin, FileText } from "lucide-react";

const LegalTerms = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Button asChild variant="ghost" className="mb-4">
            <Link to="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Link>
          </Button>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
          <p className="text-gray-600">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        {/* Terms Content */}
        <Card>
          <CardContent className="prose prose-lg max-w-none p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-700 mb-6">
              By accessing and using Retail Trade Scanner ("Service"), you accept and agree to be bound by the terms and provision of this agreement.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Description of Service</h2>
            <p className="text-gray-700 mb-6">
              Retail Trade Scanner is a financial data and analysis platform that provides real-time stock market data, portfolio management tools,
              and trading analytics. The Service is provided for informational purposes only and is not intended as investment advice.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">3. User Account</h2>
            <p className="text-gray-700 mb-4">
              To access certain features of the Service, you must register for an account. You are responsible for:
            </p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>Maintaining the confidentiality of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us immediately of any unauthorized use</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Acceptable Use</h2>
            <p className="text-gray-700 mb-4">You agree not to:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>Use the Service for any unlawful purpose or in violation of these terms</li>
              <li>Attempt to gain unauthorized access to any portion of the Service</li>
              <li>Interfere with or disrupt the Service or servers</li>
              <li>Reproduce, duplicate, copy, sell, or exploit any portion of the Service without permission</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Financial Data Disclaimer</h2>
            <p className="text-gray-700 mb-6">
              The financial data provided through our Service is for informational purposes only. We do not guarantee the accuracy,
              completeness, or timeliness of any data. Market data may be delayed and should not be considered real-time for trading purposes.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Investment Disclaimer</h2>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <p className="text-gray-800">
                <strong>Important:</strong> The Service is not intended to provide investment advice. All investment decisions should be made
                based on your own research and consultation with qualified financial advisors. Trading stocks involves risk of loss.
              </p>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Subscription and Billing</h2>
            <p className="text-gray-700 mb-6">
              Paid subscriptions are billed in advance on a monthly or annual basis. You may cancel your subscription at any time.
              Refunds are provided according to our refund policy.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">8. API Usage Limits</h2>
            <p className="text-gray-700 mb-6">
              API usage is subject to rate limits based on your subscription plan. Exceeding these limits may result in temporary
              suspension of service. Fair usage policies apply to all plans.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Limitation of Liability</h2>
            <p className="text-gray-700 mb-6">
              Retail Trade Scanner shall not be liable for any indirect, incidental, special, consequential, or punitive damages,
              including but not limited to loss of profits, data, or trading losses.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Termination</h2>
            <p className="text-gray-700 mb-6">
              We may terminate or suspend your account immediately, without prior notice, if you breach these Terms of Service.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Changes to Terms</h2>
            <p className="text-gray-700 mb-6">
              We reserve the right to modify these terms at any time. Continued use of the Service after changes constitutes
              acceptance of the new terms.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Contact Information</h2>
            <p className="text-gray-700 mb-4">
              If you have any questions about these Terms of Service, please contact us at:
            </p>
            <div className="bg-blue-50 rounded-lg p-6 mb-8">
              <div className="flex items-center mb-3">
                <Mail className="h-5 w-5 text-blue-600 mr-3" />
                <span className="font-semibold text-gray-900">Email:</span>
                <a href="mailto:admin@retailtradescanner.com" className="text-blue-600 hover:text-blue-700 ml-2">
                  admin@retailtradescanner.com
                </a>
              </div>
              <div className="flex items-center">
                <MapPin className="h-5 w-5 text-blue-600 mr-3" />
                <span className="font-semibold text-gray-900">Address:</span>
                <span className="text-gray-700 ml-2">Retail Trade Scanner, Legal Department</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer Links */}
        <div className="mt-12 text-center">
          <div className="flex flex-wrap justify-center gap-6">
            <Button asChild variant="outline">
              <Link to="/legal/privacy">
                <FileText className="h-4 w-4 mr-2" />
                Privacy Policy
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/contact">
                <Mail className="h-4 w-4 mr-2" />
                Contact Us
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalTerms;