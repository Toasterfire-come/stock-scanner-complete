import React from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";

export default function Features(){
  return (
    <Layout>
      <PageHeader title="Features" subtitle="Everything you need to research markets and act with confidence." />
      <Section>
        <div className="grid md:grid-cols-2 gap-6">
          {[
            {h:'Advanced Scanner', d:'Build complex queries with price, volume, valuation and momentum filters.'},
            {h:'Alerts', d:'Price crosses, percent moves, volume spikes and more delivered via email.'},
            {h:'Watchlists', d:'Organize symbols with notes and targets.'},
            {h:'Portfolio', d:'Track cost basis, P/L and exposure.'},
          ].map(f => (
            <div key={f.h} className="card p-6">
              <h3 className="font-semibold text-lg mb-2">{f.h}</h3>
              <p className="text-sm text-muted-foreground">{f.d}</p>
            </div>
          ))}
        </div>
      </Section>
    </Layout>
  );
}