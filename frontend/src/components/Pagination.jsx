import React from "react";

export default function Pagination({ page, pageSize, total = 0, onChange }){
  const totalPages = Math.max(1, Math.ceil((total || 0) / Math.max(1, pageSize || 1)));
  const canPrev = page > 1; const canNext = page < totalPages;
  return (
    <div className="flex items-center justify-between text-sm mt-4">
      <div className="text-muted-foreground">Page {page} of {totalPages} • Total {total ?? 0}</div>
      <div className="flex items-center gap-2">
        <button className="btn btn-outline px-3 py-1" disabled={!canPrev} onClick={()=> onChange?.(page - 1)}>Prev</button>
        <button className="btn btn-outline px-3 py-1" disabled={!canNext} onClick={()=> onChange?.(page + 1)}>Next</button>
      </div>
    </div>
  );
}