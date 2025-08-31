import React, { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../lib/api";

export default function AutosuggestSearch({ value, onChange, onSelect }){
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const boxRef = useRef(null);

  const q = value?.trim?.() || "";
  const debounceMs = 250;

  const search = useMemo(()=>{
    let t; return (query)=>{ clearTimeout(t); t = setTimeout(async ()=>{
      if (!query) { setItems([]); setOpen(false); return; }
      setLoading(true);
      try { const r = await api.get(`/search/`, { params: { q: query } }); setItems(r.data?.results || []); setOpen(true); }
      catch { setItems([]); setOpen(false); }
      finally { setLoading(false); }
    }, debounceMs); };
  },[]);

  useEffect(()=>{ search(q); }, [q]);

  useEffect(()=>{
    const handler = (e)=>{ if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false); };
    document.addEventListener('click', handler); return ()=> document.removeEventListener('click', handler);
  },[]);

  return (
    <div className="relative" ref={boxRef}>
      <input className="input" placeholder="Search (ticker or company)" value={value} onChange={(e)=> onChange?.(e.target.value)} onFocus={()=> q && setOpen(true)} />
      {open && (
        <div className="absolute z-20 mt-1 w-full rounded-lg border border-border bg-white dark:bg-[hsl(var(--background))] shadow">
          {loading ? (
            <div className="p-3 text-sm text-muted-foreground">Searching…</div>
          ) : items.length === 0 ? (
            <div className="p-3 text-sm text-muted-foreground">No matches</div>
          ) : (
            <ul className="max-h-72 overflow-auto">
              {items.map((it)=> (
                <li key={`${it.ticker}-${it.match_type}`}>
                  <button type="button" onClick={()=> { onSelect?.(it); setOpen(false); }} className="w-full text-left px-3 py-2 hover:bg-muted">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{it.ticker} <span className="text-muted-foreground font-normal">{it.company_name}</span></div>
                      <div className={`text-xs ${it.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>{it.change_percent?.toFixed?.(2)}%</div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}