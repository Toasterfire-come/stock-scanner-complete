import React from "react";
import SEO from "../components/SEO";
import { marketingMetrics, formatNumber, formatPercent, timeframeCopy } from "../data/marketingMetrics";

const Partners = () => {
  const email = process.env.REACT_APP_PARTNERS_EMAIL || process.env.REACT_APP_CONTACT_EMAIL || 'noreply.retailtradescanner@gmail.com';
  const { usage, enterprise, outcomes } = marketingMetrics;
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Partners | Trade Scan Pro"
        description="Partner with Trade Scan Pro. Affiliates, data partners, and integrations welcome."
        url="https://tradescanpro.com/partners"
        jsonLd={{"@context":"https://schema.org","@type":"AboutPage","name":"Partners","url":"https://tradescanpro.com/partners"}}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Partners</h1>
          <p className="text-lg text-gray-700 mb-6">We collaborate with financial publishers, communities, and data providers powering {formatNumber(usage.totalScreenersRunMonthly)}+ monthly screenings and {formatNumber(enterprise.apiThroughputDailyMillions)}M+ daily API calls ({timeframeCopy()}).</p>

          <div className="bg-white border rounded-xl p-6 space-y-3">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">Opportunities</h2>
              <ul className="list-disc pl-6 text-gray-700 mt-2 space-y-1">
                <li>Content partnerships reaching {formatNumber(usage.activeAccounts)} active accounts</li>
                <li>Embeddable market data widgets with {formatNumber(usage.watchlistsSyncedMonthly)} monthly syncs</li>
                <li>Affiliate and referral programs averaging {formatPercent(outcomes.trialToPaidConversionPercent)} trial conversion</li>
                <li>API integrations sustaining {formatNumber(enterprise.apiThroughputDailyMillions)}M+ calls/day</li>
              </ul>
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">Contact</h2>
              <p className="text-gray-700">Email: <a className="text-blue-600 hover:underline" href={`mailto:${email}`}>{email}</a></p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Partners;

