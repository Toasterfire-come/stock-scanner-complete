import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { addWatchlist, deleteWatchlist, getWatchlist } from "../api/client";

export default function Watchlists() {
  const [items, setItems] = useState([]);
  const [sym, setSym] = useState("");

  const load = async () => { const d = await getWatchlist(); setItems(d.data || []); };
  useEffect(() => { load(); }, []);

  const onAdd = async () => { if (!sym) return; const res = await addWatchlist(sym); if (res?.success) { setSym(""); load(); } };
  const onDel = async (id) => { await deleteWatchlist(id); load(); };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">Watchlists
          <span className="text-sm text-muted-foreground">Total: {items.length}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2">
          <Input placeholder="Add symbol" value={sym} onChange={(e) => setSym(e.target.value.toUpperCase())} />
          <Button onClick={onAdd}>Add</Button>
        </div>
        <div className="divide-y">
          {items.map((w) => (
            <div key={w.id} className="py-2 flex items-center justify-between text-sm">
              <div className="flex items-center gap-2"><span className="font-medium">{w.symbol}</span><span className="text-muted-foreground">{w.company_name}</span></div>
              <div className="flex items-center gap-2"><span>${w.current_price}</span><Button variant="outline" size="sm" onClick={() => onDel(w.id)}>Remove</Button></div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}