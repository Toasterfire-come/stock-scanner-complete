import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import { Badge } from "../../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../../components/ui/tabs";
import { X, Plus, Save, Play, Search, Info } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import logger from '../../../lib/logger';

// Prefer same-origin by default ("/api" is proxied in Docker/nginx and in dev via setupProxy.js)
const BACKEND_URL = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/$/, "");

const EnhancedCreateScreener = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [screenerData, setScreenerData] = useState({
    name: "",
    description: "",
  });
  
  const [filters, setFilters] = useState([]);
  const [availableFields, setAvailableFields] = useState({});
  const [fieldsByCategory, setFieldsByCategory] = useState({});
  const [operators, setOperators] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingFields, setIsLoadingFields] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("basic");
  const [presets, setPresets] = useState([]);

  // Load available fields and presets on mount
  useEffect(() => {
    loadFieldsAndPresets();
  }, []);

  const loadFieldsAndPresets = async () => {
    setIsLoadingFields(true);
    try {
      // Load available filter fields
      const fieldsRes = await axios.get(`${BACKEND_URL}/api/screener/fields/`);
      if (fieldsRes.data?.success) {
        setAvailableFields(fieldsRes.data.data.fields || {});
        setFieldsByCategory(fieldsRes.data.data.fields_by_category || {});
        setOperators(fieldsRes.data.data.operators || {});
      }

      // Load presets
      const presetsRes = await axios.get(`${BACKEND_URL}/api/screener/presets/`);
      if (presetsRes.data?.success) {
        setPresets(presetsRes.data.data.presets || []);
      }
    } catch (error) {
      logger.error('Failed to load screener fields:', error);
      toast.error('Failed to load screener configuration');
    } finally {
      setIsLoadingFields(false);
    }
  };

  const loadPreset = (preset) => {
    setScreenerData({
      name: preset.name,
      description: preset.description
    });
    setFilters(preset.filters || []);
    toast.success(`Loaded preset: ${preset.name}`);
  };

  const addFilter = (fieldKey) => {
    if (!fieldKey) return;
    
    const field = availableFields[fieldKey];
    if (!field) return;

    // Check if already added
    if (filters.some(f => f.field === fieldKey)) {
      toast.warning('This filter is already added');
      return;
    }

    const newFilter = {
      field: fieldKey,
      label: field.label,
      type: field.type,
      operator: field.type === 'number' ? 'gte' : 'eq',
      value: field.type === 'number' ? '' : ''
    };

    setFilters([...filters, newFilter]);
  };

  const removeFilter = (index) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const updateFilter = (index, key, value) => {
    const updated = [...filters];
    updated[index] = { ...updated[index], [key]: value };
    setFilters(updated);
  };

  const handleSave = async () => {
    if (!screenerData.name.trim()) {
      toast.error("Please enter a screener name");
      return;
    }

    if (filters.length === 0) {
      toast.error("Please add at least one filter");
      return;
    }

    setIsLoading(true);
    try {
      const payload = {
        name: screenerData.name,
        description: screenerData.description,
        criteria: filters.map(f => ({
          field: f.field,
          operator: f.operator,
          value: f.operator === 'between' ? [Number(f.value), Number(f.value2 || f.value)] : 
                 f.type === 'number' ? Number(f.value) : f.value
        }))
      };

      const response = await axios.post(`${BACKEND_URL}/api/screeners/create/`, payload);
      
      if (response.data?.success) {
        toast.success("Screener saved successfully");
        navigate("/app/screeners");
      } else {
        throw new Error('Failed to save');
      }
    } catch (error) {
      logger.error('Save error:', error);
      toast.error("Failed to save screener");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunScreener = async () => {
    if (filters.length === 0) {
      toast.error("Please add at least one filter");
      return;
    }

    setIsLoading(true);
    try {
      // Build filter payload for advanced filter API
      const payload = {
        filters: filters.map(f => ({
          field: f.field,
          operator: f.operator,
          value: f.operator === 'between' ? [Number(f.value), Number(f.value2 || f.value)] : 
                 availableFields[f.field]?.type === 'number' ? Number(f.value) : f.value
        })),
        page: 1,
        page_size: 50
      };

      const response = await axios.post(`${BACKEND_URL}/api/screener/filter/`, payload);
      
      if (response.data?.success) {
        // Store results and navigate
        sessionStorage.setItem('screener_results', JSON.stringify(response.data.data));
        sessionStorage.setItem('screener_filters', JSON.stringify(filters));
        toast.success(`Found ${response.data.data.results?.length || 0} stocks`);
        navigate('/app/screeners/results');
      } else {
        throw new Error('Failed to run screener');
      }
    } catch (error) {
      logger.error('Run error:', error);
      toast.error("Failed to run screener");
    } finally {
      setIsLoading(false);
    }
  };

  const getOperatorLabel = (op) => {
    const labels = {
      eq: 'Equals',
      ne: 'Not Equals',
      gt: 'Greater Than',
      gte: 'Greater Than or Equal',
      lt: 'Less Than',
      lte: 'Less Than or Equal',
      between: 'Between',
      contains: 'Contains',
      startswith: 'Starts With',
      endswith: 'Ends With',
      in: 'In List',
      isnull: 'Is Null'
    };
    return labels[op] || op;
  };

  const getCategoryIcon = (category) => {
    const icons = {
      basic: '📊',
      valuation: '💰',
      profitability: '📈',
      growth: '🚀',
      financial_health: '🏥',
      cash_flow: '💵',
      dividend: '💎',
      fair_value: '⚖️',
      scores: '⭐',
      classification: '🏷️'
    };
    return icons[category] || '📁';
  };

  const getCategoryLabel = (category) => {
    const labels = {
      basic: 'Basic Metrics',
      valuation: 'Valuation',
      profitability: 'Profitability',
      growth: 'Growth',
      financial_health: 'Financial Health',
      cash_flow: 'Cash Flow',
      dividend: 'Dividends',
      fair_value: 'Fair Value',
      scores: 'Scores & Ratings',
      classification: 'Classification'
    };
    return labels[category] || category;
  };

  const getFilteredFieldsByCategory = (category) => {
    const fields = fieldsByCategory[category] || [];
    if (!searchTerm) return fields;
    return fields.filter(f => 
      f.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.key.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  if (isLoadingFields) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading screener configuration...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Advanced Screener</h1>
            <p className="text-gray-600 mt-2">Filter stocks using 57+ fundamental and technical criteria</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleRunScreener} disabled={isLoading}>
              <Play className="h-4 w-4 mr-2" />
              Run Screener
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              Save Screener
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
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
                    placeholder="e.g., Undervalued Growth Stocks"
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

            {/* Active Filters */}
            <Card>
              <CardHeader>
                <CardTitle>Active Filters ({filters.length})</CardTitle>
                <CardDescription>
                  {filters.length === 0 ? 'No filters added yet. Select fields from the sidebar to add filters.' : 'Configure your filter values'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {filters.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Info className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Start by adding filters from the Available Fields panel →</p>
                  </div>
                ) : (
                  filters.map((filter, index) => (
                    <div key={index} className="border rounded-lg p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium text-gray-900">{filter.label}</h4>
                          <Badge variant="outline" className="mt-1">{filter.field}</Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFilter(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>

                      <div className="grid gap-3">
                        {/* Operator Selection */}
                        <div>
                          <Label>Operator</Label>
                          <Select
                            value={filter.operator}
                            onValueChange={(value) => updateFilter(index, 'operator', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {(operators[filter.type] || []).map(op => (
                                <SelectItem key={op} value={op}>
                                  {getOperatorLabel(op)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        {/* Value Input */}
                        {filter.operator !== 'isnull' && (
                          <div>
                            <Label>Value</Label>
                            {filter.operator === 'between' ? (
                              <div className="flex gap-2">
                                <Input
                                  type={filter.type === 'number' ? 'number' : 'text'}
                                  value={filter.value}
                                  onChange={(e) => updateFilter(index, 'value', e.target.value)}
                                  placeholder="Min"
                                />
                                <Input
                                  type={filter.type === 'number' ? 'number' : 'text'}
                                  value={filter.value2 || ''}
                                  onChange={(e) => updateFilter(index, 'value2', e.target.value)}
                                  placeholder="Max"
                                />
                              </div>
                            ) : filter.operator === 'in' ? (
                              <Input
                                value={filter.value}
                                onChange={(e) => updateFilter(index, 'value', e.target.value)}
                                placeholder="Enter comma-separated values"
                              />
                            ) : (
                              <Input
                                type={filter.type === 'number' ? 'number' : 'text'}
                                value={filter.value}
                                onChange={(e) => updateFilter(index, 'value', e.target.value)}
                                placeholder="Enter value"
                                step={filter.type === 'number' ? 'any' : undefined}
                              />
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Presets */}
            {presets.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Presets</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {presets.map((preset) => (
                    <Button
                      key={preset.id}
                      variant="outline"
                      className="w-full justify-start text-left h-auto py-2"
                      onClick={() => loadPreset(preset)}
                    >
                      <div className="flex-1">
                        <div className="font-medium text-sm">{preset.name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{preset.description}</div>
                      </div>
                    </Button>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Available Fields */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Available Fields</CardTitle>
                <div className="mt-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search fields..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
                  <TabsList className="grid grid-cols-2 gap-1 h-auto">
                    {Object.keys(fieldsByCategory).slice(0, 10).map(category => (
                      <TabsTrigger 
                        key={category} 
                        value={category}
                        className="text-xs py-1.5"
                      >
                        <span className="mr-1">{getCategoryIcon(category)}</span>
                        {getCategoryLabel(category).split(' ')[0]}
                      </TabsTrigger>
                    ))}
                  </TabsList>

                  {Object.keys(fieldsByCategory).map(category => (
                    <TabsContent key={category} value={category} className="mt-4 space-y-1 max-h-96 overflow-y-auto">
                      {getFilteredFieldsByCategory(category).map(field => (
                        <Button
                          key={field.key}
                          variant="ghost"
                          size="sm"
                          className="w-full justify-start text-left h-auto py-2"
                          onClick={() => addFilter(field.key)}
                          disabled={filters.some(f => f.field === field.key)}
                        >
                          <Plus className="h-3 w-3 mr-2 flex-shrink-0" />
                          <div className="flex-1 overflow-hidden">
                            <div className="text-sm truncate">{field.label}</div>
                            <div className="text-xs text-gray-500">{field.type}</div>
                          </div>
                        </Button>
                      ))}
                      {getFilteredFieldsByCategory(category).length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">No fields found</p>
                      )}
                    </TabsContent>
                  ))}
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedCreateScreener;
