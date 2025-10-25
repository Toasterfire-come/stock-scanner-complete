import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { pingHealth } from "../api/client";

export default function Status() {
  const [data, setData] = useState(null);
  useEffect(() => { pingHealth().then(setData).catch(() => {}); }, []);
  return (
    <Card>
      <CardHeader><CardTitle>System status</CardTitle></CardHeader>
      <CardContent className="text-sm">
        {data ? (
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div><span className="text-muted-foreground">Status:</span> <b>{data.status}</b></div>
              <div><span className="text-muted-foreground">Database:</span> <b>{data.database}</b></div>
              <div><span className="text-muted-foreground">Version:</span> {data.version}</div>
              <div><span className="text-muted-foreground">Timestamp:</span> {data.timestamp}</div>
            </div>
            <div>
              <div className="font-medium mb-1">Endpoints</div>
              <ul className="list-disc pl-5">
                {Object.entries(data.endpoints || {}).map(([k, v]) => (<li key={k}><span className="text-muted-foreground">{k}</span>: {v}</li>))}
              </ul>
            </div>
          </div>
        ) : (
          <div>Loading...</div>
        )}
      </CardContent>
    </Card>
  );
}