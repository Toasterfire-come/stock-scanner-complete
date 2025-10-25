import React from "react";
import SEO from "../components/SEO";

const Widgets = () => {
  const snippet = (
    `<script defer src="https://tradescanpro.com/widgets/market-badge.js"></script>\n` +
    `<div data-tradescan-badge data-symbol="AAPL" data-theme="light"></div>`
  );
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Widgets | Trade Scan Pro"
        description="Free embeddable stock market badge widget with attribution link. Copy and paste the snippet to add a badge to your site."
        url="https://tradescanpro.com/widgets"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "TechArticle",
          "headline": "Trade Scan Pro Widgets",
          "about": "Embeddable market badge"
        }}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Embeddable Widget</h1>
          <p className="text-lg text-gray-700 mb-8">Add a lightweight market badge with a single script tag.</p>

          <div className="bg-white border rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">Quick Start</h2>
            <p className="text-gray-700 mb-3">Paste this snippet where you want the badge to appear:</p>
            <pre className="overflow-auto text-sm bg-gray-50 border rounded p-3">
              <code>{snippet}</code>
            </pre>
            <p className="text-gray-700 mt-4">Options: <span className="font-mono">data-symbol</span> (e.g., AAPL) and <span className="font-mono">data-theme</span> (light|dark).</p>
          </div>

          <div className="bg-white border rounded-xl p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">Preview</h2>
            <div className="mt-3">
              <script defer src="/widgets/market-badge.js"></script>
              <div data-tradescan-badge data-symbol="AAPL" data-theme="light"></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Widgets;

