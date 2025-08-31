import React from "react";

export default function PageHeader({ title, subtitle, cta }) {
  return (
    <section className="section border-b border-border bg-white">
      <div className="container-page flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight" style={{fontFamily:'Poppins'}}> {title} </h1>
          {subtitle && <p className="text-muted-foreground mt-2 max-w-2xl">{subtitle}</p>}
        </div>
        {cta && <div className="mt-4 md:mt-0">{cta}</div>}
      </div>
    </section>
  );
}