import React from "react";
import SEO from "../components/SEO";
import { Link } from "react-router-dom";

const StockFilter = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Stock Filter | Fast, Flexible Filters for Stocks"
        description="Build a stock filter with price, volume, fundamentals, and technicals. Create saved filters and alerts with Trade Scan Pro."
        url={process.env.REACT_APP_PUBLIC_URL ? `${process.env.REACT_APP_PUBLIC_URL}/stock-filter` : "https://tradescanpro.com/stock-filter"}
        jsonLd={{"@context":"https://schema.org","@type":"WebPage","name":"Stock Filter","url": process.env.REACT_APP_PUBLIC_URL ? `${process.env.REACT_APP_PUBLIC_URL}/stock-filter` : "https://tradescanpro.com/stock-filter"}}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Stock Filter</h1>
          <p className="text-lg text-gray-700 mb-6">
            Filter thousands of stocks by price, market cap, volume, fundamentals, and technical signals. Save filters, set alerts, and run them anytime.
          </p>
          <div className="bg-white border rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">Popular Filter Criteria</h2>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Price range and average daily volume</li>
              <li>Market cap, PE ratio, dividend yield</li>
              <li>RSI, MACD, 52-week high/low, moving averages</li>
              <li>Insider buys and fair value deviation</li>
            </ul>
          </div>
          <div className="bg-white border rounded-xl p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">Try the Filter</h2>
            <p className="text-gray-700 mb-4">Start with a template and customize your conditions.</p>
            <Link className="text-blue-600 hover:underline" to="/screener">Open Screener →</Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default StockFilter;

