import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { useAuth } from '../../context/SecureAuthContext';
import { getAdminMetrics } from '../../api/client';

export default function AdminConsole() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const isAdmin = !!user && (user.is_staff || user.isAdmin || user.role === 'admin');

  useEffect(() => {
    if (!isAdmin) { setLoading(false); return; }
    (async () => {
      try {
        const res = await getAdminMetrics();
        if (res?.success) setMetrics(res.data); else setError(res?.error || 'Failed to load metrics');
      } catch (e) { setError('Failed to load metrics'); }
      finally { setLoading(false); }
    })();
  }, [isAdmin]);

  if (!isAdmin) {
    return (
      <div className="container mx-auto px-6 py-8">
        <Alert variant="destructive"><AlertDescription>Access denied. Admins only.</AlertDescription></Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8 space-y-6">
      <Card>
        <CardHeader><CardTitle>Admin Console</CardTitle></CardHeader>
        <CardContent>
          {loading && <div>Loading metrics…</div>}
          {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
          {metrics && (
            <div className="grid gap-4 md:grid-cols-3">
              <div className="p-4 border rounded">
                <div className="text-sm text-muted-foreground">Total Users</div>
                <div className="text-2xl font-semibold">{metrics.users?.total ?? 0}</div>
              </div>
              <div className="p-4 border rounded">
                <div className="text-sm text-muted-foreground">New Users (7d)</div>
                <div className="text-2xl font-semibold">{metrics.users?.new_7d ?? 0}</div>
              </div>
              <div className="p-4 border rounded">
                <div className="text-sm text-muted-foreground">Revenue (30d)</div>
                <div className="text-2xl font-semibold">${metrics.revenue?.last_30d ?? '0.00'}</div>
              </div>
              <div className="p-4 border rounded">
                <div className="text-sm text-muted-foreground">Alerts</div>
                <div className="text-2xl font-semibold">{metrics.alerts?.active ?? 0} / {metrics.alerts?.total ?? 0}</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {metrics && (
        <Card>
          <CardHeader><CardTitle>Plan Breakdown</CardTitle></CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {(metrics.plans || []).map((row, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 border rounded">
                  <div className="capitalize">{row.plan_type || 'unknown'}</div>
                  <div className="font-mono">{row.count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {metrics && (
        <Card>
          <CardHeader><CardTitle>Signups (last 8 days)</CardTitle></CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-3">
              {(metrics.signups || []).map((d) => (
                <div key={d.date} className="p-3 border rounded">
                  <div className="text-xs text-muted-foreground">{d.date}</div>
                  <div className="text-xl font-semibold">{d.count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
