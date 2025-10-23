import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Button } from './ui/button';

function loadChecklist(userId) {
  try {
    const raw = localStorage.getItem(`onboarding-checklist-v2:${userId}`);
    return raw ? JSON.parse(raw) : { ran_screener: false, saved_watchlist: false, created_alert: false };
  } catch {
    return { ran_screener: false, saved_watchlist: false, created_alert: false };
  }
}

function saveChecklist(userId, state) {
  try {
    localStorage.setItem(`onboarding-checklist-v2:${userId}`, JSON.stringify(state));
  } catch {}
}

export default function OnboardingChecklist({ userId, className }) {
  const [state, setState] = React.useState(() => loadChecklist(userId || 'anon'));
  React.useEffect(() => { saveChecklist(userId || 'anon', state); }, [userId, state]);

  const toggle = (key) => setState((prev) => ({ ...prev, [key]: !prev[key] }));

  const completed = Object.values(state).filter(Boolean).length;
  const total = 3;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Getting Started</CardTitle>
        <CardDescription>{completed} of {total} completed</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <label className="flex items-center gap-2">
          <Checkbox checked={state.ran_screener} onCheckedChange={() => toggle('ran_screener')} />
          <span>Run your first screener</span>
        </label>
        <label className="flex items-center gap-2">
          <Checkbox checked={state.saved_watchlist} onCheckedChange={() => toggle('saved_watchlist')} />
          <span>Save a stock to a watchlist</span>
        </label>
        <label className="flex items-center gap-2">
          <Checkbox checked={state.created_alert} onCheckedChange={() => toggle('created_alert')} />
          <span>Create a price alert</span>
        </label>
        <Button variant="outline" size="sm" onClick={() => setState({ ran_screener: false, saved_watchlist: false, created_alert: false })}>Reset</Button>
      </CardContent>
    </Card>
  );
}
