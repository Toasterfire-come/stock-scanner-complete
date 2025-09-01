import React, { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { revenueApply, revenueInitialize, revenueValidate } from "../api/client";

const PLANS = [
  { id: "basic", name: "Basic", price: 24.99, features: ["Core screeners", "Daily alerts", "Watchlist"] },
  { id: "pro", name: "Pro", price: 49.99, features: ["Everything in Basic", "Advanced filters", "Unlimited alerts"] },
];

export default function Pricing() {
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  const prefillCode = params.get("code") || "";

  const [selected, setSelected] = useState("pro");
  const [promo, setPromo] = useState(prefillCode);
  const [paypalEmail, setPayPalEmail] = useState("");
  const [applying, setApplying] = useState(false);
  const [result, setResult] = useState(null);

  const price = useMemo(() => PLANS.find((p) => p.id === selected)?.price || 0, [selected]);

  useEffect(() => {
    revenueInitialize().catch(() => {});
  }, []);

  const applyCode = async () => {
    setApplying(true);
    try {
      const valid = await revenueValidate(promo);
      if (!valid?.valid) {
        setResult({ message: valid?.message || "Invalid code", final_amount: price, discount_amount: 0, applies_discount: false });
        return;
      }
      const applied = await revenueApply(promo, price);
      setResult(applied);
    } catch (e) {
      setResult({ message: e?.response?.data || "Failed to apply", final_amount: price, discount_amount: 0, applies_discount: false });
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">Choose your plan</h1>
      <div className="grid md:grid-cols-2 gap-6">
        {PLANS.map((plan) => (
          <Card key={plan.id} className={selected === plan.id ? "ring-2 ring-primary" : ""}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{plan.name}</span>
                <span className="text-xl">${plan.price}/mo</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                {plan.features.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button variant={selected === plan.id ? "default" : "outline"} onClick={() => setSelected(plan.id)}>
                {selected === plan.id ? "Selected" : "Select"}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Checkout</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4 items-end">
            <div>
              <Label htmlFor="promo">Promo code</Label>
              <Input id="promo" placeholder="trial" value={promo} onChange={(e) => setPromo(e.target.value)} />
            </div>
            <div>
              <Label className="invisible">&nbsp;</Label>
              <Button onClick={applyCode} disabled={applying}>Apply</Button>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Subtotal</div>
              <div className="text-xl font-semibold">${price.toFixed(2)}</div>
            </div>
          </div>

          {result && (
            <div className="grid md:grid-cols-3 gap-4">
              <div className="md:col-span-2 text-sm">
                <div>Code: <b>{promo}</b> — {result.message}</div>
                <div>Discount: ${result.discount_amount?.toFixed?.(2) ?? 0}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Total due now</div>
                <div className="text-2xl font-semibold">${result.final_amount?.toFixed?.(2) ?? price.toFixed(2)}</div>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="pp">PayPal account email</Label>
              <Input id="pp" placeholder="you@paypal.com" value={paypalEmail} onChange={(e) => setPayPalEmail(e.target.value)} />
              <p className="text-xs text-muted-foreground mt-1">We will redirect you to PayPal to complete the purchase. Live PayPal buttons require a Client ID; share later to enable.</p>
            </div>
            <div className="flex items-end justify-end gap-3">
              <Button variant="outline">Pay with PayPal</Button>
              <Button disabled>Complete Order</Button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">Trial: Use code <b>trial</b> to start 7 days for $1. Auto-renews at full price unless cancelled.</p>
        </CardContent>
      </Card>
    </div>
  );
}