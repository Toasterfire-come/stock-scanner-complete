import React from "react";

const ScreenerDemo = () => {
  return (
    <section className="py-10 sm:py-14 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-6 sm:mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">See It In Action</h2>
          <p className="text-gray-600">Query → Results in under 10 seconds</p>
        </div>
        <div className="max-w-4xl mx-auto">
          <div className="rounded-xl overflow-hidden border bg-black">
            <video
              className="w-full h-auto"
              autoPlay
              muted
              loop
              playsInline
              preload="metadata"
              poster="/demo/screener-poster.jpg"
            >
              <source src="/demo/screener-demo.mp4" type="video/mp4" />
            </video>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ScreenerDemo;

