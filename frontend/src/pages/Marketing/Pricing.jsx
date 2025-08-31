import React from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";

export default function Pricing(){
  const plans = [
    {name:'Free', price:'$0', features:['Basic screener','Community templates','Email support']},
    {name:'Pro', price:'$19/mo', features:['Realtime alerts','Portfolio & watchlists','Priority support']},
    {name:'Enterprise', price:'Contact', features:['SLA','Custom integrations','Dedicated support']},
  ];
  return (
    <Layout>
      <PageHeader title="Pricing" subtitle="Simple, transparent plans." />
      <Section>
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map(p => (
            <div className="card p-6" key={p.name}>
              <h3 className="font-semibold text-lg">{p.name}</h3>
              <p className="mt-1 text-2xl" style={{fontFamily:'Poppins'}}>{p.price}</p>
              <ul className="mt-4 space-y-2 text-sm">
                {p.features.map(f => <li key={f} className="text-muted-foreground">• {f}</li>)}
              </ul>
              <button className="btn btn-primary w-full mt-6 py-2">Choose {p.name}</button>
            </div>
          ))}
        </div>
      </Section>
    </Layout>
  );
}