import React from "react";

export default function Badge({ children, color = 'accent' }){
  const styles = {
    accent: 'bg-[hsl(var(--accent))]/10 text-[hsl(var(--accent))] border-[hsl(var(--accent))]/20',
    blue: 'bg-[hsl(var(--secondary))]/10 text-[hsl(var(--secondary))] border-[hsl(var(--secondary))]/20',
    neutral: 'bg-muted text-foreground border-border',
    green: 'bg-green-50 text-green-700 border-green-200',
    red: 'bg-red-50 text-red-700 border-red-200',
  };
  return <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs ${styles[color]}`}>{children}</span>;
}