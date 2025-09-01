import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export default function LegalTerms() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Terms of Service</CardTitle>
      </CardHeader>
      <CardContent className="prose prose-sm max-w-none dark:prose-invert">
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using Retail Trade Scanner ("Service"), you accept and agree to be bound by these Terms.</p>
        <h2>2. Description of Service</h2>
        <p>Retail Trade Scanner provides financial data, screening, alerts, and portfolio tools. Information is for informational purposes only, not investment advice.</p>
        <h2>3. User Account</h2>
        <ul>
          <li>Maintain confidentiality of credentials</li>
          <li>You are responsible for all activities under your account</li>
          <li>Notify us immediately of any unauthorized use</li>
        </ul>
        <h2>4. Acceptable Use</h2>
        <ul>
          <li>No unlawful use or violation of these terms</li>
          <li>No unauthorized access attempts</li>
          <li>No interference with Service or servers</li>
          <li>No reproduction or exploitation without permission</li>
        </ul>
        <h2>5. Financial Data Disclaimer</h2>
        <p>We do not guarantee accuracy, completeness, or timeliness of data. Market data may be delayed.</p>
        <h2>6. Investment Disclaimer</h2>
        <p><strong>Important:</strong> Not investment advice. Trading involves risk of loss. Do your own research.</p>
        <h2>7. Subscription and Billing</h2>
        <p>Subscriptions are billed in advance monthly or annually. Cancellation anytime. Refunds per policy.</p>
        <h2>8. API Usage Limits</h2>
        <p>Rate limits apply by plan. Exceeding limits may cause temporary suspension.</p>
        <h2>9. Limitation of Liability</h2>
        <p>No liability for indirect, incidental, special, consequential, or punitive damages.</p>
        <h2>10. Termination</h2>
        <p>We may suspend or terminate accounts for breaches.</p>
        <h2>11. Changes</h2>
        <p>We may modify these terms; continued use constitutes acceptance.</p>
        <h2>12. Contact</h2>
        <p>Email: admin@retailtradescanner.com</p>
      </CardContent>
    </Card>
  );
}