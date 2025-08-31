import React from "react";

export function Skeleton({ className = "" }){
  return <div className={`animate-pulse rounded-md bg-muted ${className}`} />;
}

export function TableSkeleton({ rows = 5, cols = 5 }){
  return (
    <div className="w-full">
      {[...Array(rows)].map((_, r)=>(
        <div key={r} className="grid grid-cols-12 gap-2 py-2">
          {[...Array(cols)].map((__, c)=>(<Skeleton key={c} className="h-4 col-span-2" />))}
        </div>
      ))}
    </div>
  );
}