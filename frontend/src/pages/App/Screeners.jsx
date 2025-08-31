import React from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";

export default function Screeners(){
  return (
    <Layout>
      <PageHeader title="Stock Scanner" subtitle="Filter and search stocks with advanced criteria." />
      <Section>
        <div className="card p-6">
          <p className="text-sm text-muted-foreground">This screen is ready for backend filter wiring. The theme styles inputs, selects, tables and cards consistently across the app.</p>
          <div className="grid md:grid-cols-3 gap-4 mt-6">
            <input className="input" placeholder="Search (ticker or company)" />
            <select className="input"><option>Any Category</option></select>
            <select className="input"><option>Any Exchange</option></select>
            <input className="input" placeholder="Min Price" />
            <input className="input" placeholder="Max Price" />
            <input className="input" placeholder="Min Volume" />
            <button className="btn btn-primary py-2">Run</button>
          </div>
        </div>
      </Section>
    </Layout>
  );
}