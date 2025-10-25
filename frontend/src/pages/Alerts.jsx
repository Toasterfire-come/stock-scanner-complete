import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { alertsMeta, createAlert } from "../api/client";

export default function Alerts() {
  const [ticker, setTicker] = useState("");
  const [price, setPrice] = useState("");
  const [condition, setCondition] = useState("above");
  const [email, setEmail] = useState("");
  const [result, setResult] = useState(null);

  const onCreate = async () => {
    try {
      const res = await createAlert({ ticker, target_price: Number(price), condition, email });
      setResult(res);
    } catch (e) {
      setResult({ message: e?.response?.data || "Failed" });
    }
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>Create price alert</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm">Ticker</label>
            <Input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="AAPL" />
          </div>
          <div>
            <label className="text-sm">Target price</label>
            <Input type="number" value={price} onChange={(e) => setPrice(e.target.value)} placeholder="200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm">Condition</label>
            <Input value={condition} onChange={(e) => setCondition(e.target.value)} placeholder="above|below" />
          </div>
          <div>
            <label className="text-sm">Email</label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          </div>
        </div>
        <Button onClick={onCreate}>Create alert</Button>
        {result && <div className="text-sm text-muted-foreground">{result.message} #{result.alert_id}</div>}
      </CardContent>
    </Card>
  );
}