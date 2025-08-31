import React from "react";

export default function SortHeader({ label, field, activeField, order, onChange }){
  const active = activeField === field;
  const nextOrder = active && order === 'asc' ? 'desc' : 'asc';
  return (
    <button type="button" className={`flex items-center gap-1 ${active ? 'text-foreground' : 'text-muted-foreground'} hover:text-foreground`} onClick={()=> onChange?.(field, nextOrder)}>
      <span>{label}</span>
      {active && <span>{order === 'asc' ? '▲' : '▼'}</span>}
    </button>
  );
}