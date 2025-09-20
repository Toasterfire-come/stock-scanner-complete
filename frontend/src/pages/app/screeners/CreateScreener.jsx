import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import { Separator } from "../../../components/ui/separator";
import { Badge } from "../../../components/ui/badge";
import { X, Plus, Save, Play, Upload, Download } from "lucide-react";
import { toast } from "sonner";
import { createScreener, testScreener } from "../../../api/client";
import { useAuth } from "../../../context/AuthContext";
import { Link, useLocation } from "react-router-dom";
import { logClientMetric } from "../../../api/client";

const CreateScreener = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const [screenerData, setScreenerData] = useState({
    name: "",
    description: "",
    isPublic: false
  });
  const [criteria, setCriteria] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Load from querystring or localStorage drafts
  useEffect(() => {
    try {
      const params = new URLSearchParams(location.search);
      const criteriaParam = params.get('criteria');
      if (criteriaParam) {
        const parsed = JSON.parse(decodeURIComponent(criteriaParam));
        if (Array.isArray(parsed)) setCriteria(parsed);
      }
    } catch {}
    try {
      const draft = JSON.parse(localStorage.getItem('draft_screener_new') || 'null');
      if (draft && Array.isArray(draft.criteria)) {
        setCriteria(draft.criteria);
        setScreenerData(draft.meta || screenerData);
      }
    } catch {}
    try {
      const imported = JSON.parse(localStorage.getItem('draft_screener_import') || 'null');
      if (imported && Array.isArray(imported.criteria)) {
        setCriteria(imported.criteria);
        setScreenerData({ name: imported.name || '', description: imported.description || '', isPublic: Boolean(imported.isPublic) });
        localStorage.removeItem('draft_screener_import');
      }
    } catch {}
  }, []);

  // Autosave drafts
  useEffect(() => {
    localStorage.setItem('draft_screener_new', JSON.stringify({ criteria, meta: screenerData }));
  }, [criteria, screenerData]);

  const availableCriteria = [
    { id: "market_cap", name: "Market Cap", type: "range" },
    { id: "price", name: "Stock Price", type: "range" },
    { id: "volume", name: "Volume", type: "range" },
    { id: "pe_ratio", name: "P/E Ratio", type: "range" },
    { id: "dividend_yield", name: "Dividend Yield", type: "range" },
    { id: "change_percent", name: "Price Change %", type: "range" },
    { id: "exchange", name: "Exchange", type: "select" }
  ];

  const addCriterion = (criterionId) => {
    const criterionDef = availableCriteria.find(c => c.id === criterionId);
    if (!criterionDef || criteria.some(c => c.id === criterionId)) return;

    const newCriterion = {
      id: criterionId,
      name: criterionDef.name,
      type: criterionDef.type,
      min: "",
      max: "",
      value: ""
    };

    setCriteria([...criteria, newCriterion]);
  };

  const removeCriterion = (criterionId) => {
    setCriteria(criteria.filter(c => c.id !== criterionId));
  };

  const updateCriterion = (criterionId, field, value) => {
    setCriteria(criteria.map(c => 
      c.id === criterionId ? { ...c, [field]: value } : c
    ));
  };

  const validate = () => {
    const next = {};
    for (const c of criteria) {
      if (c.type === 'range') {
        const min = c.min === '' ? null : Number(c.min);
        const max = c.max === '' ? null : Number(c.max);
        if ((c.min !== '' && Number.isNaN(min)) || (c.max !== '' && Number.isNaN(max))) {
          next[c.id] = 'Enter numeric values';
        } else if (min !== null && max !== null && min > max) {
          next[c.id] = 'Min cannot exceed Max';
        }
      }
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSave = async () => {
    if (!screenerData.name.trim()) {
      toast.error("Please enter a screener name");
      return;
    }

    if (criteria.length === 0) {
      toast.error("Please add at least one criterion");
      return;
    }

    if (!validate()) return;

    if (!isAuthenticated) {
      toast.error("Please sign in to save a Screener");
      return;
    }

    setIsLoading(true);
    try {
      const payload = { ...screenerData, criteria };
      const res = await createScreener(payload);
      toast.success("Screener saved successfully");
      logClientMetric({ event: 'screener_created' });
      const sid = res?.id;
      if (sid) navigate(`/app/screeners/${sid}/results`);
      else navigate("/app/screeners");
    } catch (error) {
      toast.error("Failed to save screener");
    } finally { setIsLoading(false); }
  };

  const handleTest = async () => {
    if (criteria.length === 0) {
      toast.error("Please add at least one criterion");
      return;
    }

    setIsLoading(true);
    try {
      const payload = { ...screenerData, criteria };
      const res = await testScreener(payload);
      const count = Array.isArray(res?.results) ? res.results.length : (res?.count ?? 0);
      toast.success(`Found ${count} matching stocks`);
      // Update URL with shareable criteria
      const params = new URLSearchParams(location.search);
      params.set('criteria', encodeURIComponent(JSON.stringify(criteria)));
      window.history.replaceState({}, '', `${location.pathname}?${params.toString()}`);
      logClientMetric({ event: 'screener_test_run', count });
    } catch (error) { toast.error("Failed to test screener"); } finally { setIsLoading(false); }
  };

  const handleImportJson = async (event) => {
    try {
      const file = event.target.files?.[0];
      if (!file) return;
      const text = await file.text();
      const parsed = JSON.parse(text);
      const importedCriteria = Array.isArray(parsed?.criteria) ? parsed.criteria : [];
      const name = parsed?.name || screenerData.name;
      const description = parsed?.description || screenerData.description;
      setScreenerData({ ...screenerData, name, description });
      setCriteria(importedCriteria);
      toast.success("Criteria imported from JSON");
    } catch {
      toast.error("Invalid JSON file");
    } finally {
      event.target.value = "";
    }
  };

  const handleExportJson = () => {
    const payload = { ...screenerData, criteria };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(screenerData.name || 'screener').replace(/\s+/g,'-').toLowerCase()}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Stock Screener</h1>
            <p className="text-gray-600 mt-2">Set up criteria to find stocks that match your strategy</p>
              <div className="text-xs mt-2">
                <Link to="/docs#screeners" className="text-blue-600">Learn more about Screeners</Link>
              </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleTest} disabled={isLoading}>
              <Play className="h-4 w-4 mr-2" />
              Test Run
            </Button>
            <Button onClick={handleSave} disabled={isLoading || !isAuthenticated} aria-disabled={!isAuthenticated} title={!isAuthenticated ? 'Sign in to save' : undefined}>
              <Save className="h-4 w-4 mr-2" />
              Save Screener
            </Button>
            {!isAuthenticated && (
              <Button asChild variant="secondary">
                <Link to="/auth/sign-in">Sign in</Link>
              </Button>
            )}
            <Button type="button" variant="outline" onClick={handleExportJson}>
              <Download className="h-4 w-4 mr-2" />
              Export JSON
            </Button>
            <label className="inline-flex items-center">
              <input type="file" accept="application/json" className="hidden" onChange={handleImportJson} />
              <Button asChild variant="outline">
                <span>
                  <Upload className="h-4 w-4 mr-2" /> Import JSON
                </span>
              </Button>
            </label>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle id="screener-basic-title">Basic Information</CardTitle>
                <CardDescription>Give your screener a name and description</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="name">Screener Name</Label>
                  <Input
                    id="name"
                    value={screenerData.name}
                    onChange={(e) => setScreenerData({...screenerData, name: e.target.value})}
                    placeholder="e.g., High Dividend Value Stocks"
                    aria-required="true"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={screenerData.description}
                    onChange={(e) => setScreenerData({...screenerData, description: e.target.value})}
                    placeholder="Describe what this screener looks for..."
                    rows={3}
                    aria-describedby="screener-basic-title"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle id="criteria-title">Screening Criteria</CardTitle>
                <CardDescription>Add filters to narrow down your stock selection</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <Select onValueChange={addCriterion}>
                    <SelectTrigger>
                      <SelectValue placeholder="Add a criterion" aria-label="Add a criterion" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableCriteria
                        .filter(c => !criteria.some(existing => existing.id === c.id))
                        .map(criterion => (
                          <SelectItem key={criterion.id} value={criterion.id} aria-label={criterion.name}>
                            {criterion.name}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-4">
                  {criteria.map((criterion) => (
                    <div key={criterion.id} className="border rounded-lg p-4" role="group" aria-labelledby={`crit-${criterion.id}`}> 
                      <div className="flex justify-between items-center mb-3">
                        <Badge variant="outline" id={`crit-${criterion.id}`}>{criterion.name}</Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeCriterion(criterion.id)}
                          aria-label={`Remove ${criterion.name}`}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      {criterion.type === "range" && (
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label>Minimum</Label>
                            <Input
                              type="number"
                              value={criterion.min}
                              onChange={(e) => updateCriterion(criterion.id, "min", e.target.value)}
                              placeholder="Min value"
                              aria-label={`${criterion.name} minimum`}
                            />
                            <div className="text-xs text-gray-500 mt-1">
                              {criterion.id === 'price' && 'USD'}
                              {criterion.id === 'volume' && 'Shares'}
                              {criterion.id === 'market_cap' && 'USD'}
                            </div>
                          </div>
                          <div>
                            <Label>Maximum</Label>
                            <Input
                              type="number"
                              value={criterion.max}
                              onChange={(e) => updateCriterion(criterion.id, "max", e.target.value)}
                              placeholder="Max value"
                              aria-label={`${criterion.name} maximum`}
                            />
                            {errors[criterion.id] && (
                              <div className="text-xs text-red-600 mt-1">{errors[criterion.id]}</div>
                            )}
                          </div>
                        </div>
                      )}

                      {criterion.type === "select" && criterion.id === "exchange" && (
                        <Select onValueChange={(value) => updateCriterion(criterion.id, "value", value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select exchange" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="NYSE">NYSE</SelectItem>
                            <SelectItem value="NASDAQ">NASDAQ</SelectItem>
                            <SelectItem value="AMEX">AMEX</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    </div>
                  ))}
                </div>

                {criteria.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    No criteria added yet. Select from the dropdown above to add filters.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div>
            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Criteria Count</span>
                    <span className="font-semibold">{criteria.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Expected Matches</span>
                    <span className="font-semibold text-blue-600">~15-50</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Test Run</span>
                    <span className="font-semibold">Never</span>
                  </div>
                </div>
                <Separator className="my-4" />
                <div className="text-xs text-gray-500">
                  Click "Test Run" to see how many stocks match your current criteria.
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateScreener;