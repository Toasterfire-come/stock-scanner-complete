import React from "react";
import SEO from "../components/SEO";

const Resources = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Resources | Trade Scan Pro"
        description="Free resources to link to Trade Scan Pro: embeddable market widgets, partner badges, press kit, and helpful guides."
        url="https://tradescanpro.com/resources"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "CollectionPage",
          "name": "Trade Scan Pro Resources",
          "url": "https://tradescanpro.com/resources"
        }}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Resources</h1>
          <p className="text-lg text-gray-700 mb-10">
            Use these resources to reference or link to Trade Scan Pro. We provide easy-to-embed widgets,
            partner badges, and a press kit for mentions and articles.
          </p>

          <div className="space-y-8">
            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Embeddable Widgets</h2>
              <p className="text-gray-700 mb-4">Add a market badge to your site with a single script tag.</p>
              <a className="text-blue-600 hover:underline" href="/widgets">View widgets and snippet →</a>
            </div>

            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Partner Badges</h2>
              <p className="text-gray-700 mb-4">Showcase your integration with Trade Scan Pro using our SVG badges.</p>
              <a className="text-blue-600 hover:underline" href="/badges">Get badges and HTML →</a>
            </div>

            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Press Kit</h2>
              <p className="text-gray-700 mb-4">Logos and company boilerplate for media mentions and reviews.</p>
              <a className="text-blue-600 hover:underline" href="/press">Explore press kit →</a>
            </div>

            <div className="bg-white border rounded-xl p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Documentation</h2>
              <p className="text-gray-700 mb-4">Guides for getting started, creating screeners, and analytics.</p>
              <a className="text-blue-600 hover:underline" href="/docs">Browse docs →</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Resources;

