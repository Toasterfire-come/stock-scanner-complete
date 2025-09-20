import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LegalPage = ({ type }) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    const endpoint = type === 'privacy' ? `${BACKEND_URL}/api/legal/privacy` : `${BACKEND_URL}/api/legal/terms`;
    axios.get(endpoint)
      .then(r => setData(r.data))
      .catch(e => setError(e?.response?.data?.error || e.message || 'Failed to load'));
  }, [type]);
  if (error) return <div className="p-6 max-w-3xl mx-auto"><p className="text-red-600">{error}</p></div>;
  if (!data) return <div className="p-6 max-w-3xl mx-auto"><p>Loading…</p></div>;
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">{data.title}</h1>
      {data.intro && <p className="text-sm text-gray-600 mb-4">{data.intro}</p>}
      {Array.isArray(data.sections) && data.sections.map((s, idx) => (
        <div key={idx} className="mt-4">
          {s.heading && <h2 className="text-xl font-semibold">{s.heading}</h2>}
          {s.body && <p className="mt-1">{s.body}</p>}
          {Array.isArray(s.list) && (
            <ul className="list-disc ml-6 mt-2">
              {s.list.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          )}
        </div>
      ))}
      {data.last_updated && <p className="text-xs text-gray-500 mt-4">Last updated: {data.last_updated}</p>}
    </div>
  );
};

const Account = () => {
  const [plan, setPlan] = useState(null);
  const [autoRenew, setAutoRenew] = useState(null);
  const [usage, setUsage] = useState(null);
  const [refSum, setRefSum] = useState(null);
  const [loading, setLoading] = useState(true);
  const userId = useMemo(() => window.localStorage.getItem('rts_user_id') || '', []);
  useEffect(() => {
    const load = async () => {
      try {
        const [p, u, r] = await Promise.all([
          axios.get(`${API}/billing/current-plan/`, { withCredentials: true }).then(r=>r.data),
          axios.get(`${API}/usage/`, { withCredentials: true }).then(r=>r.data),
          axios.get(`${API}/referrals/summary`, { params: { user_id: userId }}).then(r=>r.data),
        ]);
        setPlan(p?.data || {});
        setAutoRenew(!!p?.data?.auto_renew);
        setUsage(u?.data || {});
        setRefSum(r || {});
      } catch (e) {}
      setLoading(false);
    };
    load();
  }, [userId]);
  const onToggle = async () => {
    try {
      const r = await axios.post(`${API}/billing/auto-renew/`, { auto_renew: !autoRenew }, { withCredentials: true });
      setAutoRenew(!!r.data.auto_renew);
    } catch (e) { alert('Failed to update'); }
  };
  if (loading) return <div className="p-6">Loading…</div>;
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Account</h1>
      <div className="border rounded p-4">
        <h2 className="text-lg font-semibold">Plan</h2>
        <p className="text-sm text-gray-600">{plan?.plan_name} · Billing: {plan?.billing_cycle}</p>
        <p className="text-sm">Next billing date: {plan?.next_billing_date || '—'}</p>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-sm">Auto renew:</span>
          <button className="px-3 py-1 border rounded" onClick={onToggle}>{autoRenew ? 'On' : 'Off'}</button>
        </div>
      </div>
      <div className="border rounded p-4 mt-4">
        <h2 className="text-lg font-semibold">Usage</h2>
        <p className="text-sm">Monthly API calls: {usage?.monthly?.api_calls ?? 0} / {usage?.monthly?.limit ?? 0}</p>
      </div>
      <div className="border rounded p-4 mt-4">
        <h2 className="text-lg font-semibold">Referrals</h2>
        <p className="text-sm">Invited: {refSum?.total_invited ?? 0} · Paid: {refSum?.total_paid ?? 0} · Pending free months: {refSum?.pending_rewards_months ?? 0}</p>
      </div>
    </div>
  );
};

const Home = () => {
  const [health, setHealth] = useState(null);
  const [breakouts, setBreakouts] = useState([]);
  const [undervalued, setUndervalued] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [referral, setReferral] = useState({ link: null, code: null, summary: null });
  const [inviteEmail, setInviteEmail] = useState("");
  const [keys, setKeys] = useState([]);
  const [newKeyName, setNewKeyName] = useState('');
  const userId = useMemo(() => {
    // Placeholder for real auth user id integration
    const stored = window.localStorage.getItem("rts_user_id");
    if (stored) return stored;
    const gen = crypto.randomUUID();
    window.localStorage.setItem("rts_user_id", gen);
    return gen;
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        const [h, b, u, link, sum] = await Promise.all([
          axios.get(`${API}/health/`).then(r => r.data),
          axios.get(`${API}/stocks/top-gainers/`, { params: { limit: 5 } }).then(r => r.data),
          axios.get(`${API}/filter/`, { params: { max_pe: 15, min_market_cap: 1000000000, limit: 5 } }).then(r => r.data),
          axios.get(`${API}/referrals/link`, { params: { user_id: userId } }).then(r => r.data),
          axios.get(`${API}/referrals/summary`, { params: { user_id: userId } }).then(r => r.data),
        ]);
        setHealth(h);
        setBreakouts((b && (b.data || b.stocks)) || []);
        setUndervalued((u && (u.stocks || u.data)) || []);
        setReferral({ link: link.referral_link, code: link.referral_code, summary: sum });
      } catch (e) {
        setError(e?.response?.data?.detail || e.message || "Failed to load data");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [userId]);

  const onInvite = async (e) => {
    e.preventDefault();
    if (!inviteEmail) return;
    try {
      await axios.post(`${API}/referrals/invite`, { inviter_id: userId, invitee_email: inviteEmail });
      const sum = await axios.get(`${API}/referrals/summary`, { params: { user_id: userId } }).then(r => r.data);
      setReferral(prev => ({ ...prev, summary: sum }));
      setInviteEmail("");
      alert("Invite sent!");
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || "Failed to send invite");
    }
  };

  const loadKeys = async () => {
    try {
      const r = await axios.get(`${API}/user/api-keys/`, { withCredentials: true });
      setKeys((r.data && r.data.keys) || []);
    } catch (e) {
      /* silently ignore if disabled */
    }
  };
  useEffect(() => { loadKeys(); }, []);

  const onCreateKey = async () => {
    try {
      const r = await axios.post(`${API}/user/api-keys/create/`, { name: newKeyName || 'default' }, { withCredentials: true });
      alert(`Copy your API key now: ${r.data.api_key}`);
      setNewKeyName('');
      loadKeys();
    } catch (e) {
      alert(e?.response?.data?.detail || 'Failed to create key');
    }
  };
  const onRevokeKey = async (id) => {
    try {
      await axios.post(`${API}/user/api-keys/revoke/`, { id }, { withCredentials: true });
      loadKeys();
    } catch (e) {
      alert('Failed to revoke key');
    }
  };

  return (
    <div className="container mx-auto p-6">
      <header className="flex flex-col gap-2 items-start">
        <h1 className="text-3xl font-bold">RetailTradeScanner</h1>
        <p className="text-gray-600">
          Catch breakouts early · Find undervalued stocks in 1 click · Save hours of charting
        </p>
        {referral.link && (
          <div className="mt-2">
            <span className="text-sm">Your referral link: </span>
            <a className="text-blue-600 underline" href={referral.link} target="_blank" rel="noreferrer">
              {referral.link}
            </a>
          </div>
        )}
      </header>

      {loading && <p>Loading…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {health && (
        <section className="mt-6">
          <h2 className="text-xl font-semibold">System health</h2>
          <p className="text-sm text-gray-600">Status: {health.status} · DB: {health.mongodb}</p>
        </section>
      )}

      <section className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold">Breakouts</h2>
          <ul className="mt-2 list-disc ml-5">
            {breakouts.map((r) => (
              <li key={r.ticker || r.symbol}>
                <span className="font-mono">{r.ticker || r.symbol}</span> · Change {Number(r.change_percent ?? r.price_change_today ?? 0).toFixed(2)}%
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2 className="text-xl font-semibold">Undervalued</h2>
          <ul className="mt-2 list-disc ml-5">
            {undervalued.map((r) => (
              <li key={r.ticker || r.symbol}>
                <span className="font-mono">{r.ticker || r.symbol}</span> · P/E {Number(r.pe_ratio ?? 0).toFixed(2)} · Mkt Cap ${Number(r.market_cap ?? 0).toLocaleString()}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-xl font-semibold">Refer friends</h2>
        <p className="text-gray-600 text-sm">Invite 3 paid users, get 1 month free. Unlimited rewards.</p>
        <form className="mt-3 flex gap-2" onSubmit={onInvite}>
          <input
            type="email"
            required
            placeholder="friend@email.com"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            className="border px-3 py-2 rounded w-64"
          />
          <button className="bg-black text-white px-4 py-2 rounded" type="submit">Send invite</button>
        </form>
        {referral.summary && (
          <p className="text-sm mt-2">
            Invited: {referral.summary.total_invited} · Paid: {referral.summary.total_paid} · Earned months: {referral.summary.rewards_months_earned} · Granted: {referral.summary.rewards_months_granted} · Pending: {referral.summary.pending_rewards_months}
          </p>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-xl font-semibold">API access (private)</h2>
        <p className="text-gray-600 text-sm">Use API keys for server-to-server access. Keys are hidden by default in production.</p>
        <div className="mt-3 flex gap-2 items-center">
          <input className="border px-3 py-2 rounded" placeholder="Key name" value={newKeyName} onChange={(e)=>setNewKeyName(e.target.value)} />
          <button className="bg-black text-white px-4 py-2 rounded" onClick={onCreateKey}>Create key</button>
        </div>
        {!!keys.length && (
          <ul className="mt-3 list-disc ml-5">
            {keys.map(k => (
              <li key={k.id} className="flex items-center gap-2">
                <span>{k.name} · {k.prefix}•••• · {k.is_active ? 'active' : 'revoked'}</span>
                {k.is_active && <button className="text-red-600 underline" onClick={()=>onRevokeKey(k.id)}>Revoke</button>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

function App() {
  const [cookieConsent, setCookieConsent] = useState(() => window.localStorage.getItem('cookie_consent') || '');
  return (
    <div className="App">
      <BrowserRouter>
        {!cookieConsent && (
          <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-white border shadow p-4 rounded max-w-xl w-[90%] z-50">
            <p className="text-sm">We use cookies to improve your experience, analyze usage, and personalize content. See our <a className="underline" href="/privacy">Privacy Policy</a>.</p>
            <div className="mt-3 flex gap-2 justify-end">
              <button className="px-3 py-1 border rounded" onClick={() => {window.localStorage.setItem('cookie_consent','declined'); setCookieConsent('declined');}}>Decline</button>
              <button className="px-3 py-1 bg-black text-white rounded" onClick={() => {window.localStorage.setItem('cookie_consent','accepted'); setCookieConsent('accepted');}}>Accept</button>
            </div>
          </div>
        )}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/account" element={<Account />} />
          <Route path="*" element={<div className="p-6"><h1 className="text-2xl font-bold">404</h1><p className="text-gray-600">Page not found.</p></div>} />
          <Route path="/terms" element={<LegalPage type="terms" />} />
          <Route path="/privacy" element={<LegalPage type="privacy" />} />
        </Routes>
        <footer className="mt-12 border-t pt-6 text-sm text-gray-600">
          <div className="max-w-5xl mx-auto px-6 flex flex-col md:flex-row gap-2 justify-between">
            <div>© {new Date().getFullYear()} RetailTradeScanner</div>
            <nav className="flex gap-4">
              <a className="underline" href="/terms">Terms of Service</a>
              <a className="underline" href="/privacy">Privacy Policy</a>
            </nav>
          </div>
        </footer>
      </BrowserRouter>
    </div>
  );
}

export default App;
