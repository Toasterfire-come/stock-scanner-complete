import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { api } from "../api/client";

export default function AdminSettings() {
  const [payPalEnabled, setPayPalEnabled] = useState(false);
  const [mode, setMode] = useState("sandbox");
  const [clientId, setClientId] = useState("");
  const [secret, setSecret] = useState("");
  const [adminPass, setAdminPass] = useState("");
  const [msg, setMsg] = useState("");
  const [publicInfo, setPublicInfo] = useState(null);

  const load = async () => {
    const { data } = await api.get("/admin/settings/public");
    setPublicInfo(data);
    setPayPalEnabled(!!data.paypal_enabled);
    setMode(data.paypal_mode || "sandbox");
  };

  useEffect(() => { load(); }, []);

  const save = async () => {
    try {
      const body = { paypal_enabled: payPalEnabled, paypal_mode: mode, paypal_client_id: clientId };
      if (secret) body.paypal_client_secret = secret;
      await api.post("/admin/settings", body, { params: { admin_password: adminPass } });
      setMsg("Saved settings");
      setSecret("");
      load();
    } catch (e) {
      setMsg(e?.response?.data?.detail || "Failed to save");
    }
  };

  const initAdmin = async () => {
    try {
      await api.post("/admin/settings/init", {}, { params: { admin_password: adminPass } });
      setMsg("Admin password initialized");
    } catch (e) {
      setMsg(e?.response?.data?.detail || "Failed to init");
    }
  };

  return (
    <Card className="max-w-2xl">
      <CardHeader><CardTitle>Admin Settings</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">Configure PayPal now or later. Secrets are stored on the server, never exposed to the browser.</div>
        <div className="grid md:grid-cols-2 gap-3">
          <div>
            <label className="text-sm">Admin password</label>
            <Input type="password" value={adminPass} onChange={(e) => setAdminPass(e.target.value)} placeholder="Set or enter admin password" />
            <div className="mt-2 flex gap-2">
              <Button size="sm" variant="outline" onClick={initAdmin}>Initialize/Update Password</Button>
            </div>
          </div>
          <div>
            <label className="text-sm">PayPal Mode</label>
            <Input value={mode} onChange={(e) => setMode(e.target.value)} placeholder="sandbox|live" />
          </div>
          <div>
            <label className="text-sm">PayPal Client ID</label>
            <Input value={clientId} onChange={(e) => setClientId(e.target.value)} placeholder="Paste sandbox client id" />
          </div>
          <div>
            <label className="text-sm">PayPal Client Secret</label>
            <Input type="password" value={secret} onChange={(e) => setSecret(e.target.value)} placeholder="Paste sandbox secret" />
          </div>
          <div className="col-span-full flex items-center justify-between">
            <div className="text-sm">Enabled: {payPalEnabled ? "Yes" : "No"}</div>
            <Button onClick={() => setPayPalEnabled((v) => !v)} variant="outline">Toggle</Button>
            <Button onClick={save}>Save</Button>
          </div>
        </div>
        {publicInfo && (
          <div className="text-xs text-muted-foreground">Public: mode={publicInfo.paypal_mode} has_client_id={publicInfo.has_client_id ? "yes" : "no"} enabled={publicInfo.paypal_enabled ? "yes" : "no"}</div>
        )}
        {msg && <div className="text-sm">{msg}</div>}
      </CardContent>
    </Card>
  );
}