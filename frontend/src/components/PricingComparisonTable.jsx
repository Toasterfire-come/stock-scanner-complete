import React from 'react';
import { Check, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

const PricingComparisonTable = () => {
  const features = [
    {
      category: "Core Features",
      items: [
        { name: "NYSE & NASDAQ Stock Coverage", bronze: true, silver: true, gold: true },
        { name: "Real-Time Stock Scanner", bronze: true, silver: true, gold: true },
        { name: "Technical Indicators", bronze: "7 indicators", silver: "14 indicators", gold: "14 indicators" },
        { name: "Fundamental Screeners", bronze: true, silver: true, gold: true },
        { name: "API Calls per Day", bronze: "150", silver: "500", gold: "Unlimited" },
        { name: "API Calls per Month", bronze: "1,500", silver: "5,000", gold: "Unlimited" },
      ]
    },
    {
      category: "Alerts & Notifications",
      items: [
        { name: "Real-Time Price Alerts", bronze: "50/month", silver: "100/month", gold: "Unlimited" },
        { name: "Email Notifications", bronze: true, silver: true, gold: true },
        { name: "Push Notifications", bronze: false, silver: true, gold: true },
        { name: "Custom Alert Conditions", bronze: "Basic", silver: "Advanced", gold: "Advanced" },
        { name: "Alert History", bronze: "30 days", silver: "90 days", gold: "Unlimited" },
      ]
    },
    {
      category: "Portfolio & Watchlists",
      items: [
        { name: "Watchlists", bronze: "2", silver: "10", gold: "Unlimited" },
        { name: "Portfolio Tracking", bronze: false, silver: "1 portfolio", gold: "Unlimited" },
        { name: "Performance Analytics", bronze: false, silver: true, gold: true },
        { name: "Sector Allocation Analysis", bronze: false, silver: true, gold: true },
        { name: "Export to CSV/Excel", bronze: false, silver: true, gold: true },
      ]
    },
    {
      category: "Data & Analytics",
      items: [
        { name: "Historical Data Access", bronze: "6 months", silver: "2 years", gold: "5 years" },
        { name: "Insider Trading Data", bronze: false, silver: true, gold: true },
        { name: "News Integration", bronze: "Basic", silver: "Advanced", gold: "Advanced" },
        { name: "Market Sentiment Analysis", bronze: false, silver: true, gold: true },
        { name: "Custom Reports", bronze: false, silver: false, gold: true },
      ]
    },
    {
      category: "API & Integration",
      items: [
        { name: "REST API Access", bronze: false, silver: false, gold: true },
        { name: "WebSocket Real-Time Feed", bronze: false, silver: false, gold: true },
        { name: "Webhook Support", bronze: false, silver: false, gold: true },
        { name: "Third-Party Integrations", bronze: false, silver: false, gold: true },
      ]
    },
    {
      category: "Support",
      items: [
        { name: "Email Support", bronze: "Standard", silver: "Priority", gold: "24/7 Priority" },
        { name: "Response Time", bronze: "48 hours", silver: "24 hours", gold: "4 hours" },
        { name: "Phone Support", bronze: false, silver: false, gold: true },
        { name: "Dedicated Account Manager", bronze: false, silver: false, gold: true },
        { name: "Onboarding Assistance", bronze: false, silver: false, gold: true },
      ]
    }
  ];

  const renderCell = (value) => {
    if (typeof value === 'boolean') {
      return value ? (
        <Check className="h-5 w-5 text-green-600 mx-auto" />
      ) : (
        <X className="h-5 w-5 text-gray-300 mx-auto" />
      );
    }
    return <span className="text-sm font-medium">{value}</span>;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-2xl">Complete Feature Comparison</CardTitle>
        <p className="text-gray-600">Compare all features across Bronze, Silver, and Gold plans</p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left p-4 font-semibold">Features</th>
                <th className="text-center p-4 w-32">
                  <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-300">
                    Bronze
                  </Badge>
                  <div className="text-lg font-bold mt-2">$24.99/mo</div>
                </th>
                <th className="text-center p-4 w-32">
                  <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300">
                    Silver
                  </Badge>
                  <div className="text-lg font-bold mt-2">$49.99/mo</div>
                </th>
                <th className="text-center p-4 w-32">
                  <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-300">
                    Gold
                  </Badge>
                  <div className="text-lg font-bold mt-2">$89.99/mo</div>
                </th>
              </tr>
            </thead>
            <tbody>
              {features.map((category, idx) => (
                <React.Fragment key={idx}>
                  <tr className="bg-gray-50">
                    <td colSpan={4} className="p-3 font-semibold text-sm uppercase tracking-wide text-gray-700">
                      {category.category}
                    </td>
                  </tr>
                  {category.items.map((item, itemIdx) => (
                    <tr key={itemIdx} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="p-4 text-sm">{item.name}</td>
                      <td className="p-4 text-center">{renderCell(item.bronze)}</td>
                      <td className="p-4 text-center">{renderCell(item.silver)}</td>
                      <td className="p-4 text-center">{renderCell(item.gold)}</td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default PricingComparisonTable;
