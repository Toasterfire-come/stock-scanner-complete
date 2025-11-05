import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { ChevronDown, HelpCircle } from 'lucide-react';

const PricingFAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "How does the 7-day free trial work?",
      answer: "Your free trial lasts until the 1st of the next month. No credit card required to start. You'll have full access to all features of your chosen plan during the trial period. If you don't cancel before the trial ends, you'll be automatically charged on the 1st of the next month."
    },
    {
      question: "Can I cancel my subscription at any time?",
      answer: "Yes, absolutely! You can cancel your subscription at any time with no cancellation fees or penalties. Once canceled, you'll retain access until the end of your current billing period. No questions asked, no hassle."
    },
    {
      question: "What payment methods do you accept?",
      answer: "We accept all major credit cards (Visa, Mastercard, American Express, Discover) and PayPal. All payments are processed securely through PayPal's payment gateway with industry-standard 256-bit SSL encryption."
    },
    {
      question: "Do you offer refunds?",
      answer: "Yes, we offer a 30-day money-back guarantee. If you're not satisfied with Trade Scan Pro within the first 30 days of your subscription, contact our support team for a full refund. No questions asked."
    },
    {
      question: "What's the difference between Bronze, Silver, and Gold plans?",
      answer: "Bronze is perfect for casual traders with 150 API calls/day. Silver offers 500 calls/day plus advanced filtering, portfolio tracking, and insider data. Gold provides unlimited API calls, REST API access, webhooks, and priority 24/7 support with a dedicated account manager."
    },
    {
      question: "Can I upgrade or downgrade my plan?",
      answer: "Yes, you can change your plan at any time. When upgrading, you'll be charged a prorated amount for the remainder of your billing cycle. When downgrading, your new rate applies at the start of your next billing cycle, and you'll keep your current features until then."
    },
    {
      question: "How accurate is your market data?",
      answer: "We source data from reliable market data providers with direct exchange feeds. Our data is updated in real-time during market hours. We cover 7,000+ NYSE and NASDAQ stocks with 14 technical indicators. While we strive for accuracy, we recommend verifying critical data with your broker."
    },
    {
      question: "Do you provide investment advice?",
      answer: "No, Trade Scan Pro is a data and analytical tool only. We do not provide investment advice, recommendations, or financial planning services. All investment decisions should be made based on your own research and consultation with qualified financial advisors."
    },
    {
      question: "What happens if I exceed my API call limit?",
      answer: "If you exceed your daily or monthly API call limit, your requests will be temporarily throttled until the next reset period. You'll receive email notifications when you reach 80% and 95% of your limit. Consider upgrading to a higher plan if you consistently hit your limits."
    },
    {
      question: "Is there a long-term contract or commitment?",
      answer: "No, all our plans are month-to-month with no long-term contracts. You can cancel at any time. We believe in earning your business every month by providing exceptional value and service."
    },
    {
      question: "Do you offer discounts for annual subscriptions?",
      answer: "Yes! Annual subscriptions receive a 15% discount compared to monthly billing. Contact our sales team for current annual pricing and additional volume discounts for teams or institutions."
    },
    {
      question: "Can I use Trade Scan Pro on multiple devices?",
      answer: "Yes, your subscription allows you to access Trade Scan Pro from any device with an internet connection. However, simultaneous sessions from the same account may be limited based on your plan. Contact us for multi-user enterprise plans."
    },
    {
      question: "How do alerts work?",
      answer: "Set custom alerts for price movements, volume spikes, and technical indicator thresholds. You'll receive instant notifications via email. Silver and Gold plans also include push notifications. Alerts are checked in real-time during market hours."
    },
    {
      question: "Do you offer an API for developers?",
      answer: "Yes, Gold plan subscribers get full REST API access with comprehensive documentation. This allows you to integrate Trade Scan Pro data into your own applications, trading bots, or analytical tools. WebSocket feeds are also available for real-time data streaming."
    },
    {
      question: "What kind of support do you provide?",
      answer: "Bronze includes standard email support (48-hour response). Silver gets priority email support (24-hour response). Gold receives 24/7 priority support with 4-hour response time, phone support, and a dedicated account manager. All plans include access to our knowledge base and video tutorials."
    }
  ];

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-3 flex items-center justify-center gap-2">
          <HelpCircle className="h-8 w-8 text-blue-600" />
          Frequently Asked Questions
        </h2>
        <p className="text-gray-600 text-lg">
          Everything you need to know about pricing and plans
        </p>
      </div>

      {faqs.map((faq, index) => (
        <Collapsible
          key={index}
          open={openIndex === index}
          onOpenChange={() => setOpenIndex(openIndex === index ? null : index)}
        >
          <Card className="border-l-4 border-l-blue-500 hover:shadow-md transition-shadow">
            <CollapsibleTrigger className="w-full">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-left pr-4">{faq.question}</h3>
                  <ChevronDown
                    className={`h-5 w-5 text-gray-400 flex-shrink-0 transition-transform ${
                      openIndex === index ? 'rotate-180' : ''
                    }`}
                  />
                </div>
              </CardContent>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="px-6 pb-6 pt-0">
                <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
              </CardContent>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      ))}
    </div>
  );
};

export default PricingFAQ;
