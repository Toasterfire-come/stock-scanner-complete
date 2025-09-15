import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import { Separator } from "../../../components/ui/separator";
import { Badge } from "../../../components/ui/badge";
import { X, Plus, Save, Play } from "lucide-react";
import { toast } from "sonner";
import { filterStocks } from "../../../api/client";

const CreateScreener = () => {
  const navigate = useNavigate();
  const [screenerData, setScreenerData] = useState({
    name: "",
    description: "",
    isPublic: false
  });
  const [criteria, setCriteria] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

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
      mode: "range",
      min: "",
      max: "",
      value: ""
    };

    setCriteria([...criteria, newCriterion]);
  };

  const buildFilterParams = (criteriaList) => {
    // Only include defined, non-empty values; never send placeholders like null/none/empty strings
    const params = {};
    const addNum = (key, val) => {
      if (val === undefined || val === null) return;
      const v = String(val).trim();
      if (!v || v.toLowerCase() === 'none' || v.toLowerCase() === 'null') return;
      const n = Number(v);
      if (!Number.isFinite(n)) return;
      params[key] = n;
    };
    const applyNumericFilter = (base, c) => {
      const mode = (c.mode || 'range');
      if (mode === 'eq') {
        addNum(`${base}_eq`, c.value);
        return;
      }
      if (mode === 'gte' || mode === 'range') {
        addNum(`${base}_min`, c.min);
      }
      if (mode === 'lte' || mode === 'range') {
        addNum `${base}_max`, c.max;
      }
    };
    for (const c of criteriaList) {
      if (c.id === "market_cap") { applyNumericFilter('market_cap', c); }
      if (c.id === "price") { applyNumericFilter('price', c); }
      if (c.id === "volume") { applyNumericFilter('volume', c); }
      if (c.id === "pe_ratio") { applyNumericFilter('pe_ratio', c); }
      if (c.id === "dividend_yield") { applyNumericFilter('dividend_yield', c); }
      if (c.id === "change_percent") { applyNumericFilter('change_percent', c); }
      if (c.id === "exchange") {
        const v = (c.value || '').trim();
        if (v && v.toLowerCase() !== 'none' && v.toLowerCase() !== 'null') params.exchange = v;
      }
    }
    return params;
  };

  const removeCriterion = (criterionId) => {
    setCriteria(criteria.filter(c => c.id !== criterionId));
  };

  const updateCriterion = (criterionId, field, value) => {
    setCriteria(criteria.map(c => 
      c.id === criterionId ? { ...c, [field]: value } : c
    ));
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

    // Persist to local storage as the source of truth for now
    try {
      const payload = { ...screenerData, criteria };
      window.localStorage.setItem('screener:lastSaved', JSON.stringify(payload));
    } catch {}
  };

  const handleTest = async () => {
    if (criteria.length === 0) {
      toast.error("Please add at least one criterion");
      return;
    }

    setIsLoading(true);
    try {
      // Save before testing
      await handleSave();
      const params = buildFilterParams(criteria);
      const data = await filterStocks(params);
      const rows = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : []);
      const count = rows.length || 0;
      window.localStorage.setItem('screener:lastParams', JSON.stringify(params));
      toast.success(`Found ${count} matching stocks`);
      navigate(`/app/screeners/adhoc/results`);
    } catch (error) {
      toast.error("Failed to test screener");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Stock Screener</h1>
            <p className="text-gray-600 mt-2">Set up criteria to find stocks that match your strategy</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleTest} disabled={isLoading}>
              <Play className="h-4 w-4 mr-2" />
              Save & Test
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
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
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Screening Criteria</CardTitle>
                <CardDescription>Add filters to narrow down your stock selection</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <Select onValueChange={addCriterion}>
                    <SelectTrigger>
                      <SelectValue placeholder="Add a criterion" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableCriteria
                        .filter(c => !criteria.some(existing => existing.id === c.id))
                        .map(criterion => (
                          <SelectItem key={criterion.id} value={criterion.id}>
                            {criterion.name}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-4">
                  {criteria.map((criterion) => (
                    <div key={criterion.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-3">
                        <Badge variant="outline">{criterion.name}</Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeCriterion(criterion.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      {criterion.type === "range" && (
                        <>
                          <div className="mb-3">
                            <Label>Operator</Label>
                            <Select value={criterion.mode} onValueChange={(v) => updateCriterion(criterion.id, "mode", v)}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select operator" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="range">Between (inclusive)</SelectItem>
                                <SelectItem value="gte">Greater than or equal</SelectItem>
                                <SelectItem value="lte">Less than or equal</SelectItem>
                                <SelectItem value="eq">Equal to</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          {criterion.mode === 'eq' ? (
                            <div>
                              <Label>Value</Label>
                              <Input
                                type="number"
                                value={criterion.value}
                                onChange={(e) => updateCriterion(criterion.id, "value", e.target.value)}
                                placeholder="Exact value"
                              />
                            </div>
                          ) : (
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <Label>Minimum</Label>
                                <Input
                                  type="number"
                                  value={criterion.min}
                                  onChange={(e) => updateCriterion(criterion.id, "min", e.target.value)}
                                  placeholder="Min value"
                                  disabled={criterion.mode === 'lte'}
                                />
                              </div>
                              <div>
                                <Label>Maximum</Label>
                                <Input
                                  type="number"
                                  value={criterion.max}
                                  onChange={(e) => updateCriterion(criterion.id, "max", e.target.value)}
                                  placeholder="Max value"
                                  disabled={criterion.mode === 'gte'}
                                />
                              </div>
                            </div>
                          )}
                        </>
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
                  Click "Save & Test" to save your configuration and see how many stocks match your criteria.
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