import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Play, 
  Edit, 
  Trash2, 
  Copy,
  Save,
  Settings,
  BarChart3,
  Target
} from 'lucide-react';
import { 
  getScreeners, 
  createScreener, 
  updateScreener, 
  deleteScreener, 
  runScreener,
  getScreenerTemplates,
  filterStocks,
  exportStocksCSV
} from '../api/client';
import { Link, useNavigate } from 'react-router-dom';

const AdvancedScreenerInterface = () => {
  const [screeners, setScreeners] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingScreener, setEditingScreener] = useState(null);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  // Screener creation form state
  const [newScreener, setNewScreener] = useState({
    name: '',
    description: '',
    criteria: [],
    is_public: false
  });

  useEffect(() => {
    fetchScreenerData();
  }, []);

  const fetchScreenerData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [screenersRes, templatesRes] = await Promise.all([
        getScreeners().catch(() => ({ data: [] })),
        getScreenerTemplates().catch(() => ({ data: [] }))
      ]);

      setScreeners(Array.isArray(screenersRes.data) ? screenersRes.data : []);
      setTemplates(Array.isArray(templatesRes.data) ? templatesRes.data : []);
    } catch (err) {
      setError('Failed to load screener data');
      console.error('Screener data error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateScreener = async () => {
    if (!newScreener.name.trim()) {
      setError('Screener name is required');
      return;
    }

    try {
      const result = await createScreener(newScreener);
      if (result.success) {
        await fetchScreenerData();
        setShowCreateForm(false);
        setNewScreener({ name: '', description: '', criteria: [], is_public: false });
        setError(null);
      }
    } catch (err) {
      setError('Failed to create screener');
      console.error('Create screener error:', err);
    }
  };

  const handleRunScreener = async (screenerId) => {
    try {
      // Kick off run in background, then navigate to detail which auto-runs
      runScreener(screenerId).catch(() => {});
      navigate(`/app/screeners/${screenerId}`);
    } catch (err) {
      setError('Failed to run screener');
      console.error('Run screener error:', err);
    }
  };

  const handleDeleteScreener = async (screenerId) => {
    if (!window.confirm('Are you sure you want to delete this screener?')) return;

    try {
      const result = await deleteScreener(screenerId);
      if (result.success) {
        await fetchScreenerData();
        setError(null);
      }
    } catch (err) {
      setError('Failed to delete screener');
      console.error('Delete screener error:', err);
    }
  };

  const handleDuplicateScreener = async (screener) => {
    const duplicated = {
      name: `${screener.name} (Copy)`,
      description: screener.description,
      criteria: screener.criteria,
      is_public: false
    };

    try {
      const result = await createScreener(duplicated);
      if (result.success) {
        await fetchScreenerData();
        setError(null);
      }
    } catch (err) {
      setError('Failed to duplicate screener');
      console.error('Duplicate screener error:', err);
    }
  };

  const handleExportResults = async (screenerId) => {
    try {
      const csvData = await exportStocksCSV({ screener_id: screenerId });
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screener-results-${screenerId}-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export results');
      console.error('Export error:', err);
    }
  };

  const addCriterion = () => {
    setNewScreener(prev => ({
      ...prev,
      criteria: [...prev.criteria, { id: 'market_cap', min: '', max: '' }]
    }));
  };

  const updateCriterion = (index, field, value) => {
    setNewScreener(prev => ({
      ...prev,
      criteria: prev.criteria.map((criterion, i) => 
        i === index ? { ...criterion, [field]: value } : criterion
      )
    }));
  };

  const removeCriterion = (index) => {
    setNewScreener(prev => ({
      ...prev,
      criteria: prev.criteria.filter((_, i) => i !== index)
    }));
  };

  const filteredScreeners = screeners.filter(screener =>
    screener.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    screener.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const criteriaOptions = [
    { value: 'market_cap', label: 'Market Cap', type: 'range' },
    { value: 'price', label: 'Stock Price', type: 'range' },
    { value: 'volume', label: 'Volume', type: 'range' },
    { value: 'pe_ratio', label: 'P/E Ratio', type: 'range' },
    { value: 'dividend_yield', label: 'Dividend Yield', type: 'range' },
    { value: 'change_percent', label: 'Price Change %', type: 'range' },
    { value: 'exchange', label: 'Exchange', type: 'select' }
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading screeners...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock Screeners</h1>
          <p className="text-gray-600">Create and manage custom stock screening criteria</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Screener
          </Button>
        </div>
      </div>

      {error && (
        <Alert>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Search and Filter */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search screeners..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Templates Section */}
      {templates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Screener Templates</CardTitle>
            <CardDescription>Pre-built screening strategies to get you started</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((template) => (
                <div key={template.id} className="p-4 border rounded-lg hover:bg-gray-50">
                  <h4 className="font-semibold mb-2">{template.name}</h4>
                  <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                  <Button size="sm" variant="outline" className="w-full">
                    Use Template
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Screener Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Screener</CardTitle>
            <CardDescription>Define your custom stock screening criteria</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Screener Name</label>
              <Input
                placeholder="Enter screener name..."
                value={newScreener.name}
                onChange={(e) => setNewScreener(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description (Optional)</label>
              <Textarea
                placeholder="Describe your screening strategy..."
                value={newScreener.description}
                onChange={(e) => setNewScreener(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Screening Criteria</label>
              <div className="space-y-3">
                {newScreener.criteria.map((criterion, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <select
                      value={criterion.id}
                      onChange={(e) => updateCriterion(index, 'id', e.target.value)}
                      className="px-3 py-2 border rounded-md"
                    >
                      {criteriaOptions.map(option => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                    
                    {criteriaOptions.find(opt => opt.value === criterion.id)?.type === 'range' ? (
                      <>
                        <Input
                          placeholder="Min"
                          value={criterion.min}
                          onChange={(e) => updateCriterion(index, 'min', e.target.value)}
                          className="w-24"
                        />
                        <span className="text-gray-500">to</span>
                        <Input
                          placeholder="Max"
                          value={criterion.max}
                          onChange={(e) => updateCriterion(index, 'max', e.target.value)}
                          className="w-24"
                        />
                      </>
                    ) : (
                      <Input
                        placeholder="Value"
                        value={criterion.value || ''}
                        onChange={(e) => updateCriterion(index, 'value', e.target.value)}
                        className="w-32"
                      />
                    )}
                    
                    <Button variant="ghost" size="sm" onClick={() => removeCriterion(index)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button variant="outline" onClick={addCriterion}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Criterion
                </Button>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={newScreener.is_public}
                  onChange={(e) => setNewScreener(prev => ({ ...prev, is_public: e.target.checked }))}
                />
                <span className="text-sm">Make this screener public</span>
              </label>
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleCreateScreener}>
                <Save className="h-4 w-4 mr-2" />
                Create Screener
              </Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Screeners List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredScreeners.map((screener) => (
          <Card key={screener.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{screener.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {screener.description || 'No description provided'}
                  </CardDescription>
                </div>
                <div className="flex gap-1">
                  {screener.is_public && (
                    <Badge variant="secondary">Public</Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-3">
                {/* Criteria Preview */}
                {screener.criteria && screener.criteria.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Criteria:</h4>
                    <div className="flex flex-wrap gap-1">
                      {screener.criteria.slice(0, 3).map((criterion, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {criteriaOptions.find(opt => opt.value === criterion.id)?.label || criterion.id}
                        </Badge>
                      ))}
                      {screener.criteria.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{screener.criteria.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {/* Last Run Info */}
                {screener.last_run && (
                  <div className="text-xs text-gray-500">
                    Last run: {new Date(screener.last_run).toLocaleDateString()}
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-2">
                  <Button 
                    size="sm" 
                    onClick={() => handleRunScreener(screener.id)}
                    className="flex-1"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Run
                  </Button>
                  
                  <Button variant="outline" size="sm" asChild>
                    <Link to={`/app/screeners/${screener.id}/edit`}>
                      <Edit className="h-4 w-4" />
                    </Link>
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleDuplicateScreener(screener)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleExportResults(screener.id)}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleDeleteScreener(screener.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredScreeners.length === 0 && !isLoading && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Target className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No screeners found</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm ? 'No screeners match your search.' : 'Create your first stock screener to get started.'}
              </p>
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Screener
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdvancedScreenerInterface;