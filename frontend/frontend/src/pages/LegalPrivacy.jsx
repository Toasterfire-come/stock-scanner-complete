import React from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { ArrowLeft, Mail, MapPin, FileText, Shield, Lock, Eye, Users, Globe } from "lucide-react";

const LegalPrivacy = () => {
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
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-gray-600">
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>

        {/* Privacy Commitment Banner */}
        <Card className="mb-8 border-l-4 border-l-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center mb-4">
              <Shield className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-xl font-bold text-gray-900">Our Commitment</h2>
            </div>
            <p className="text-gray-700">
              We are committed to protecting your privacy and ensuring the security of your personal information.
              This policy explains how we collect, use, and protect your data.
            </p>
          </CardContent>
        </Card>

        {/* Privacy Content */}
        <Card>
          <CardContent className="prose prose-lg max-w-none p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <Users className="h-6 w-6 mr-3" />
              1. Information We Collect
            </h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-3">Account Information</h3>
            <p className="text-gray-700 mb-4">When you create an account, we collect:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>Name and email address</li>
              <li>Password (encrypted)</li>
              <li>Phone number (optional)</li>
              <li>Company information (optional)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Usage Data</h3>
            <p className="text-gray-700 mb-4">We automatically collect information about how you use our Service:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>API requests and usage patterns</li>
              <li>Feature usage and preferences</li>
              <li>Device and browser information</li>
              <li>IP address and location data</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <Eye className="h-6 w-6 mr-3" />
              2. How We Use Your Information
            </h2>
            <p className="text-gray-700 mb-4">We use your information to:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>Provide and maintain our Service</li>
              <li>Process payments and manage subscriptions</li>
              <li>Send important service notifications</li>
              <li>Provide customer support</li>
              <li>Improve our Service and develop new features</li>
              <li>Comply with legal obligations</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <Lock className="h-6 w-6 mr-3" />
              3. Data Security
            </h2>
            <p className="text-gray-700 mb-4">We implement industry-standard security measures to protect your data:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>End-to-end encryption for data transmission</li>
              <li>Secure data storage with encryption at rest</li>
              <li>Regular security audits and monitoring</li>
              <li>SOC 2 compliance standards</li>
              <li>Limited access controls and authentication</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Data Sharing</h2>
            <p className="text-gray-700 mb-4">
              We do not sell, trade, or rent your personal information to third parties. We may share your information only in the following circumstances:
            </p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>With your explicit consent</li>
              <li>To comply with legal requirements</li>
              <li>To protect our rights or the safety of others</li>
              <li>With trusted service providers who assist in our operations (under strict confidentiality agreements)</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Cookies and Tracking</h2>
            <p className="text-gray-700 mb-4">We use cookies and similar technologies to:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>Remember your login status and preferences</li>
              <li>Analyze usage patterns and improve our Service</li>
              <li>Provide personalized content and features</li>
            </ul>
            <p className="text-gray-700 mb-6">
              You can control cookie settings through your browser preferences.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Your Rights</h2>
            <p className="text-gray-700 mb-4">You have the right to:</p>
            <ul className="list-disc pl-6 mb-6 text-gray-700">
              <li>Access your personal information</li>
              <li>Correct or update your data</li>
              <li>Delete your account and associated data</li>
              <li>Export your data</li>
              <li>Opt-out of marketing communications</li>
            </ul>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Data Retention</h2>
            <p className="text-gray-700 mb-6">
              We retain your information for as long as necessary to provide our Service or as required by law.
              When you delete your account, we will remove your personal information within 30 days, except where
              retention is required for legal or business purposes.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <Globe className="h-6 w-6 mr-3" />
              8. International Data Transfers
            </h2>
            <p className="text-gray-700 mb-6">
              Your information may be processed and stored in countries other than your own. We ensure appropriate
              safeguards are in place to protect your data during international transfers.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Children's Privacy</h2>
            <p className="text-gray-700 mb-6">
              Our Service is not intended for children under 18. We do not knowingly collect personal information
              from children under 18. If you are a parent and believe your child has provided us with personal
              information, please contact us.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Changes to This Policy</h2>
            <p className="text-gray-700 mb-6">
              We may update this Privacy Policy from time to time. We will notify you of any material changes by
              posting the updated policy on this page and updating the "Last updated" date.
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Contact Us</h2>
            <p className="text-gray-700 mb-4">
              If you have questions about this Privacy Policy or want to exercise your rights, please contact us:
            </p>
            <div className="bg-blue-50 rounded-lg p-6 mb-8">
              <div className="flex items-center mb-3">
                <Mail className="h-5 w-5 text-blue-600 mr-3" />
                <span className="font-semibold text-gray-900">Email:</span>
                <a href="mailto:admin@retailtradescanner.com" className="text-blue-600 hover:text-blue-700 ml-2">
                  admin@retailtradescanner.com
                </a>
              </div>
              <div className="flex items-center mb-3">
                <FileText className="h-5 w-5 text-blue-600 mr-3" />
                <span className="font-semibold text-gray-900">Subject:</span>
                <span className="text-gray-700 ml-2">Privacy Policy Inquiry</span>
              </div>
              <div className="flex items-center">
                <MapPin className="h-5 w-5 text-blue-600 mr-3" />
                <span className="font-semibold text-gray-900">Address:</span>
                <span className="text-gray-700 ml-2">Retail Trade Scanner, Privacy Officer</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer Links */}
        <div className="mt-12 text-center">
          <div className="flex flex-wrap justify-center gap-6">
            <Button asChild variant="outline">
              <Link to="/legal/terms">
                <FileText className="h-4 w-4 mr-2" />
                Terms of Service
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

export default LegalPrivacy;