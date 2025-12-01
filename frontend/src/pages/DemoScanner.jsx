import React, { useEffect, useState } from "react";
import SEO from "../components/SEO";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Button } from "../components/ui/button";

const DemoScanner = () => {
  const navigate = useNavigate();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const { data } = await api.get('/stocks/', { params: { limit: 25 } });
        if (!mounted) return;
        const items = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : []);
        setRows(items);
      } catch (e) {
        setError('Failed to load demo data');
      } finally { setLoading(false); }
    })();
    return () => { mounted = false; };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Demo Stock Scanner | First 10 Results"
        description="Preview the stock scanner with the first 10 results. Sign in to view full results, alerts, and advanced filters."
        url="https://tradescanpro.com/demo-scanner"
        jsonLd={{"@context":"https://schema.org","@type":"WebPage","name":"Demo Stock Scanner","url":"https://tradescanpro.com/demo-scanner"}}
      />
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 max-w-5xl">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Demo Stock Scanner</h1>
          <p className="text-lg text-gray-700 mb-6">View the first 10 results. Sign in to unlock full results, real-time alerts, and saved filters.</p>

          <div className="bg-white border rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left p-3">Symbol</th>
                    <th className="text-left p-3">Name</th>
                    <th className="text-right p-3">Price</th>
                    <th className="text-right p-3">Change</th>
                    <th className="text-right p-3">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {loading && (
                    <tr><td className="p-4" colSpan={5}>Loading…</td></tr>
                  )}
                  {(!loading && error) && (
                    <tr><td className="p-4 text-red-600" colSpan={5}>{error}</td></tr>
                  )}
                  {(!loading && !error) && (rows.slice(0, 10)).map((r, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td className="p-3 font-semibold text-gray-900">{r.symbol || r.ticker || '-'}</td>
                      <td className="p-3 text-gray-700">{r.name || r.company_name || '-'}</td>
                      <td className="p-3 text-right text-gray-900">{Number(r.current_price || r.price || 0).toFixed(2)}</td>
                      <td className="p-3 text-right">{Number(r.change_percent || r.price_change_today || 0).toFixed(2)}%</td>
                      <td className="p-3 text-right">{Number(r.volume || 0).toLocaleString()}</td>
                    </tr>
                  ))}
                  <tr>
                    <td colSpan={5} className="p-4 bg-gray-50 text-center">
                      Sign in to view full results, advanced filters, real-time alerts, watchlists, and portfolios.
                      <div className="mt-3 flex justify-center gap-3">
                        <Button asChild><Link to="/auth/sign-up">Create Free Account</Link></Button>
                        <Button variant="outline" asChild><Link to="/auth/sign-in">Sign In</Link></Button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DemoScanner;

