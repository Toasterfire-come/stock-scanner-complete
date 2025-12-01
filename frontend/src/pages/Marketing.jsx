import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  marketingMetrics,
  formatNumber,
  formatPercent,
  timeframeCopy,
} from "../data/marketingMetrics";

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

const { usage, outcomes, reliability, enterprise, testimonials } = marketingMetrics;

export function Features() {
  return (
    <Section title="Features">
      <ul>
        <li>{`${formatNumber(usage.totalScreenersRunMonthly)}+ screeners run monthly across ${formatNumber(usage.teamsOnPlatform)} teams`}</li>
        <li>{`${formatNumber(usage.alertsDeliveredMonthly)} real-time alerts delivered with sub-${reliability.apiP95LatencyMs}ms latency`}</li>
        <li>{`${formatNumber(usage.watchlistsSyncedMonthly)} watchlists synced with ${formatPercent(outcomes.averageDrawdownReductionPercent)} average drawdown reduction`}</li>
        <li>{`${formatPercent(marketingMetrics.testimonials.retentionPercent90Day)} 90-day retention by combining screeners, alerts, and analytics workflows`}</li>
        <li>{`REST + WebSocket APIs sustaining ${enterprise.apiThroughputDailyMillions}M+ calls/day`}</li>
      </ul>
    </Section>
  );
}

export function Product() {
  return (
    <Section title="Product overview">
      <p>{`Trade Scan Pro is built for active traders and research teams. During ${timeframeCopy()}, ${formatNumber(usage.activeAccounts)} accounts executed ${formatNumber(usage.totalScreenersRunMonthly)}+ screeners per month while keeping time-to-first-screener under ${usage.medianTimeToFirstScreenerMinutes} minutes.`}</p>
    </Section>
  );
}

export function DataCoverage() {
  return (
    <Section title="Data coverage">
      <p>{`${formatNumber(usage.coverageUniverse)}+ equities across ${usage.coverageVenues.join(", ")} with live pricing, depth, market cap, and sentiment. Extended coverage streams ${formatNumber(enterprise.apiThroughputDailyMillions)}M+ API calls/day with ${reliability.apiP50LatencyMs}ms median latency.`}</p>
    </Section>
  );
}

export function UseCases() {
  return (
    <Section title="Use cases">
      <ul>
        <li>{`Identify momentum setups pre-market using screeners that trigger ${formatNumber(usage.alertsDeliveredMonthly)} alerts each month`}</li>
        <li>{`Spot value opportunities with fundamentals that improved portfolios by ${formatPercent(outcomes.averagePortfolioLiftPercent)}`}</li>
        <li>{`Automate breakout alerts that contribute to ${formatPercent(outcomes.averageDrawdownReductionPercent)} drawdown reduction`}</li>
        <li>{`Maintain personalized watchlists syncing ${formatNumber(usage.watchlistsSyncedMonthly)} lists per month`}</li>
      </ul>
    </Section>
  );
}

export function Changelog() {
  return (
    <Section title="Changelog">
      <ul>
        <li>{`${timeframeCopy()}: Expanded coverage to ${formatNumber(usage.coverageUniverse)}+ equities and ${formatNumber(usage.totalScreenersRunMonthly)}+ monthly screening runs`}</li>
        <li>{`${timeframeCopy("Q3 cohort")}: Improved trial-to-paid conversion to ${formatPercent(outcomes.trialToPaidConversionPercent)}`}</li>
      </ul>
    </Section>
  );
}

export function Docs() {
  return (
    <Section title="Docs" hint="API available at /docs">
      <p>{`Visit /docs for REST and WebSocket references. The stack currently handles ${enterprise.apiThroughputDailyMillions}M+ calls/day with ${reliability.apiP50LatencyMs}ms median latency and ${formatPercent(reliability.uptimePercent, 2)} uptime.`}</p>
    </Section>
  );
}

export function Guides() {
  return (
    <Section title="Guides">
      <ul>
        <li>{`Getting started with screeners (median time to first insight: ${usage.medianTimeToFirstScreenerMinutes} minutes)`}</li>
        <li>{`Creating your first alert (supports ${formatNumber(usage.alertsDeliveredMonthly)} monthly notifications)`}</li>
        <li>{`Managing your portfolio (teams report ${formatPercent(outcomes.averagePortfolioLiftPercent)} portfolio lift)`}</li>
      </ul>
    </Section>
  );
}

export function Tutorials() {
  return (
    <Section title="Tutorials">
      <p>{`Step-by-step tutorials launching ${timeframeCopy("Q4")} covering high-converting workflows responsible for ${formatPercent(outcomes.trialToPaidConversionPercent)} trial-to-paid conversion.`}</p>
    </Section>
  );
}

export function Glossary() {
  return (
    <Section title="Glossary">
      <ul>
        <li>{`Change %: Percentage move tracked across ${formatNumber(usage.coverageUniverse)}+ listed equities each session`}</li>
        <li>{`Market Cap: Total market value of outstanding shares, refreshed every ${marketingMetrics.reliability.dataFreshnessSeconds}s`}</li>
      </ul>
    </Section>
  );
}

export function About() {
  return (
    <Section title="About">
      <p>{`Trade Scan Pro is a subscription platform focused on scanning, alerts, and insights. ${formatNumber(usage.activeAccounts)} active accounts report ${formatPercent(outcomes.averagePortfolioLiftPercent)} average portfolio lift and ${formatPercent(marketingMetrics.testimonials.retentionPercent90Day)} retention.`}</p>
    </Section>
  );
}

export function Contact() {
  return (
    <Section title="Contact">
      <p>{`Email: growth@tradescanpro.com · Median first response ${reliability.supportFirstResponseMinutes} minutes`}</p>
    </Section>
  );
}

export function Careers() {
  return (
    <Section title="Careers">
      <p>{`No open roles today. We review pipeline needs quarterly based on ${formatPercent(outcomes.trialToPaidConversionPercent)} conversion and ${formatNumber(enterprise.enterpriseClients)} enterprise accounts. Introduce yourself at growth@tradescanpro.com.`}</p>
    </Section>
  );
}

export function Blog() {
  return (
    <Section title="Blog">
      <p>{`Insights and updates covering ${formatPercent(outcomes.averagePortfolioLiftPercent)} average portfolio lift stories are releasing throughout ${timeframeCopy("Q4")}.`}</p>
    </Section>
  );
}

export function Help() {
  return (
    <Section title="Help center">
      <p>{`Support: support@tradescanpro.com · ${reliability.supportFirstResponseMinutes} min median first reply · ${formatPercent(reliability.uptimePercent, 2)} platform uptime.`}</p>
    </Section>
  );
}

export function FAQ() {
  return (
    <Section title="FAQ">
      <ul>
        <li>{`Do you offer a trial? Yes — free until the next 1st of the month. ${formatPercent(outcomes.trialToPaidConversionPercent)} of trials convert after activating alerts.`}</li>
        <li>{`What retention can we expect? ${formatPercent(marketingMetrics.testimonials.retentionPercent90Day)} of customers stay active through day 90.`}</li>
      </ul>
    </Section>
  );
}

export function Community() {
  return (
    <Section title="Community">
      <p>{`Join ${formatNumber(usage.teamsOnPlatform)} teams sharing workflows, case studies, and ${formatNumber(testimonials.verifiedCaseStudies)} verified success stories.`}</p>
    </Section>
  );
}

export function Roadmap() {
  return (
    <Section title="Roadmap">
      <ul>
        <li>{`Advanced screen builder (targeting ${formatPercent(outcomes.trialToPaidConversionPercent)}+ trial conversion)`}</li>
        <li>{`Backtesting for rules with ${formatPercent(outcomes.averagePortfolioLiftPercent)} projected lift benchmarks`}</li>
        <li>{`Expanded fundamentals covering ${formatNumber(usage.coverageUniverse + 500)}+ tickers`}</li>
      </ul>
    </Section>
  );
}