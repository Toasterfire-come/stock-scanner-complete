import React from "react";

const QuickMiniFAQ = () => {
  const items = [
    { q: "Is data real-time?", a: "Yes, key endpoints update in real time with >99.9% uptime." },
    { q: "Can I cancel anytime?", a: "Yes. Manage your plan in Account → Plan & Billing." },
    { q: "Are sources reliable?", a: "We aggregate from major exchanges and validated providers." },
  ];
  return (
    <div className="mt-6 grid sm:grid-cols-3 gap-4 text-left">
      {items.map((it, i) => (
        <div key={i} className="bg-white/70 border rounded-lg p-4">
          <div className="font-semibold text-gray-900 mb-1">{it.q}</div>
          <div className="text-sm text-gray-600">{it.a}</div>
        </div>
      ))}
    </div>
  );
};

export default QuickMiniFAQ;

