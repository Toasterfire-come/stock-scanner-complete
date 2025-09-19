import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [health, setHealth] = useState(null);
  const [breakouts, setBreakouts] = useState([]);
  const [undervalued, setUndervalued] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [referral, setReferral] = useState({ link: null, code: null, summary: null });
  const [inviteEmail, setInviteEmail] = useState("");
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
          axios.get(`${API}/health`).then(r => r.data),
          axios.get(`${API}/scans/breakouts`, { params: { universe: "sp500", limit: 5 } }).then(r => r.data),
          axios.get(`${API}/scans/undervalued`, { params: { universe: "sp500", limit: 5 } }).then(r => r.data),
          axios.get(`${API}/referrals/link`, { params: { user_id: userId } }).then(r => r.data),
          axios.get(`${API}/referrals/summary`, { params: { user_id: userId } }).then(r => r.data),
        ]);
        setHealth(h);
        setBreakouts(b.results || []);
        setUndervalued(u.results || []);
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
              <li key={r.symbol}>
                <span className="font-mono">{r.symbol}</span> · +{r.pct_above_prior_high?.toFixed(2)}% above 20d high · Vol x{r.volume_ratio_vs_20d?.toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2 className="text-xl font-semibold">Undervalued</h2>
          <ul className="mt-2 list-disc ml-5">
            {undervalued.map((r) => (
              <li key={r.symbol}>
                <span className="font-mono">{r.symbol}</span> · P/E {r.pe_ratio?.toFixed(2)} · P/B {r.price_to_book?.toFixed(2)} · Score {r.undervalued_score?.toFixed(2)}
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
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
