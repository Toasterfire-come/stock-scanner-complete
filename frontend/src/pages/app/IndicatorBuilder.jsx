import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Textarea } from "../../components/ui/textarea";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Switch } from "../../components/ui/switch";
import { Alert, AlertDescription } from "../../components/ui/alert";
import {
  Plus,
  Trash2,
  Save,
  Code,
  Calculator,
  Play,
  Loader2,
  AlertCircle,
  Copy,
  Edit,
  Eye,
  Globe,
  Lock,
  Sparkles,
  LineChart,
  Settings,
  HelpCircle,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "../../api/client";
import SEO from "../../components/SEO";

// Custom Indicator Builder Page - Phase 9 Retention Feature
export default function IndicatorBuilder() {
  const [indicators, setIndicators] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("library");
  const [editingIndicator, setEditingIndicator] = useState(null);
  const [saving, setSaving] = useState(false);

  // Form state for new/edit indicator
  const [formData, setFormData] = useState({
    name: "",
    mode: "formula",
    formula: "",
    jsCode: "",
    params: [],
    palette: { line: "#3B82F6", fill: "#93C5FD" },
    privacy: "private",
  });

  useEffect(() => {
    loadIndicators();
  }, []);

  const loadIndicators = async () => {
    setIsLoading(true);
    try {
      const { data } = await api.get("/indicators/");
      if (data?.success) {
        setIndicators(data.data || []);
      }
    } catch (error) {
      console.error("Failed to load indicators:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.error("Indicator name is required");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        name: formData.name,
        mode: formData.mode,
        formula: formData.formula,
        jsCode: formData.jsCode,
        params: formData.params,
        palette: formData.palette,
        privacy: formData.privacy,
      };

      let response;
      if (editingIndicator) {
        response = await api.put(`/indicators/${editingIndicator.id}/`, payload);
      } else {
        response = await api.post("/indicators/create/", payload);
      }

      if (response.data?.success) {
        toast.success(editingIndicator ? "Indicator updated!" : "Indicator created!");
        resetForm();
        loadIndicators();
        setActiveTab("library");
      } else {
        toast.error(response.data?.error || "Failed to save indicator");
      }
    } catch (error) {
      toast.error("Failed to save indicator");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this indicator?")) return;
    try {
      const response = await api.delete(`/indicators/${id}/`);
      if (response.data?.success) {
        toast.success("Indicator deleted");
        loadIndicators();
      }
    } catch {
      toast.error("Failed to delete indicator");
    }
  };

  const handleEdit = (indicator) => {
    setEditingIndicator(indicator);
    setFormData({
      name: indicator.name || "",
      mode: indicator.mode || "formula",
      formula: indicator.formula || "",
      jsCode: indicator.js_code || indicator.jsCode || "",
      params: indicator.params || [],
      palette: indicator.palette || { line: "#3B82F6", fill: "#93C5FD" },
      privacy: indicator.privacy || "private",
    });
    setActiveTab("builder");
  };

  const resetForm = () => {
    setEditingIndicator(null);
    setFormData({
      name: "",
      mode: "formula",
      formula: "",
      jsCode: "",
      params: [],
      palette: { line: "#3B82F6", fill: "#93C5FD" },
      privacy: "private",
    });
  };

  const addParam = () => {
    setFormData((prev) => ({
      ...prev,
      params: [...prev.params, { name: "", type: "number", default: 14 }],
    }));
  };

  const removeParam = (index) => {
    setFormData((prev) => ({
      ...prev,
      params: prev.params.filter((_, i) => i !== index),
    }));
  };

  const updateParam = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      params: prev.params.map((p, i) => (i === index ? { ...p, [field]: value } : p)),
    }));
  };

  // Formula helper examples
  const formulaExamples = [
    { name: "Simple Moving Average", formula: "SMA(close, 20)" },
    { name: "Exponential Moving Average", formula: "EMA(close, 12)" },
    { name: "RSI", formula: "RSI(close, 14)" },
    { name: "MACD Line", formula: "EMA(close, 12) - EMA(close, 26)" },
    { name: "Bollinger Upper", formula: "SMA(close, 20) + 2 * STDDEV(close, 20)" },
  ];

  return (
    <div className="container mx-auto px-4 py-6 max-w-6xl" data-testid="indicator-builder-page">
      <SEO
        title="Custom Indicator Builder | Trade Scan Pro"
        description="Create and manage custom technical indicators"
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg">
            <LineChart className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Custom Indicator Builder</h1>
            <p className="text-gray-500">Create your own technical indicators using formulas or JavaScript</p>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="library" className="gap-2">
              <Settings className="h-4 w-4" />
              My Indicators
            </TabsTrigger>
            <TabsTrigger value="builder" className="gap-2">
              <Sparkles className="h-4 w-4" />
              {editingIndicator ? "Edit Indicator" : "New Indicator"}
            </TabsTrigger>
          </TabsList>

          {activeTab === "library" && (
            <Button onClick={() => { resetForm(); setActiveTab("builder"); }} className="gap-2">
              <Plus className="h-4 w-4" />
              New Indicator
            </Button>
          )}
        </div>

        {/* Library Tab */}
        <TabsContent value="library" className="space-y-4">
          {isLoading ? (
            <Card className="p-12 text-center">
              <Loader2 className="h-12 w-12 mx-auto animate-spin text-blue-500 mb-4" />
              <p className="text-gray-500">Loading indicators...</p>
            </Card>
          ) : indicators.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {indicators.map((indicator) => (
                <Card key={indicator.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">{indicator.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {indicator.mode === "js" ? (
                              <><Code className="h-3 w-3 mr-1" /> JavaScript</>
                            ) : (
                              <><Calculator className="h-3 w-3 mr-1" /> Formula</>
                            )}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {indicator.privacy === "public" ? (
                              <><Globe className="h-3 w-3 mr-1" /> Public</>
                            ) : (
                              <><Lock className="h-3 w-3 mr-1" /> Private</>
                            )}
                          </Badge>
                        </div>
                      </div>
                      <span className="text-xs text-gray-400">v{indicator.version || 1}</span>
                    </div>

                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleEdit(indicator)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-500 hover:text-red-600"
                        onClick={() => handleDelete(indicator.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <LineChart className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Custom Indicators</h3>
              <p className="text-gray-500 mb-4">Create your first custom indicator to enhance your charts</p>
              <Button onClick={() => setActiveTab("builder")}>
                <Plus className="h-4 w-4 mr-2" />
                Create Indicator
              </Button>
            </Card>
          )}
        </TabsContent>

        {/* Builder Tab */}
        <TabsContent value="builder" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Main Form */}
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>{editingIndicator ? "Edit Indicator" : "Create New Indicator"}</CardTitle>
                  <CardDescription>Define your custom indicator using formula or JavaScript</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Name */}
                  <div className="space-y-2">
                    <Label htmlFor="name">Indicator Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
                      placeholder="e.g., My Custom RSI"
                    />
                  </div>

                  {/* Mode Selection */}
                  <div className="space-y-2">
                    <Label>Mode</Label>
                    <div className="flex gap-4">
                      <div
                        className={`flex-1 p-4 border rounded-lg cursor-pointer transition-colors ${
                          formData.mode === "formula" ? "border-blue-500 bg-blue-50" : "hover:border-gray-300"
                        }`}
                        onClick={() => setFormData((p) => ({ ...p, mode: "formula" }))}
                      >
                        <Calculator className="h-5 w-5 mb-2 text-blue-600" />
                        <p className="font-medium">Formula</p>
                        <p className="text-xs text-gray-500">Simple expression-based</p>
                      </div>
                      <div
                        className={`flex-1 p-4 border rounded-lg cursor-pointer transition-colors ${
                          formData.mode === "js" ? "border-blue-500 bg-blue-50" : "hover:border-gray-300"
                        }`}
                        onClick={() => setFormData((p) => ({ ...p, mode: "js" }))}
                      >
                        <Code className="h-5 w-5 mb-2 text-purple-600" />
                        <p className="font-medium">JavaScript</p>
                        <p className="text-xs text-gray-500">Full control with code</p>
                      </div>
                    </div>
                  </div>

                  {/* Formula/Code Input */}
                  {formData.mode === "formula" ? (
                    <div className="space-y-2">
                      <Label htmlFor="formula">Formula</Label>
                      <Textarea
                        id="formula"
                        value={formData.formula}
                        onChange={(e) => setFormData((p) => ({ ...p, formula: e.target.value }))}
                        placeholder="SMA(close, 20) + STDDEV(close, 20)"
                        rows={4}
                        className="font-mono text-sm"
                      />
                      <p className="text-xs text-gray-500">
                        Available functions: SMA, EMA, RSI, STDDEV, MAX, MIN, ABS
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Label htmlFor="jsCode">JavaScript Code</Label>
                      <Textarea
                        id="jsCode"
                        value={formData.jsCode}
                        onChange={(e) => setFormData((p) => ({ ...p, jsCode: e.target.value }))}
                        placeholder={`// Access: data (array of {open, high, low, close, volume})\n// Return: array of values\nfunction calculate(data, params) {\n  return data.map(d => d.close);\n}`}
                        rows={10}
                        className="font-mono text-sm"
                      />
                    </div>
                  )}

                  {/* Privacy */}
                  <div className="space-y-2">
                    <Label>Privacy</Label>
                    <Select
                      value={formData.privacy}
                      onValueChange={(v) => setFormData((p) => ({ ...p, privacy: v }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="private">Private - Only you can see</SelectItem>
                        <SelectItem value="unlisted">Unlisted - Anyone with link</SelectItem>
                        <SelectItem value="public">Public - Visible to everyone</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Colors */}
                  <div className="space-y-2">
                    <Label>Colors</Label>
                    <div className="flex gap-4">
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={formData.palette.line}
                          onChange={(e) => setFormData((p) => ({ ...p, palette: { ...p.palette, line: e.target.value } }))}
                          className="w-10 h-10 rounded cursor-pointer"
                        />
                        <span className="text-sm">Line</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={formData.palette.fill}
                          onChange={(e) => setFormData((p) => ({ ...p, palette: { ...p.palette, fill: e.target.value } }))}
                          className="w-10 h-10 rounded cursor-pointer"
                        />
                        <span className="text-sm">Fill</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3 pt-4">
                    <Button onClick={handleSave} disabled={saving} className="gap-2">
                      {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                      {saving ? "Saving..." : "Save Indicator"}
                    </Button>
                    {editingIndicator && (
                      <Button variant="outline" onClick={resetForm}>
                        Cancel
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar - Help & Examples */}
            <div className="space-y-6">
              {/* Formula Examples */}
              {formData.mode === "formula" && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <HelpCircle className="h-4 w-4" />
                      Formula Examples
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {formulaExamples.map((ex, i) => (
                      <div
                        key={i}
                        className="p-2 bg-gray-50 rounded text-sm cursor-pointer hover:bg-gray-100"
                        onClick={() => setFormData((p) => ({ ...p, formula: ex.formula }))}
                      >
                        <p className="font-medium text-gray-700">{ex.name}</p>
                        <code className="text-xs text-gray-500">{ex.formula}</code>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Parameters */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center justify-between">
                    Parameters
                    <Button variant="outline" size="sm" onClick={addParam}>
                      <Plus className="h-4 w-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {formData.params.length > 0 ? (
                    formData.params.map((param, index) => (
                      <div key={index} className="flex gap-2 items-end">
                        <div className="flex-1">
                          <Input
                            placeholder="Name"
                            value={param.name}
                            onChange={(e) => updateParam(index, "name", e.target.value)}
                          />
                        </div>
                        <div className="w-20">
                          <Input
                            type="number"
                            placeholder="Default"
                            value={param.default}
                            onChange={(e) => updateParam(index, "default", Number(e.target.value))}
                          />
                        </div>
                        <Button variant="ghost" size="icon" onClick={() => removeParam(index)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No parameters. Click + to add configurable parameters.
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
