import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { useAuth } from "../context/AuthContext";

export default function SignIn() {
  const { login, loading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const res = await login(username, password);
    if (!res.ok) setError(res.error || "Login failed");
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Sign in</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div>
            <label className="text-sm">Username or email</label>
            <Input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="demo" />
          </div>
          <div>
            <label className="text-sm">Password</label>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password123" />
          </div>
          {error && <div className="text-sm text-red-600">{error}</div>}
          <Button type="submit" disabled={loading} className="w-full">Sign in</Button>
        </form>
        <p className="text-xs text-muted-foreground mt-3">Tip: demo / password123</p>
      </CardContent>
    </Card>
  );
}