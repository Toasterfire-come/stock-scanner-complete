import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

function Section({ title, children, hint }) {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">{title}{hint && <span className="text-xs text-muted-foreground font-normal">{hint}</span>}</CardTitle>
      </CardHeader>
      <CardContent className="prose prose-sm max-w-none dark:prose-invert">
        {children}
      </CardContent>
    </Card>
  );
}

export function Features() {
  return (
    <Section title="Features">
      <ul>
        <li>Powerful stock screener with performance filters</li>
        <li>Alerts (price/volume) with email notifications</li>
        <li>Watchlists and portfolio tracking</li>
        <li>Market overview and trending movers</li>
        <li>REST API access for integrations</li>
      </ul>
    </Section>
  );
}

export function Product() {
  return (
    <Section title="Product overview">
      <p>Retail Trade Scanner is built for active retail traders. Research faster with scanners, monitor positions with alerting, and understand the market at a glance.</p>
    </Section>
  );
}

export function DataCoverage() {
  return (
    <Section title="Data coverage">
      <p>US equities with pricing, volume, market cap and basic fundamentals. Extended: trending, gainers/losers, and market stats. API responses are optimized for UI performance.</p>
    </Section>
  );
}

export function UseCases() {
  return (
    <Section title="Use cases">
      <ul>
        <li>Find momentum stocks pre-market</li>
        <li>Scan for value setups by PE and market cap</li>
        <li>Create alerts for breakout levels</li>
        <li>Track personalized watchlists</li>
      </ul>
    </Section>
  );
}

export function Changelog() {
  return (
    <Section title="Changelog">
      <ul>
        <li>v0.1.0: Initial launch with stocks, alerts, portfolio, revenue discounts</li>
      </ul>
    </Section>
  );
}

export function Docs() {
  return (
    <Section title="Docs" hint="API available at /docs">
      <p>Visit API docs at /docs on the backend. Frontend components and routes mirror the API contracts defined in contracts.md.</p>
    </Section>
  );
}

export function Guides() {
  return (
    <Section title="Guides">
      <ul>
        <li>Getting started with screeners</li>
        <li>Creating your first alert</li>
        <li>Managing your portfolio</li>
      </ul>
    </Section>
  );
}

export function Tutorials() {
  return (
    <Section title="Tutorials">
      <p>Step-by-step tutorials coming soon.</p>
    </Section>
  );
}

export function Glossary() {
  return (
    <Section title="Glossary">
      <ul>
        <li>Change %: Percentage price change for the session</li>
        <li>Market Cap: Total market value of a company’s outstanding shares</li>
      </ul>
    </Section>
  );
}

export function About() {
  return (
    <Section title="About">
      <p>Retail Trade Scanner is a subscription product focused on scanning, alerts and insights for traders.</p>
    </Section>
  );
}

export function Contact() {
  return (
    <Section title="Contact">
      <p>Email: admin@retailtradescanner.com</p>
    </Section>
  );
}

export function Careers() {
  return (
    <Section title="Careers">
      <p>No open roles yet. Reach out at admin@retailtradescanner.com.</p>
    </Section>
  );
}

export function Blog() {
  return (
    <Section title="Blog">
      <p>Insights and updates coming soon.</p>
    </Section>
  );
}

export function Help() {
  return (
    <Section title="Help center">
      <p>For support, contact admin@retailtradescanner.com</p>
    </Section>
  );
}

export function FAQ() {
  return (
    <Section title="FAQ">
      <ul>
        <li>Do you offer a trial? Yes, use code "trial" for $1 / 7 days, then auto-renew.</li>
      </ul>
    </Section>
  );
}

export function Community() {
  return (
    <Section title="Community">
      <p>Join the discussion with other traders. Community area coming soon.</p>
    </Section>
  );
}

export function Roadmap() {
  return (
    <Section title="Roadmap">
      <ul>
        <li>Advanced screen builder</li>
        <li>Backtesting for rules</li>
        <li>More fundamentals</li>
      </ul>
    </Section>
  );
}