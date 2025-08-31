import React from "react";
import Layout from "../components/Layout";
import PageHeader from "../components/PageHeader";
import Section from "../components/Section";

export default function DesignSystem(){
  const tokens = [
    { name: 'Background', var: '--background' },
    { name: 'Foreground', var: '--foreground' },
    { name: 'Primary (Onyx)', var: '--primary' },
    { name: 'Accent (Coral)', var: '--accent' },
    { name: 'Secondary (Blue)', var: '--secondary' },
    { name: 'Muted / Tints', var: '--muted' },
    { name: 'Border', var: '--border' },
  ];
  return (
    <Layout>
      <PageHeader title="Design System" subtitle="Tokens and components used across the app." />
      <Section>
        <div className="grid md:grid-cols-3 gap-6">
          {tokens.map(t => (
            <div className="card p-4" key={t.var}>
              <div className="flex items-center justify-between mb-3">
                <div className="font-medium">{t.name}</div>
                <code className="text-xs">{t.var}</code>
              </div>
              <div className="h-16 rounded-lg border" style={{backgroundColor:`hsl(var(${t.var}))`}} />
            </div>
          ))}
        </div>
        <div className="mt-12 grid md:grid-cols-2 gap-6">
          <div className="card p-6 space-y-3">
            <div className="font-semibold">Buttons</div>
            <div className="flex gap-3 items-center">
              <button className="btn btn-primary px-4 py-2">Primary</button>
              <button className="btn btn-secondary px-4 py-2">Secondary</button>
              <button className="btn btn-outline px-4 py-2">Outline</button>
            </div>
          </div>
          <div className="card p-6 space-y-3">
            <div className="font-semibold">Inputs</div>
            <div className="grid grid-cols-2 gap-3">
              <input className="input" placeholder="Text" />
              <input className="input" placeholder="Number" type="number" />
              <select className="input"><option>Option</option></select>
              <input className="input" placeholder="With ring focus" />
            </div>
          </div>
        </div>
      </Section>
    </Layout>
  );
}