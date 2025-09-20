import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Link } from "react-router-dom";

const Section = ({ title, children }) => (
  <Card className="mb-6">
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent className="prose prose-sm max-w-none dark:prose-invert">
      {children}
    </CardContent>
  </Card>
);

export default function Documentation() {
  return (
    <div className="container-enhanced py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Platform Documentation</h1>

      <Section title="Overview">
        <p>Trade Scan Pro provides a unified stock research experience with scanning (screeners), portfolio tracking, alerts, and a clean market overview. This document explains all features, configuration options, billing, and policies.</p>
      </Section>

      <Section title="Screeners (Filters)">
        <ul>
          <li>Build filters using criteria: Price, Volume, Market Cap, P/E Ratio, Dividend Yield, Change %, Exchange.</li>
          <li>Test Run: runs your criteria against all stocks and shows matches.</li>
          <li>Save: stores your screener (name, description, criteria) for later use.</li>
          <li>Results: view matching stocks; export CSV for offline analysis. Import/Export criteria as JSON from Create/Edit pages.</li>
        </ul>
        <p className="mt-2 text-sm text-gray-600">JSON schema for import:</p>
        <pre className="text-xs overflow-x-auto p-3 bg-gray-50 border rounded">
{`{
  "name": "High Dividend Value Stocks",
  "description": "Large cap, value screen",
  "isPublic": false,
  "criteria": [
    { "id": "market_cap", "min": 5000000000, "max": 1000000000000 },
    { "id": "price", "min": 5, "max": 200 },
    { "id": "pe_ratio", "max": 20 },
    { "id": "dividend_yield", "min": 2 },
    { "id": "exchange", "value": "NYSE" }
  ]
}`}
        </pre>
        <p>Endpoints:</p>
        <ul>
          <li>GET/POST <code>/api/filter/</code> – execute a filter (JSON criteria supported via POST).</li>
          <li>GET <code>/api/screeners/</code> – list saved screeners (public + yours).</li>
          <li>POST <code>/api/screeners/create/</code> – save a screener.</li>
          <li>GET <code>/api/screeners/&lt;id&gt;/</code> – fetch a screener.</li>
          <li>POST <code>/api/screeners/&lt;id&gt;/update/</code> – update a screener.</li>
          <li>DELETE <code>/api/screeners/&lt;id&gt;/</code> – delete a screener.</li>
          <li>GET/POST <code>/api/screeners/&lt;id&gt;/results/</code> – run and return results.</li>
          <li>GET <code>/api/screeners/&lt;id&gt;/export.csv</code> – download results as CSV.</li>
        </ul>
      </Section>

      <Section title="Alerts">
        <ul>
          <li>Create price alerts: above/below a target price. Toggle active status and delete alerts.</li>
          <li>Endpoints: <code>/api/alerts/</code>, <code>/api/alerts/create/</code>, <code>/api/alerts/&lt;id&gt;/toggle/</code>, <code>/api/alerts/&lt;id&gt;/delete/</code>.</li>
        </ul>
      </Section>

      <Section title="Portfolio">
        <ul>
          <li>Track holdings, value, P&L, return %, and counts.</li>
          <li>Endpoints: <code>/api/portfolio/</code>, <code>/api/portfolio/add/</code>, <code>/api/portfolio/&lt;id&gt;/</code> (DELETE), plus <code>/api/portfolio/value/</code>, <code>/api/portfolio/pnl/</code>, <code>/api/portfolio/return/</code>, <code>/api/portfolio/holdings-count/</code>.</li>
        </ul>
      </Section>

      <Section title="Market Overview">
        <ul>
          <li>Trending (gainers/losers/most active) and stats.</li>
          <li>Endpoints: <code>/api/trending/</code>, <code>/api/market-stats/</code>, <code>/api/statistics/</code>.</li>
        </ul>
      </Section>

      <Section title="Authentication & Account">
        <ul>
          <li>CSRF: <code>/api/auth/csrf/</code>. Login: <code>/api/auth/login/</code>. Logout: <code>/api/auth/logout/</code>. Profile: <code>/api/user/profile/</code>. Change Password: <code>/api/user/change-password/</code>.</li>
        </ul>
      </Section>

      <Section title="Billing">
        <ul>
          <li>Plan: <code>/api/billing/current-plan/</code>, Change Plan: <code>/api/billing/change-plan/</code>, Billing History: <code>/api/billing/history/</code>, Download Invoice: <code>/api/billing/download/&lt;invoice_id&gt;/</code>, Cancel: <code>/api/billing/cancel</code>.</li>
          <li>Discounts & PayPal: validate/apply at <code>/revenue/*</code>, create/capture PayPal order at <code>/api/billing/*paypal*</code>.</li>
        </ul>
      </Section>

      <Section title="Settings & Notifications">
        <ul>
          <li>Notification settings: <code>/api/user/notification-settings/</code>, history/mark read under <code>/api/notifications/*</code>.</li>
          <li>Usage: <code>/api/usage/</code>, <code>/api/usage-stats/</code>, <code>/api/usage/history/</code>.</li>
        </ul>
      </Section>

      <Section title="Policies & Terms">
        <ul>
          <li><Link to="/legal/privacy" className="text-blue-600">Privacy Policy</Link></li>
          <li><Link to="/legal/terms" className="text-blue-600">Terms of Service</Link></li>
        </ul>
      </Section>

      <Section title="Support">
        <p>For help, visit the Help Center or contact support via the Contact page. See System Status at <Link to="/endpoint-status" className="text-blue-600">Endpoint Status</Link>.</p>
      </Section>
    </div>
  );
}