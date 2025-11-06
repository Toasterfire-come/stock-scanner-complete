import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../ui/collapsible";
import { ChevronDown } from "lucide-react";

const defaultFaqs = [
  {
    question: "How accurate is your market data?",
    answer: "Our data is sourced directly from major exchanges and updated in real-time. We maintain 99.9% uptime and ensure data accuracy through multiple validation layers."
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Yes, you can cancel your subscription at any time. There are no long-term contracts or cancellation fees. Your subscription will remain active until the end of your current billing period."
  },
  {
    question: "Do you offer API access?",
    answer: "Yes! Our Silver and Gold plans include full REST API access, allowing you to integrate our data into your own applications and trading systems."
  },
  {
    question: "What's the difference between plans?",
    answer: "Plans differ mainly in the number of API calls per month, available features, and support level. Bronze is great for casual traders, Silver for active traders, and Gold for professional traders and institutions."
  },
  {
    question: "How does the API call counting work?",
    answer: "Different operations consume different amounts of API calls: listing all stocks (5 calls), single stock data (1 call), running screeners (2 calls), creating alerts (2 calls), loading market data (2 calls), and making watchlists (2 calls)."
  }
];

const HomeFAQ = ({ faqs = defaultFaqs }) => {
  const [openIdx, setOpenIdx] = useState(null);
  return (
    <section className="py-16 sm:py-24 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4 sm:mb-6">
            Frequently Asked Questions
          </h2>
          <p className="text-xl sm:text-2xl text-gray-600">
            Everything you need to know about getting started
          </p>
        </div>
        <div className="max-w-4xl mx-auto space-y-4">
          {faqs.map((faq, index) => (
            <Collapsible
              key={index}
              open={openIdx === index}
              onOpenChange={() => setOpenIdx(openIdx === index ? null : index)}
            >
              <Card className="hover:shadow-lg transition-shadow">
                <CollapsibleTrigger className="w-full text-left">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0">
                    <CardTitle className="text-lg sm:text-xl font-semibold">{faq.question}</CardTitle>
                    <ChevronDown className={`h-6 w-6 text-gray-400 transition-transform ${openIdx === index ? 'rotate-180' : ''}`} />
                  </CardHeader>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <CardContent className="pt-0">
                    <p className="text-gray-700 text-base sm:text-lg leading-relaxed">{faq.answer}</p>
                  </CardContent>
                </CollapsibleContent>
              </Card>
            </Collapsible>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HomeFAQ;

