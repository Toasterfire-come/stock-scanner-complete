import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import {
  EnhancedSelect,
  EnhancedSelectContent,
  EnhancedSelectItem,
  EnhancedSelectTrigger,
  EnhancedSelectValue,
  EnhancedSelectGroup,
  EnhancedSelectLabel
} from "../../../components/ui/enhanced-select";
import { Textarea } from "../../../components/ui/textarea";
import { Separator } from "../../../components/ui/separator";
import { Badge } from "../../../components/ui/badge";
import { X, Plus, Save, Play, DollarSign, TrendingUp, BarChart3, Target } from "lucide-react";
import { toast } from "sonner";
import { createScreener, runScreener } from "../../../api/client";

const CreateScreener = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [screenerData, setScreenerData] = useState({
    name: "",
    description: "",
    isPublic: false
  });
  const [criteria, setCriteria] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const availableCriteria = [
    // Price & Valuation
    { id: "market_cap", name: "Market Cap", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },
    { id: "price", name: "Stock Price", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },
    { id: "pe_ratio", name: "P/E Ratio", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },
    { id: "price_to_book", name: "Price to Book", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },
    { id: "dividend_yield", name: "Dividend Yield", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },
    { id: "bid_price", name: "Bid Price", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },
    { id: "ask_price", name: "Ask Price", type: "range", category: "price", icon: <DollarSign className="h-4 w-4" /> },

    // Trading Activity
    { id: "volume", name: "Volume", type: "range", category: "trading", icon: <BarChart3 className="h-4 w-4" /> },
    { id: "dvav", name: "Volume vs Avg (DV/AV)", type: "range", category: "trading", icon: <BarChart3 className="h-4 w-4" /> },
    { id: "change_percent", name: "Price Change %", type: "range", category: "trading", icon: <TrendingUp className="h-4 w-4" /> },

    // Fundamentals
    { id: "earnings_per_share", name: "Earnings Per Share (EPS)", type: "range", category: "fundamentals", icon: <Target className="h-4 w-4" /> },
    { id: "book_value", name: "Book Value", type: "range", category: "fundamentals", icon: <Target className="h-4 w-4" /> },

    // 52-Week Metrics
    { id: "week_52_low", name: "52-Week Low", type: "range", category: "52week", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "week_52_high", name: "52-Week High", type: "range", category: "52week", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "one_year_target", name: "1-Year Target", type: "range", category: "52week", icon: <Target className="h-4 w-4" /> },

    // Exchange
    { id: "exchange", name: "Exchange", type: "select", category: "other" }
  ];

  const getCriteriaByCategory = (category) => {
    return availableCriteria.filter(c => c.category === category && !criteria.some(existing => existing.id === c.id));
  };

  // Apply getting-started template if requested
  useEffect(() => {
    try {
      const params = new URLSearchParams(location.search || "");
      const template = params.get("template");
      if (template === "getting-started") {
        setScreenerData({
          name: "Getting Started: Momentum Setup",
          description: "Example screener: Price > $10, Volume > 1,000,000, RSI 50-70",
          isPublic: false
        });
        setCriteria([
          { id: "price", name: "Stock Price", type: "range", min: "10", max: "", value: "" },
          { id: "volume", name: "Volume", type: "range", min: "1000000", max: "", value: "" },
          { id: "change_percent", name: "Price Change %", type: "range", min: "2", max: "", value: "" }
        ]);
      }
    } catch {}
  }, [location.search]);

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

  const buildFilterParams = (criteriaList) => {
    const params = {};
    for (const c of criteriaList) {
      if (c.id === "market_cap") { if (c.min) params.market_cap_min = Number(c.min); if (c.max) params.market_cap_max = Number(c.max); }
      if (c.id === "price") { if (c.min) params.price_min = Number(c.min); if (c.max) params.price_max = Number(c.max); }
      if (c.id === "volume") { if (c.min) params.volume_min = Number(c.min); if (c.max) params.volume_max = Number(c.max); }
      if (c.id === "pe_ratio") { if (c.min) params.pe_ratio_min = Number(c.min); if (c.max) params.pe_ratio_max = Number(c.max); }
      if (c.id === "dividend_yield") { if (c.min) params.dividend_yield_min = Number(c.min); if (c.max) params.dividend_yield_max = Number(c.max); }
      if (c.id === "change_percent") { if (c.min) params.change_percent_min = Number(c.min); if (c.max) params.change_percent_max = Number(c.max); }
      if (c.id === "price_to_book") { if (c.min) params.price_to_book_min = Number(c.min); if (c.max) params.price_to_book_max = Number(c.max); }
      if (c.id === "earnings_per_share") { if (c.min) params.earnings_per_share_min = Number(c.min); if (c.max) params.earnings_per_share_max = Number(c.max); }
      if (c.id === "book_value") { if (c.min) params.book_value_min = Number(c.min); if (c.max) params.book_value_max = Number(c.max); }
      if (c.id === "week_52_low") { if (c.min) params.week_52_low_min = Number(c.min); if (c.max) params.week_52_low_max = Number(c.max); }
      if (c.id === "week_52_high") { if (c.min) params.week_52_high_min = Number(c.min); if (c.max) params.week_52_high_max = Number(c.max); }
      if (c.id === "one_year_target") { if (c.min) params.one_year_target_min = Number(c.min); if (c.max) params.one_year_target_max = Number(c.max); }
      if (c.id === "dvav") { if (c.min) params.dvav_min = Number(c.min); if (c.max) params.dvav_max = Number(c.max); }
      if (c.id === "bid_price") { if (c.min) params.bid_price_min = Number(c.min); if (c.max) params.bid_price_max = Number(c.max); }
      if (c.id === "ask_price") { if (c.min) params.ask_price_min = Number(c.min); if (c.max) params.ask_price_max = Number(c.max); }
      if (c.id === "exchange" && c.value) { params.exchange = c.value; }
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

    setIsLoading(true);
    try {
      const payload = { name: screenerData.name, description: screenerData.description, criteria: criteria.map(({ id, min, max, value }) => ({ id, ...(min ? { min: Number(min) } : {}), ...(max ? { max: Number(max) } : {}), ...(value ? { value } : {}) })), is_public: screenerData.isPublic };
      const res = await createScreener(payload);
      if (res?.success) {
        toast.success("Screener saved successfully");
        navigate("/app/screeners");
      } else {
        throw new Error(res?.message || 'Failed');
      }
    } catch (error) {
      toast.error("Failed to save screener");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTest = async () => {
    if (criteria.length === 0) {
      toast.error("Please add at least one criterion");
      return;
    }

    setIsLoading(true);
    try {
      // Create a temporary saved screener and run it, then navigate to its results
      const tmpName = screenerData.name?.trim() || `Adhoc Screener ${new Date().toLocaleString()}`;
      const payload = { name: tmpName, description: screenerData.description, criteria: criteria.map(({ id, min, max, value }) => ({ id, ...(min ? { min: Number(min) } : {}), ...(max ? { max: Number(max) } : {}), ...(value ? { value } : {}) })), is_public: false };
      const res = await createScreener(payload);
      const newId = res?.data?.id || res?.id;
      if (!newId) throw new Error('Failed to create temporary screener');
      await runScreener(newId);
      toast.success("Screener ran successfully");
      try {
        const coach = (location.state && location.state.coach) || null;
        if (coach === 'run_save_alert') {
          setTimeout(() => {
            toast.info('Next: Save your screener', { description: 'Click Save Screener to reuse later.' });
          }, 500);
          setTimeout(() => {
            toast.info('Then: Set an alert', { description: 'Create an alert to be notified when new stocks match.' });
          }, 2000);
        }
      } catch {}
      navigate(`/app/screeners/${newId}/results`);
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
              Filter
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              Save Screener
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
                  <EnhancedSelect onValueChange={addCriterion}>
                    <EnhancedSelectTrigger>
                      <EnhancedSelectValue placeholder="Search and add a criterion..." />
                    </EnhancedSelectTrigger>
                    <EnhancedSelectContent
                      searchable={true}
                      searchPlaceholder="Search criteria..."
                      showCount={true}
                      grouped={true}
                      maxHeight={400}
                    >
                      {getCriteriaByCategory('price').length > 0 && (
                        <EnhancedSelectGroup>
                          <EnhancedSelectLabel>Price & Valuation</EnhancedSelectLabel>
                          {getCriteriaByCategory('price').map(criterion => (
                            <EnhancedSelectItem
                              key={criterion.id}
                              value={criterion.id}
                              icon={criterion.icon}
                            >
                              {criterion.name}
                            </EnhancedSelectItem>
                          ))}
                        </EnhancedSelectGroup>
                      )}

                      {getCriteriaByCategory('trading').length > 0 && (
                        <EnhancedSelectGroup>
                          <EnhancedSelectLabel>Trading Activity</EnhancedSelectLabel>
                          {getCriteriaByCategory('trading').map(criterion => (
                            <EnhancedSelectItem
                              key={criterion.id}
                              value={criterion.id}
                              icon={criterion.icon}
                            >
                              {criterion.name}
                            </EnhancedSelectItem>
                          ))}
                        </EnhancedSelectGroup>
                      )}

                      {getCriteriaByCategory('fundamentals').length > 0 && (
                        <EnhancedSelectGroup>
                          <EnhancedSelectLabel>Fundamentals</EnhancedSelectLabel>
                          {getCriteriaByCategory('fundamentals').map(criterion => (
                            <EnhancedSelectItem
                              key={criterion.id}
                              value={criterion.id}
                              icon={criterion.icon}
                            >
                              {criterion.name}
                            </EnhancedSelectItem>
                          ))}
                        </EnhancedSelectGroup>
                      )}

                      {getCriteriaByCategory('52week').length > 0 && (
                        <EnhancedSelectGroup>
                          <EnhancedSelectLabel>52-Week Metrics</EnhancedSelectLabel>
                          {getCriteriaByCategory('52week').map(criterion => (
                            <EnhancedSelectItem
                              key={criterion.id}
                              value={criterion.id}
                              icon={criterion.icon}
                            >
                              {criterion.name}
                            </EnhancedSelectItem>
                          ))}
                        </EnhancedSelectGroup>
                      )}

                      {getCriteriaByCategory('other').length > 0 && (
                        <EnhancedSelectGroup>
                          <EnhancedSelectLabel>Other</EnhancedSelectLabel>
                          {getCriteriaByCategory('other').map(criterion => (
                            <EnhancedSelectItem
                              key={criterion.id}
                              value={criterion.id}
                            >
                              {criterion.name}
                            </EnhancedSelectItem>
                          ))}
                        </EnhancedSelectGroup>
                      )}
                    </EnhancedSelectContent>
                  </EnhancedSelect>
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
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label>Minimum</Label>
                            <Input
                              type="number"
                              value={criterion.min}
                              onChange={(e) => updateCriterion(criterion.id, "min", e.target.value)}
                              placeholder="Min value"
                            />
                          </div>
                          <div>
                            <Label>Maximum</Label>
                            <Input
                              type="number"
                              value={criterion.max}
                              onChange={(e) => updateCriterion(criterion.id, "max", e.target.value)}
                              placeholder="Max value"
                            />
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