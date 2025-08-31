import React, { useEffect, useState } from "react";
import GenericPage from "./GenericPage";
import { getHealth } from "../../lib/api";

export default function Status(){
  const [data, setData] = useState(null);
  useEffect(()=>{ getHealth().then(r=> setData(r.data)).catch(()=> setData({status:'degraded'})); },[]);
  return (
    <GenericPage title="System Status" subtitle="Live service status and API health.">
      {!data ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card p-6">
            <div className="text-sm text-muted-foreground">Overall</div>
            <div className="mt-1 text-2xl font-semibold">{data.status}</div>
            <div className="mt-2 text-sm">Database: <span className="font-medium">{data.database}</span></div>
            <div className="mt-2 text-sm">Version: <span className="font-medium">{data.version}</span></div>
          </div>
          <div className="card p-6">
            <div className="text-sm text-muted-foreground mb-2">Endpoints</div>
            <ul className="text-sm divide-y">
              {data.endpoints && Object.entries(data.endpoints).map(([k,v]) => (
                <li key={k} className="py-2 flex items-center justify-between"><span className="capitalize">{k.replaceAll('_',' ')}</span><span className="text-muted-foreground">{v}</span></li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </GenericPage>
  );
}