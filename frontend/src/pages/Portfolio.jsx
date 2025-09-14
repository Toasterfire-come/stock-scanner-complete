import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { addPortfolio, deletePortfolio, getPortfolio } from "../api/client";

export default function Portfolio() {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState({});
  const [symbol, setSymbol] = useState("");
  const [shares, setShares] = useState("");
  const [avg, setAvg] = useState("");

  const load = async () => { const d = await getPortfolio(); setItems(d.data || []); setSummary(d.summary || {}); };
  useEffect(() => { load(); }, []);

  const onAdd = async () => { if (!symbol || !shares || !avg) return; await addPortfolio({ symbol, shares: Number(shares), avg_cost: Number(avg) }); setSymbol(""); setShares(""); setAvg(""); load(); };
  const onDel = async (id) => { await deletePortfolio(id); load(); };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">Add Holding</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-4 gap-3">
          <Input placeholder="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} />
          <Input type="number" placeholder="Shares" value={shares} onChange={(e) => setShares(e.target.value)} />
          <Input type="number" placeholder="Avg cost" value={avg} onChange={(e) => setAvg(e.target.value)} />
          <Button onClick={onAdd}>Save</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Portfolio</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <div className="grid md:grid-cols-4 gap-4 text-sm">
            <div><span className="text-muted-foreground">Value</span><div className="text-xl font-semibold">${summary.total_value?.toFixed?.(2) ?? 0}</div></div>
            <div><span className="text-muted-foreground">P/L</span><div className={`text-xl font-semibold ${summary.total_gain_loss > 0 ? "text-green-600" : "text-red-600"}`}>{summary.total_gain_loss?.toFixed?.(2) ?? 0}</div></div>
            <div><span className="text-muted-foreground">P/L %</span><div className="text-xl font-semibold">{summary.total_gain_loss_percent?.toFixed?.(2) ?? 0}%</div></div>
            <div><span className="text-muted-foreground">Holdings</span><div className="text-xl font-semibold">{summary.total_holdings ?? 0}</div></div>
          </div>
          <div className="divide-y mt-4">
            {items.map((h) => (
              <div key={h.id} className="py-2 flex items-center justify-between text-sm">
                <div className="flex items-center gap-3"><span className="font-medium">{h.symbol}</span><span className="text-muted-foreground">{h.shares} sh @ ${h.avg_cost}</span></div>
                <div className="flex items-center gap-3"><span>${h.total_value?.toFixed?.(2) ?? h.total_value}</span><Button variant="outline" size="sm" onClick={() => onDel(h.id)}>Remove</Button></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}