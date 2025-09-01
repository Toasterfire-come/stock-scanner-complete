import React, { useEffect, useState } from 'react';
import { getEndpointStatus } from '../../lib/api';
import { CheckCircle2, XCircle, Timer, RefreshCw } from 'lucide-react';

export default function EndpointStatus() {
  const [state, setState] = useState({ loading: true, error: '', data: null });

  const load = async () => {
    setState(s => ({ ...s, loading: true, error: '' }));
    const res = await getEndpointStatus();
    if (!res.ok) setState({ loading: false, error: res.error || 'Failed to load', data: null });
    else setState({ loading: false, error: '', data: res.data?.data || res.data });
  };

  useEffect(() => { load(); }, []);

  const list = state.data?.endpoints || [];
  const summary = {
    total: state.data?.total_tested ?? list.length,
    success: state.data?.successful ?? list.filter(e => e.status === 'success').length,
    failed: state.data?.failed ?? list.filter(e => e.status !== 'success').length,
  };

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">API Endpoint Status</h1>
        <button onClick={load} className="inline-flex items-center gap-2 px-3 py-2 rounded-md border hover:bg-accent">
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {state.loading && (
        <div className="space-y-2">
          <div className="h-10 w-64 bg-muted animate-pulse rounded" />
          <div className="h-20 w-full bg-muted animate-pulse rounded" />
          <div className="h-20 w-full bg-muted animate-pulse rounded" />
        </div>
      )}

      {state.error && (
        <div className="p-4 border rounded bg-destructive/10 text-destructive">
          Failed to load endpoint status: {state.error}
        </div>
      )}

      {!state.loading && !state.error && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Stat label="Total" value={summary.total} />
            <Stat label="Success" value={summary.success} positive />
            <Stat label="Failed" value={summary.failed} negative />
          </div>

          <div className="overflow-x-auto border rounded">
            <table className="min-w-full text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">URL</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">Code</th>
                  <th className="text-left p-2">Response Time (ms)</th>
                </tr>
              </thead>
              <tbody>
                {list.map((e, idx) => (
                  <tr key={idx} className="border-t">
                    <td className="p-2 whitespace-nowrap">{e.name}</td>
                    <td className="p-2 text-muted-foreground max-w-[420px] truncate" title={e.url}>{e.url}</td>
                    <td className="p-2">{e.status === 'success' ? (
                      <span className="inline-flex items-center gap-1 text-emerald-600"><CheckCircle2 className="h-4 w-4" /> OK</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-red-600"><XCircle className="h-4 w-4" /> Error</span>
                    )}</td>
                    <td className="p-2">{e.status_code ?? '-'}</td>
                    <td className="p-2">{e.response_time ?? '-'}</td>
                  </tr>
                ))}
                {!list.length && (
                  <tr>
                    <td className="p-4 text-center text-muted-foreground" colSpan={5}>No endpoints reported</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, positive, negative }) {
  return (
    <div className="p-4 border rounded">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-2xl font-semibold flex items-center gap-2">
        {positive && <CheckCircle2 className="h-5 w-5 text-emerald-600" />}
        {negative && <XCircle className="h-5 w-5 text-red-600" />}
        {!positive && !negative && <Timer className="h-5 w-5 text-muted-foreground" />}
        <span>{value}</span>
      </div>
    </div>
  );
}