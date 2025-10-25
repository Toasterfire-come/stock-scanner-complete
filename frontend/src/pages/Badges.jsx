import React from "react";
import SEO from "../components/SEO";

const Badges = () => {
  const htmlLight = `<a href=\"https://tradescanpro.com/?utm_source=badge&utm_medium=referral\" rel=\"noopener\"><img src=\"https://tradescanpro.com/badges/tradescanpro-badge-light.svg\" alt=\"Powered by Trade Scan Pro\" width=\"180\" height=\"48\"/></a>`;
  const htmlDark = `<a href=\"https://tradescanpro.com/?utm_source=badge&utm_medium=referral\" rel=\"noopener\"><img src=\"https://tradescanpro.com/badges/tradescanpro-badge-dark.svg\" alt=\"Powered by Trade Scan Pro\" width=\"180\" height=\"48\"/></a>`;
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Badges | Trade Scan Pro"
        description="Download partner badges and copy HTML to link back to Trade Scan Pro."
        url="https://tradescanpro.com/badges"
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Partner Badges</h1>
          <p className="text-lg text-gray-700 mb-8">Choose a badge and copy the HTML snippet to add to your site.</p>

          <div className="grid sm:grid-cols-2 gap-6">
            <div className="bg-white border rounded-xl p-6">
              <img src="/badges/tradescanpro-badge-light.svg" alt="Trade Scan Pro Badge Light" className="mb-4 w-[180px] h-[48px]" />
              <pre className="overflow-auto text-sm bg-gray-50 border rounded p-3"><code>{htmlLight}</code></pre>
              <div className="mt-3"><a className="text-blue-600 hover:underline" href="/badges/tradescanpro-badge-light.svg" download>Download SVG</a></div>
            </div>
            <div className="bg-white border rounded-xl p-6">
              <img src="/badges/tradescanpro-badge-dark.svg" alt="Trade Scan Pro Badge Dark" className="mb-4 w-[180px] h-[48px]" />
              <pre className="overflow-auto text-sm bg-gray-50 border rounded p-3"><code>{htmlDark}</code></pre>
              <div className="mt-3"><a className="text-blue-600 hover:underline" href="/badges/tradescanpro-badge-dark.svg" download>Download SVG</a></div>
            </div>
          </div>

          <p className="text-sm text-gray-500 mt-6">Tip: add rel="nofollow" if required by your editorial policy.</p>
        </div>
      </section>
    </div>
  );
};

export default Badges;

