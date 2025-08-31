import React from "react";

export default function AlertBanner({ type = 'info', title, message, onClose }){
  const palette = {
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-700 border-red-200',
    info: 'bg-[hsl(var(--muted))] text-foreground border-border',
  };
  return (
    <div className={`rounded-lg border p-3 ${palette[type]}`}> 
      <div className="flex items-start justify-between gap-4">
        <div>
          {title && <div className="font-medium">{title}</div>}
          {message && <div className="text-sm opacity-90">{message}</div>}
        </div>
        {onClose && (
          <button className="text-sm underline" onClick={onClose}>Dismiss</button>
        )}
      </div>
    </div>
  );
}