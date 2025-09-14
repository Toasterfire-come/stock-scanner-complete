import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { api } from "../api/client";

export default function Notifications() {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState({ total_unread: 0 });

  const load = async () => {
    try {
      const { data } = await api.get("/notifications/history/");
      setItems(data.data || []);
      setSummary(data.summary || { total_unread: 0 });
    } catch {}
  };

  useEffect(() => { load(); }, []);

  const markAll = async () => {
    await api.post("/notifications/mark-read/", { mark_all: true });
    load();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">Notifications <span className="text-sm text-muted-foreground">Unread: {summary.total_unread}</span></CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button size="sm" onClick={markAll}>Mark all read</Button>
        <div className="divide-y">
          {items.map((n) => (
            <div key={n.id} className="py-2 text-sm flex items-center justify-between">
              <div>
                <div className="font-medium">{n.title}</div>
                <div className="text-muted-foreground">{n.message}</div>
              </div>
              {!n.is_read && <span className="text-xs text-amber-600">new</span>}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}