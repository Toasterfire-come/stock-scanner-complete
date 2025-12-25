import React from "react";
import SEO from "../components/SEO";
import { marketingMetrics, formatNumber, formatPercent, timeframeCopy } from "../data/marketingMetrics";

const Press = () => {
  const contactEmail = process.env.REACT_APP_PRESS_EMAIL || process.env.REACT_APP_CONTACT_EMAIL || 'noreply.retailtradescanner@gmail.com';
  const { usage, outcomes, testimonials, reliability, enterprise } = marketingMetrics;
  const siteUrl = process.env.REACT_APP_PUBLIC_URL || "https://tradescanpro.com";
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Trade Scan Pro",
    "url": siteUrl,
    "logo": `${siteUrl}/logo.png`,
    "contactPoint": [{
      "@type": "ContactPoint",
      "contactType": "Press",
      "email": contactEmail
    }]
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Press Kit | Trade Scan Pro"
        description="Logos, brand usage, and boilerplate for media. Contact our team for quotes and product reviews."
        url={process.env.REACT_APP_PUBLIC_URL ? `${process.env.REACT_APP_PUBLIC_URL}/press` : "https://tradescanpro.com/press"}
        jsonLd={jsonLd}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Press Kit</h1>
          <p className="text-lg text-gray-700 mb-10">Assets and guidelines for referencing Trade Scan Pro, covering {timeframeCopy()} metrics.</p>

          <div className="space-y-8">
            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">Brand Assets</h2>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li><a className="text-blue-600 hover:underline" href="/logo.png" download>Primary Logo (PNG)</a></li>
                <li><a className="text-blue-600 hover:underline" href="/badges/tradescanpro-badge-light.svg" download>Badge (Light SVG)</a></li>
                <li><a className="text-blue-600 hover:underline" href="/badges/tradescanpro-badge-dark.svg" download>Badge (Dark SVG)</a></li>
              </ul>
            </div>

            <div className="bg-white border rounded-xl p-6 grid sm:grid-cols-2 gap-4">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-3">Key Metrics</h2>
                <ul className="list-disc pl-6 text-gray-700 space-y-1">
                  <li>{`${formatNumber(usage.totalScreenersRunMonthly)}+ screeners run monthly`}</li>
                  <li>{`${formatNumber(usage.alertsDeliveredMonthly)} alerts delivered monthly`}</li>
                  <li>{`${formatPercent(testimonials.retentionPercent90Day)} 90-day retention`}</li>
                  <li>{`${formatPercent(outcomes.averagePortfolioLiftPercent)} average portfolio lift (self-reported)`}</li>
                  <li>{`${formatPercent(reliability.uptimePercent, 2)} platform uptime`}</li>
                </ul>
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-3">Reach</h2>
                <ul className="list-disc pl-6 text-gray-700 space-y-1">
                  <li>{`${formatNumber(usage.activeAccounts)} active accounts`}</li>
                  <li>{`${formatNumber(usage.teamsOnPlatform)} customer teams across ${enterprise.countriesServed} countries`}</li>
                  <li>{`${formatNumber(testimonials.verifiedCaseStudies)} verified case studies`}</li>
                </ul>
              </div>
            </div>

            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">Company Boilerplate</h2>
              <p className="text-gray-700">
                Trade Scan Pro delivers professional-grade screening, alerts, and analytics across {formatNumber(usage.coverageUniverse)}+ equities. During {timeframeCopy()}, customers ran {formatNumber(usage.totalScreenersRunMonthly)}+ screeners per month, delivered {formatNumber(usage.alertsDeliveredMonthly)} alerts, and achieved {formatPercent(outcomes.averagePortfolioLiftPercent)} average portfolio lift while maintaining {formatPercent(reliability.uptimePercent, 2)} uptime.
              </p>
            </div>

            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">Press Contact</h2>
              <p className="text-gray-700">Email: <a className="text-blue-600 hover:underline" href={`mailto:${contactEmail}`}>{contactEmail}</a></p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Press;

