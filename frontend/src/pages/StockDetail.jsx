import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { getStock, addWatchlist } from "../api/client";

export default function StockDetail() {
  const { symbol } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => { getStock(symbol).then((d) => setData(d.data)).catch(() => {}); }, [symbol]);

  if (!data) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">{data.ticker} <span className="text-base text-muted-foreground">{data.company_name}</span></CardTitle>
        </CardHeader>
        <CardContent className="text-sm grid md:grid-cols-3 gap-4">
          <div>
            <div className="text-muted-foreground">Price</div>
            <div className="text-xl font-semibold">${data.current_price}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Market cap</div>
            <div className="text-xl font-semibold">{data.market_cap}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Change</div>
            <div className={data.change_percent > 0 ? "text-green-600" : "text-red-600"}>{data.change_percent}%</div>
          </div>
          <div className="md:col-span-3 flex items-center gap-3">
            <Button size="sm" onClick={async () => { await addWatchlist(data.ticker); }}>Add to watchlist</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}