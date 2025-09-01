import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { api } from "../api/client";

export function SignUp() {
  const [username, setU] = useState("");
  const [email, setE] = useState("");
  const [password, setP] = useState("");
  const [msg, setMsg] = useState("");
  const submit = async (e) => { e.preventDefault(); try { const { data } = await api.post("/auth/signup/", { username, email, password }); setMsg(data.message || "Account created"); } catch (e) { setMsg(e?.response?.data?.detail || "Failed"); } };
  return (
    <Card className="max-w-md mx-auto"><CardHeader><CardTitle>Sign up</CardTitle></CardHeader><CardContent><form onSubmit={submit} className="space-y-3"><Input placeholder="Username" value={username} onChange={(e)=>setU(e.target.value)} /><Input placeholder="Email" value={email} onChange={(e)=>setE(e.target.value)} /><Input type="password" placeholder="Password" value={password} onChange={(e)=>setP(e.target.value)} /><Button className="w-full">Create account</Button></form><div className="text-sm mt-2">{msg}</div></CardContent></Card>
  );
}

export function ForgotPassword() {
  const [email, setE] = useState("");
  const [msg, setMsg] = useState("");
  const submit = async (e) => { e.preventDefault(); try { const { data } = await api.post("/auth/forgot-password/", { email }); setMsg(`Token: ${data.token} (copy to reset)`); } catch (e) { setMsg(e?.response?.data?.detail || "Failed"); } };
  return (<Card className="max-w-md mx-auto"><CardHeader><CardTitle>Forgot password</CardTitle></CardHeader><CardContent><form onSubmit={submit} className="space-y-3"><Input placeholder="Email" value={email} onChange={(e)=>setE(e.target.value)} /><Button className="w-full">Request reset</Button></form><div className="text-sm mt-2">{msg}</div></CardContent></Card>);
}

export function ResetPassword() {
  const [token, setT] = useState("");
  const [password, setP] = useState("");
  const [msg, setMsg] = useState("");
  const submit = async (e) => { e.preventDefault(); try { await api.post("/auth/reset-password/", { token, new_password: password }); setMsg("Password reset"); } catch (e) { setMsg(e?.response?.data?.detail || "Failed"); } };
  return (<Card className="max-w-md mx-auto"><CardHeader><CardTitle>Reset password</CardTitle></CardHeader><CardContent><form onSubmit={submit} className="space-y-3"><Input placeholder="Reset token" value={token} onChange={(e)=>setT(e.target.value)} /><Input type="password" placeholder="New password" value={password} onChange={(e)=>setP(e.target.value)} /><Button className="w-full">Reset</Button></form><div className="text-sm mt-2">{msg}</div></CardContent></Card>);
}

export function VerifyEmail() {
  const [token, setT] = useState("");
  const [msg, setMsg] = useState("");
  const submit = async (e) => { e.preventDefault(); try { await api.post("/auth/verify-email/", { token }); setMsg("Email verified"); } catch (e) { setMsg(e?.response?.data?.detail || "Failed"); } };
  return (<Card className="max-w-md mx-auto"><CardHeader><CardTitle>Verify email</CardTitle></CardHeader><CardContent><form onSubmit={submit} className="space-y-3"><Input placeholder="Verification token" value={token} onChange={(e)=>setT(e.target.value)} /><Button className="w-full">Verify</Button></form><div className="text-sm mt-2">{msg}</div></CardContent></Card>);
}