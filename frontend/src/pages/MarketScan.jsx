import React from "react";
import SEO from "../components/SEO";
import { Link } from "react-router-dom";

const MarketScan = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Market Scan | Real-Time Market Scanning"
        description="Run a market scan to find movers, breakouts, and unusual volume. Real-time scanning with alerts and watchlists."
        url={process.env.REACT_APP_PUBLIC_URL ? `${process.env.REACT_APP_PUBLIC_URL}/market-scan` : "https://tradescanpro.com/market-scan"}
        jsonLd={{"@context":"https://schema.org","@type":"WebPage","name":"Market Scan","url": process.env.REACT_APP_PUBLIC_URL ? `${process.env.REACT_APP_PUBLIC_URL}/market-scan` : "https://tradescanpro.com/market-scan"}}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Market Scan</h1>
          <p className="text-lg text-gray-700 mb-6">
            Scan the market in real time to discover momentum, breakouts, and unusual volume. Save scans, set alerts, and track watchlists.
          </p>
          <div className="bg-white border rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">Scan Ideas</h2>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Top gainers with high relative volume</li>
              <li>New 52-week highs with rising volume</li>
              <li>RSI over 60 with positive price action</li>
              <li>Insider buying within 7 days</li>
            </ul>
          </div>
          <div className="bg-white border rounded-xl p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">Run a Scan</h2>
            <p className="text-gray-700 mb-4">Use templates or build your own scanner in minutes.</p>
            <Link className="text-blue-600 hover:underline" to="/screener">Open Screener →</Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default MarketScan;

