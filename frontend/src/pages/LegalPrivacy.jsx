import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export default function LegalPrivacy() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Privacy Policy</CardTitle>
      </CardHeader>
      <CardContent className="prose prose-sm max-w-none dark:prose-invert">
        <p><strong>Our Commitment:</strong> We protect your privacy and secure your information.</p>
        <h2>1. Information We Collect</h2>
        <ul>
          <li>Account: name, email, encrypted password, optional phone/company</li>
          <li>Usage: API requests, features used, device/browser, IP/location</li>
        </ul>
        <h2>2. How We Use Information</h2>
        <ul>
          <li>Provide and maintain the Service</li>
          <li>Process payments and subscriptions</li>
          <li>Send service notifications</li>
          <li>Support and improve the Service</li>
          <li>Legal compliance</li>
        </ul>
        <h2>3. Security</h2>
        <ul>
          <li>Encryption in transit and at rest</li>
          <li>Access controls and audits</li>
          <li>SOC 2 aligned practices</li>
        </ul>
        <h2>4. Sharing</h2>
        <p>No selling of personal data. Shared only with consent, legal requirements, protection of rights, or trusted processors.</p>
        <h2>5. Cookies</h2>
        <p>Used for login, analytics, personalization. Manage via browser settings.</p>
        <h2>6. Your Rights</h2>
        <ul>
          <li>Access, correct, delete, export data; opt-out of marketing</li>
        </ul>
        <h2>7. Retention</h2>
        <p>Data retained as needed; deleted within 30 days after account deletion unless legally required.</p>
        <h2>8. International Transfers</h2>
        <p>Safeguards applied for cross-border processing.</p>
        <h2>9. Children</h2>
        <p>Not for under 18. Contact us if data was submitted by a minor.</p>
        <h2>10. Changes</h2>
        <p>We update this policy and post effective date changes.</p>
        <h2>11. Contact</h2>
        <p>Email: admin@retailtradescanner.com</p>
      </CardContent>
    </Card>
  );
}