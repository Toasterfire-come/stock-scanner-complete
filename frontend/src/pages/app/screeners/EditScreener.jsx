import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import { Badge } from "../../../components/ui/badge";
import { X, Save, Play, Trash2 } from "lucide-react";
import { toast } from "sonner";

const EditScreener = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [screenerData, setScreenerData] = useState({
    name: "",
    description: "",
    isPublic: false
  });
  const [criteria, setCriteria] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const availableCriteria = [
    { id: "market_cap", name: "Market Cap", type: "range" },
    { id: "price", name: "Stock Price", type: "range" },
    { id: "volume", name: "Volume", type: "range" },
    { id: "pe_ratio", name: "P/E Ratio", type: "range" },
    { id: "dividend_yield", name: "Dividend Yield", type: "range" },
    { id: "change_percent", name: "Price Change %", type: "range" },
    { id: "exchange", name: "Exchange", type: "select" }
  ];

  useEffect(() => {
    // Simulate loading existing screener data
    setTimeout(() => {
      setScreenerData({
        name: "High Growth Tech",
        description: "Technology stocks with >20% revenue growth",
        isPublic: true
      });
      setCriteria([
        {
          id: "market_cap",
          name: "Market Cap",
          type: "range",
          min: "1000000000",
          max: "100000000000"
        },
        {
          id: "change_percent",
          name: "Price Change %",
          type: "range",
          min: "5",
          max: ""
        }
      ]);
      setIsLoading(false);
    }, 1000);
  }, [id]);

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

    setIsSaving(true);
    try {
      // Persist to local storage and then run a test
      const payload = { ...screenerData, criteria };
      window.localStorage.setItem('screener:lastSaved', JSON.stringify(payload));
      toast.success("Screener saved");
      // Also run a test with the current params
      navigate("/app/screeners/adhoc/results");
    } catch (error) {
      toast.error("Failed to update screener");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this screener?")) return;

    setIsSaving(true);
    try {
      // Simulate API call to delete screener
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("Screener deleted successfully");
      navigate("/app/screeners");
    } catch (error) {
      toast.error("Failed to delete screener");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Edit Screener</h1>
            <p className="text-gray-600 mt-2">Modify your stock screening criteria</p>
          </div>
          <div className="flex gap-2">
            <Button variant="destructive" onClick={handleDelete} disabled={isSaving}>
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              <Play className="h-4 w-4 mr-2" />
              Save & Test
            </Button>
          </div>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name">Screener Name</Label>
                <Input
                  id="name"
                  value={screenerData.name}
                  onChange={(e) => setScreenerData({...screenerData, name: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={screenerData.description}
                  onChange={(e) => setScreenerData({...screenerData, description: e.target.value})}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Screening Criteria</CardTitle>
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
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default EditScreener;