import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div>
      {/* Promo banner */}
      <div className="w-full bg-yellow-300 text-black text-sm md:text-base py-2 px-4 text-center">
        <span className="font-semibold">Limited-time:</span> 7-day trial for $1 on any plan — Use code <span className="font-bold">TRIAL</span>
      </div>

      {/* Hero section */}
      <header className="App-header">
        <div className="max-w-3xl px-6 text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight">
            Get full access with a 7-day trial for $1
          </h1>
          <p className="mt-4 text-lg md:text-xl text-gray-300">
            Unlock all features on any plan. Apply code <span className="font-semibold text-white">TRIAL</span> at checkout.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
            <a href="#pricing" className="inline-flex items-center justify-center rounded-md bg-white text-black px-6 py-3 font-medium shadow hover:opacity-90 transition">
              Start 7-day trial — $1
            </a>
            <a href="#pricing" className="inline-flex items-center justify-center rounded-md border border-white/30 px-6 py-3 font-medium text-white hover:bg-white/10 transition">
              View plans
            </a>
          </div>

          <ul className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm text-gray-300">
            <li className="bg-white/5 rounded-md px-3 py-2">All features on any plan</li>
            <li className="bg-white/5 rounded-md px-3 py-2">Cancel anytime</li>
            <li className="bg-white/5 rounded-md px-3 py-2">No hidden fees</li>
          </ul>
        </div>
      </header>

      {/* Pricing section */}
      <section id="pricing" className="py-16 px-6 bg-white text-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-extrabold">Choose your plan</h2>
            <p className="mt-2 text-gray-600">Try any plan for 7 days for $1 with code <span className="font-semibold">TRIAL</span>.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Basic */}
            <div className="rounded-xl border border-gray-200 p-6 shadow-sm">
              <h3 className="text-xl font-semibold">Basic</h3>
              <p className="mt-1 text-gray-600">Great to get started</p>
              <div className="mt-4">
                <span className="text-4xl font-extrabold">$19</span>
                <span className="text-gray-600">/mo</span>
              </div>
              <ul className="mt-4 space-y-2 text-sm text-gray-700">
                <li>Core features</li>
                <li>Email support</li>
              </ul>
              <a href="#" className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-black text-white px-4 py-2 font-medium hover:opacity-90 transition">
                Start $1 trial
              </a>
              <p className="mt-2 text-xs text-gray-500">Use code TRIAL at checkout.</p>
            </div>

            {/* Pro */}
            <div className="rounded-xl border-2 border-black p-6 shadow-md">
              <div className="inline-flex items-center gap-2 rounded-full bg-black text-white px-3 py-1 text-xs">Most Popular</div>
              <h3 className="mt-3 text-xl font-semibold">Pro</h3>
              <p className="mt-1 text-gray-600">Advanced for power users</p>
              <div className="mt-4">
                <span className="text-4xl font-extrabold">$49</span>
                <span className="text-gray-600">/mo</span>
              </div>
              <ul className="mt-4 space-y-2 text-sm text-gray-700">
                <li>Everything in Basic</li>
                <li>Priority support</li>
              </ul>
              <a href="#" className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-black text-white px-4 py-2 font-medium hover:opacity-90 transition">
                Start $1 trial
              </a>
              <p className="mt-2 text-xs text-gray-500">Use code TRIAL at checkout.</p>
            </div>

            {/* Enterprise */}
            <div className="rounded-xl border border-gray-200 p-6 shadow-sm">
              <h3 className="text-xl font-semibold">Enterprise</h3>
              <p className="mt-1 text-gray-600">For teams and orgs</p>
              <div className="mt-4">
                <span className="text-4xl font-extrabold">$99</span>
                <span className="text-gray-600">/mo</span>
              </div>
              <ul className="mt-4 space-y-2 text-sm text-gray-700">
                <li>Everything in Pro</li>
                <li>Dedicated support</li>
              </ul>
              <a href="#" className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-black text-white px-4 py-2 font-medium hover:opacity-90 transition">
                Start $1 trial
              </a>
              <p className="mt-2 text-xs text-gray-500">Use code TRIAL at checkout.</p>
            </div>
          </div>
        </div>
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
