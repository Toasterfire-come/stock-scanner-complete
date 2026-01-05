import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function EmbedBacktest() {
  const { slug } = useParams();
  const [loading, setLoading] = useState(true);
  const [backtest, setBacktest] = useState(null);

  useEffect(() => {
    const run = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE_URL}/api/share/backtests/${encodeURIComponent(slug)}/`);
        const data = await res.json();
        if (data?.success) setBacktest(data.backtest);
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [slug]);

  const equityData = useMemo(() => {
    const curve = backtest?.equity_curve || [];
    return curve.map((v, i) => ({ day: i + 1, equity: v }));
  }, [backtest]);

  if (loading) {
    return (
      <div style={{ padding: 16, fontFamily: "system-ui, sans-serif" }}>
        Loading…
      </div>
    );
  }

  if (!backtest) {
    return (
      <div style={{ padding: 16, fontFamily: "system-ui, sans-serif" }}>
        Not found
      </div>
    );
  }

  const r = backtest.results || {};
  const grade = r.quality_grade || "N/A";

  return (
    <div className="bg-white p-3">
      <Card className="border-2">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <CardTitle className="text-base truncate">{backtest.name}</CardTitle>
              <div className="text-xs text-gray-500">
                TradeScanPro • {backtest.category?.replace(/_/g, " ")}
              </div>
            </div>
            <Badge variant="outline">{grade}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded-lg border p-2">
              <div className="text-[10px] text-gray-500">Return</div>
              <div className="text-sm font-bold">
                {r.total_return >= 0 ? "+" : ""}{Number(r.total_return || 0).toFixed(1)}%
              </div>
            </div>
            <div className="rounded-lg border p-2">
              <div className="text-[10px] text-gray-500">Sharpe</div>
              <div className="text-sm font-bold">{Number(r.sharpe_ratio || 0).toFixed(2)}</div>
            </div>
            <div className="rounded-lg border p-2">
              <div className="text-[10px] text-gray-500">Win rate</div>
              <div className="text-sm font-bold">{Number(r.win_rate || 0).toFixed(1)}%</div>
            </div>
          </div>

          <div className="h-[160px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={equityData}>
                <defs>
                  <linearGradient id="embedEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" hide />
                <YAxis hide domain={["auto", "auto"]} />
                <Tooltip />
                <Area type="monotone" dataKey="equity" stroke="#3B82F6" fill="url(#embedEquity)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="text-[10px] text-gray-500">
            Powered by TradeScanPro.com
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

