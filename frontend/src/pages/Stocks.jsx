import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { listStocks } from "../api/client";
import { useNavigate } from "react-router-dom";

export default function Stocks() {
  const [data, setData] = useState([]);
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try { const res = await listStocks({ limit, search: query }); setData(res.data || []); } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Input placeholder="Search by ticker or company" value={query} onChange={(e) => setQuery(e.target.value)} />
        <Button onClick={load} disabled={loading}>Search</Button>
      </div>
      <Card>
        <CardHeader><CardTitle>Stocks</CardTitle></CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-2">
            {data.map((s) => (
              <div key={s.ticker} className="border rounded-md p-3 flex items-center justify-between text-sm">
                <div>
                  <div className="font-medium">{s.ticker}</div>
                  <div className="text-muted-foreground">{s.company_name}</div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">${s.current_price}</div>
                  <div className={s.change_percent > 0 ? "text-green-600" : "text-red-600"}>{s.change_percent?.toFixed?.(2)}%</div>
                  <Button size="sm" className="mt-2" onClick={() => navigate(`/app/stocks/${s.ticker}`)}>View</Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}