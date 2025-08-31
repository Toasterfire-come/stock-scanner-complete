import React, { useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";

export default function Contact(){
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name:"", email:"", message:"" });
  const submit = (e)=> { e.preventDefault(); setSubmitted(true); };
  return (
    <Layout>
      <PageHeader title="Contact" subtitle="We'd love to hear from you." />
      <Section>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="card p-6">
            <form onSubmit={submit} className="space-y-4">
              <div><label className="label">Name</label><input className="input" value={form.name} onChange={(e)=> setForm({...form,name:e.target.value})} /></div>
              <div><label className="label">Email</label><input className="input" type="email" value={form.email} onChange={(e)=> setForm({...form,email:e.target.value})} /></div>
              <div><label className="label">Message</label><textarea className="input min-h-[120px]" value={form.message} onChange={(e)=> setForm({...form,message:e.target.value})} /></div>
              <button className="btn btn-primary px-4 py-2">Send message</button>
            </form>
          </div>
          <div className="card p-6">
            <h3 className="font-semibold mb-2">Support</h3>
            <p className="text-sm text-muted-foreground">Email us at support@example.com or use the form.</p>
            {submitted && <p className="mt-4 text-[hsl(var(--accent))]">Thanks! We will get back to you shortly.</p>}
          </div>
        </div>
      </Section>
    </Layout>
  );
}