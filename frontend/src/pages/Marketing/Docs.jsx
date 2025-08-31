import React from "react";
import GenericPage from "./GenericPage";

export default function Docs(){
  return (
    <GenericPage title="Documentation" subtitle="API and product documentation.">
      <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
        <li>REST API base: <code>/api/</code></li>
        <li>Stocks: <code>/api/stocks/</code></li>
        <li>Search: <code>/api/search/</code></li>
        <li>Trending: <code>/api/trending/</code></li>
        <li>Alerts: <code>/api/alerts/create/</code></li>
      </ul>
    </GenericPage>
  );
}