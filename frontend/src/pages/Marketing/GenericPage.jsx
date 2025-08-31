import React from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";

export default function GenericPage({ title, children, subtitle }){
  return (
    <Layout>
      <PageHeader title={title} subtitle={subtitle} />
      <Section>
        <div className="prose max-w-none">
          {children || <p className="text-muted-foreground">Content coming soon. We are building something great.</p>}
        </div>
      </Section>
    </Layout>
  );
}