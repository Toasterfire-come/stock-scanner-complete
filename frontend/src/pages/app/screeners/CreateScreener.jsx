import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Textarea } from "../../../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Checkbox } from "../../../components/ui/checkbox";
import { Badge } from "../../../components/ui/badge";
import { Separator } from "../../../components/ui/separator";
import { toast } from "sonner";
import { 
  Save, 
  Play, 
  Plus, 
  X, 
  TrendingUp, 
  DollarSign, 
  BarChart3, 
  Volume2,
  Target,
  Zap,
  ArrowLeft
} from "lucide-react";

const screenerSchema = z.object({
  name: z.string().min(1, "Name is required").max(100, "Name too long"),
  description: z.string().max(500, "Description too long"),
  category: z.string().min(1, "Category is required"),
});

const CreateScreener = () => {
  const [isSaving, setIsSaving] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [criteria, setCriteria] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(screenerSchema),
    defaultValues: {
      name: "",
      description: "",
      category: "",
    }
  });

  const watchCategory = watch("category");

  const availableCriteria = [
    {
      id: "market_cap",
      name: "Market Cap",
      icon: <BarChart3 className="h-4 w-4" />,
      type: "range",
      options: ["Any", "Micro (<$300M)", "Small ($300M-$2B)", "Mid ($2B-$10B)", "Large (>$10B)"]
    },
    {
      id: "price",
      name: "Stock Price",
      icon: <DollarSign className="h-4 w-4" />,
      type: "range",
      min: 0,
      max: 1000,
      step: 0.01
    },
    {
      id: "volume",
      name: "Volume",
      icon: <Volume2 className="h-4 w-4" />,
      type: "range",
      options: ["Any", ">100K", ">500K", ">1M", ">5M"]
    },
    {
      id: "pe_ratio",
      name: "P/E Ratio",
      icon: <Target className="h-4 w-4" />,
      type: "range",
      min: 0,
      max: 100,
      step: 0.1
    },
    {
      id: "price_change",
      name: "Price Change %",
      icon: <TrendingUp className="h-4 w-4" />,
      type: "range",
      min: -50,
      max: 50,
      step: 0.1
    },
    {
      id: "dividend_yield",
      name: "Dividend Yield",
      icon: <Zap className="h-4 w-4" />,
      type: "range",
      min: 0,
      max: 20,
      step: 0.1
    }
  ];

  const categories = [
    { value: "growth", label: "Growth" },
    { value: "value", label: "Value" },
    { value: "momentum", label: "Momentum" },
    { value: "quality", label: "Quality" },
    { value: "dividend", label: "Dividend" },
    { value: "custom", label: "Custom" }
  ];

  const predefinedTags = [
    "tech", "healthcare", "finance", "energy", "consumer", "industrial",
    "small-cap", "mid-cap", "large-cap", "growth", "value", "momentum",
    "dividend", "high-volume", "breakout", "oversold", "undervalued"
  ];

  const addCriterion = (criterionId) => {
    const criterion = availableCriteria.find(c => c.id === criterionId);
    if (criterion && !criteria.find(c => c.id === criterionId)) {
      setCriteria(prev => [...prev, {
        id: criterion.id,
        name: criterion.name,
        type: criterion.type,
        operator: ">=",
        value: criterion.type === "range" ? { min: "", max: "" } : "",
        selected_option: criterion.options ? criterion.options[0] : null
      }]);
    }
  };

  const removeCriterion = (criterionId) => {
    setCriteria(prev => prev.filter(c => c.id !== criterionId));
  };

  const updateCriterion = (criterionId, field, value) => {
    setCriteria(prev => prev.map(c => 
      c.id === criterionId ? { ...c, [field]: value } : c
    ));
  };

  const toggleTag = (tag) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const onSubmit = async (data) => {
    if (criteria.length === 0) {
      toast.error("Please add at least one screening criterion");
      return;
    }

    setIsSaving(true);
    try {
      // Mock save screener
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const screenerId = "new_" + Date.now();
      toast.success("Screener created successfully");
      navigate(`/app/screeners/${screenerId}/results`);
    } catch (error) {
      toast.error("Failed to create screener");
    } finally {
      setIsSaving(false);
    }
  };

  const runScreener = async () => {
    const form = document.querySelector('form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    if (!data.name || !data.category || criteria.length === 0) {
      toast.error("Please fill in all required fields and add criteria");
      return;
    }

    setIsRunning(true);
    try {
      // Mock run screener
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success("Screener executed! Found 23 matching stocks");
      navigate('/app/screeners/preview/results');
    } catch (error) {
      toast.error("Failed to run screener");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create New Screener</h1>
            <p className="text-gray-600 mt-2">
              Define criteria to find stocks that match your investment strategy
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>
                Give your screener a name and description
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Screener Name *</Label>
                  <Input
                    id="name"
                    placeholder="e.g., High Growth Tech Stocks"
                    {...register("name")}
                  />
                  {errors.name && (
                    <p className="text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Category *</Label>
                  <Select 
                    value={watchCategory} 
                    onValueChange={(value) => setValue("category", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.value} value={category.value}>
                          {category.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.category && (
                    <p className="text-sm text-red-600">{errors.category.message}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this screener looks for..."
                  rows={3}
                  {...register("description")}
                />
                {errors.description && (
                  <p className="text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>

              {/* Tags */}
              <div className="space-y-2">
                <Label>Tags (Optional)</Label>
                <div className="flex flex-wrap gap-2">
                  {predefinedTags.map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => toggleTag(tag)}
                      className={`px-3 py-1 text-sm border rounded-full transition-colors ${
                        selectedTags.includes(tag)
                          ? 'bg-blue-100 border-blue-300 text-blue-800'
                          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Screening Criteria */}
          <Card>
            <CardHeader>
              <CardTitle>Screening Criteria</CardTitle>
              <CardDescription>
                Add criteria to filter stocks based on your requirements
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Criterion Buttons */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {availableCriteria.map((criterion) => (
                  <Button
                    key={criterion.id}
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => addCriterion(criterion.id)}
                    disabled={criteria.some(c => c.id === criterion.id)}
                    className="justify-start"
                  >
                    {criterion.icon}
                    <span className="ml-2">{criterion.name}</span>
                    {criteria.some(c => c.id === criterion.id) && (
                      <span className="ml-auto text-green-600">✓</span>
                    )}
                  </Button>
                ))}
              </div>

              {criteria.length > 0 && <Separator />}

              {/* Active Criteria */}
              <div className="space-y-4">
                {criteria.map((criterion) => {
                  const template = availableCriteria.find(c => c.id === criterion.id);
                  return (
                    <div key={criterion.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          {template.icon}
                          <span className="font-medium">{criterion.name}</span>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeCriterion(criterion.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>

                      {template.options ? (
                        <Select
                          value={criterion.selected_option}
                          onValueChange={(value) => updateCriterion(criterion.id, 'selected_option', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {template.options.map((option) => (
                              <SelectItem key={option} value={option}>
                                {option}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <div className="grid grid-cols-3 gap-2">
                          <Select
                            value={criterion.operator}
                            onValueChange={(value) => updateCriterion(criterion.id, 'operator', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value=">=">&gt;=</SelectItem>
                              <SelectItem value="<=">&lt;=</SelectItem>
                              <SelectItem value="between">Between</SelectItem>
                            </SelectContent>
                          </Select>

                          {criterion.operator === "between" ? (
                            <>
                              <Input
                                type="number"
                                placeholder="Min"
                                step={template.step}
                                value={criterion.value.min}
                                onChange={(e) => updateCriterion(criterion.id, 'value', {
                                  ...criterion.value,
                                  min: e.target.value
                                })}
                              />
                              <Input
                                type="number"
                                placeholder="Max"
                                step={template.step}
                                value={criterion.value.max}
                                onChange={(e) => updateCriterion(criterion.id, 'value', {
                                  ...criterion.value,
                                  max: e.target.value
                                })}
                              />
                            </>
                          ) : (
                            <Input
                              type="number"
                              placeholder="Value"
                              step={template.step}
                              value={criterion.value}
                              onChange={(e) => updateCriterion(criterion.id, 'value', e.target.value)}
                              className="col-span-2"
                            />
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {criteria.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Add screening criteria above to filter stocks</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/app/screeners')}
            >
              Cancel
            </Button>

            <div className="flex space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={runScreener}
                disabled={isRunning}
              >
                {isRunning ? (
                  "Running..."
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Test Run
                  </>
                )}
              </Button>

              <Button type="submit" disabled={isSaving}>
                {isSaving ? (
                  "Saving..."
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Screener
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateScreener;