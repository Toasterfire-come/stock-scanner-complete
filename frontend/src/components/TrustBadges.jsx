import React from 'react';
import { Shield, Lock, CreditCard, RefreshCw, Award, CheckCircle } from 'lucide-react';
import { Card } from './ui/card';

const TrustBadges = ({ variant = 'full' }) => {
  const badges = [
    {
      icon: <Lock className="h-6 w-6" />,
      title: "256-Bit SSL Encryption",
      description: "Your payment information is securely encrypted",
      color: "text-green-600"
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Secure Payment Processing",
      description: "Powered by PayPal - Industry leading security",
      color: "text-blue-600"
    },
    {
      icon: <RefreshCw className="h-6 w-6" />,
      title: "30-Day Money-Back Guarantee",
      description: "Full refund if you're not satisfied",
      color: "text-purple-600"
    },
    {
      icon: <CreditCard className="h-6 w-6" />,
      title: "Cancel Anytime",
      description: "No long-term contracts or cancellation fees",
      color: "text-indigo-600"
    },
    {
      icon: <Award className="h-6 w-6" />,
      title: "Trusted by 5,000+ Traders",
      description: "Join thousands of satisfied customers",
      color: "text-orange-600"
    },
    {
      icon: <CheckCircle className="h-6 w-6" />,
      title: "PCI DSS Compliant",
      description: "Meeting the highest security standards",
      color: "text-teal-600"
    }
  ];

  if (variant === 'compact') {
    return (
      <div className="flex flex-wrap items-center justify-center gap-4 py-4">
        {badges.slice(0, 3).map((badge, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <span className={badge.color}>{badge.icon}</span>
            <span className="font-medium text-gray-700">{badge.title}</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="w-full py-8">
      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Secure & Trusted</h3>
        <p className="text-gray-600">Your security and satisfaction are our top priorities</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {badges.map((badge, index) => (
          <Card key={index} className="p-4 hover:shadow-lg transition-shadow border-l-4" style={{ borderLeftColor: badge.color.replace('text-', '') }}>
            <div className="flex items-start gap-3">
              <div className={`${badge.color} flex-shrink-0`}>
                {badge.icon}
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">{badge.title}</h4>
                <p className="text-sm text-gray-600">{badge.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="mt-6 text-center">
        <div className="inline-flex items-center gap-2 text-sm text-gray-500">
          <Lock className="h-4 w-4" />
          <span>All transactions are secure and encrypted</span>
        </div>
      </div>
    </div>
  );
};

export default TrustBadges;
