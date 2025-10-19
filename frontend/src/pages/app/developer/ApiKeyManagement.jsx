import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Badge } from '../../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Copy, Eye, EyeOff, Key, Plus, Trash2, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { getApiKeys, createApiKey, deleteApiKey } from '../../../api/client';
import { toast } from 'sonner';

const ApiKeyManagement = () => {
  const { user } = useAuth();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedKey, setSelectedKey] = useState(null);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState(null);
  const [showCreatedKey, setShowCreatedKey] = useState(false);
  const [visibleKeys, setVisibleKeys] = useState(new Set());

  // Check if user has Gold plan
  const hasGoldPlan = user?.plan === 'gold';

  useEffect(() => {
    if (hasGoldPlan) {
      loadApiKeys();
    } else {
      setLoading(false);
    }
  }, [hasGoldPlan]);

  const loadApiKeys = async () => {
    try {
      const response = await getApiKeys();
      if (response.success) {
        setApiKeys(response.data || []);
      } else {
        toast.error('Failed to load API keys');
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
      toast.error('Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a name for the API key');
      return;
    }

    try {
      const response = await createApiKey({ name: newKeyName.trim() });
      if (response.success) {
        setCreatedKey(response);
        setShowCreatedKey(true);
        setShowCreateDialog(false);
        setNewKeyName('');
        await loadApiKeys();
        toast.success('API key created successfully');
      } else {
        toast.error(response.message || 'Failed to create API key');
      }
    } catch (error) {
      console.error('Failed to create API key:', error);
      toast.error('Failed to create API key');
    }
  };

  const handleDeleteKey = async () => {
    if (!selectedKey) return;

    try {
      const response = await deleteApiKey(selectedKey.id);
      if (response.success) {
        await loadApiKeys();
        setShowDeleteDialog(false);
        setSelectedKey(null);
        toast.success('API key deleted successfully');
      } else {
        toast.error('Failed to delete API key');
      }
    } catch (error) {
      console.error('Failed to delete API key:', error);
      toast.error('Failed to delete API key');
    }
  };

  const toggleKeyVisibility = (keyId) => {
    const newVisible = new Set(visibleKeys);
    if (newVisible.has(keyId)) {
      newVisible.delete(keyId);
    } else {
      newVisible.add(keyId);
    }
    setVisibleKeys(newVisible);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const formatKey = (key, isVisible) => {
    if (isVisible) return key;
    return key.substring(0, 8) + '••••••••••••••••' + key.substring(key.length - 4);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!hasGoldPlan) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">API Key Management</h1>
            <p className="text-gray-600">Manage your API keys for programmatic access</p>
          </div>

          <Alert className="border-amber-200 bg-amber-50">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <AlertDescription className="text-amber-800">
              <div className="font-semibold mb-2">Gold Plan Required</div>
              <p className="mb-4">
                API key management is available exclusively for Gold plan subscribers. Upgrade your plan to access programmatic API features.
              </p>
              <Button asChild className="bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-700 hover:to-yellow-700">
                <a href="/account/plan" rel="noopener noreferrer">Upgrade to Gold Plan</a>
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading API keys...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">API Key Management</h1>
              <p className="text-gray-600">Manage your API keys for programmatic access</p>
            </div>
            <Button onClick={() => setShowCreateDialog(true)} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              Create API Key
            </Button>
          </div>
        </div>

        {/* API Keys List */}
        <div className="space-y-4">
          {apiKeys.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No API Keys Yet</h3>
                <p className="text-gray-600 mb-4">Create your first API key to start using our programmatic interface.</p>
                <Button onClick={() => setShowCreateDialog(true)} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Create API Key
                </Button>
              </CardContent>
            </Card>
          ) : (
            apiKeys.map((key) => (
              <Card key={key.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{key.name}</h3>
                        <Badge variant={key.is_active ? "default" : "secondary"}>
                          {key.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      
                      <div className="font-mono text-sm bg-gray-100 rounded px-3 py-2 mb-3 flex items-center justify-between">
                        <span className="text-gray-700">
                          {formatKey(key.key, visibleKeys.has(key.id))}
                        </span>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => toggleKeyVisibility(key.id)}
                            className="h-6 w-6 p-0"
                          >
                            {visibleKeys.has(key.id) ? (
                              <EyeOff className="h-3 w-3" />
                            ) : (
                              <Eye className="h-3 w-3" />
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => copyToClipboard(key.key)}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>

                      <div className="text-sm text-gray-600 space-y-1">
                        <p>Created: {formatDate(key.created_at)}</p>
                        {key.last_used ? (
                          <p>Last used: {formatDate(key.last_used)}</p>
                        ) : (
                          <p>Never used</p>
                        )}
                      </div>
                    </div>

                    <div className="ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedKey(key);
                          setShowDeleteDialog(true);
                        }}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Usage Information */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>API Usage Guidelines</CardTitle>
            <CardDescription>Important information about using your API keys</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Rate Limits</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Gold Plan: Unlimited API calls</li>
                  <li>• Real-time data access included</li>
                  <li>• No throttling for Gold subscribers</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Security Best Practices</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Never share your API keys publicly</li>
                  <li>• Rotate keys regularly</li>
                  <li>• Use environment variables in your code</li>
                  <li>• Monitor usage for suspicious activity</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Create API Key Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New API Key</DialogTitle>
              <DialogDescription>
                Create a new API key for programmatic access to Trade Scan Pro data.
              </DialogDescription>
            </DialogHeader>
            
            <div className="py-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key Name
              </label>
              <Input
                placeholder="e.g., Production App, Mobile Client"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreateKey()}
              />
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateKey} className="bg-blue-600 hover:bg-blue-700">
                Create API Key
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Show Created Key Dialog */}
        <Dialog open={showCreatedKey} onOpenChange={setShowCreatedKey}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                API Key Created Successfully
              </DialogTitle>
              <DialogDescription>
                Your new API key has been created. Please copy it now as it won't be shown again.
              </DialogDescription>
            </DialogHeader>
            
            {createdKey && (
              <div className="py-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your API Key
                </label>
                <div className="font-mono text-sm bg-gray-100 rounded px-3 py-2 flex items-center justify-between">
                  <span className="text-gray-700 break-all">{createdKey.key}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => copyToClipboard(createdKey.key)}
                    className="ml-2"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Store this key securely. You won't be able to see the full key again.
                </p>
              </div>
            )}

            <DialogFooter>
              <Button onClick={() => setShowCreatedKey(false)} className="bg-blue-600 hover:bg-blue-700">
                I've Copied the Key
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
                Delete API Key
              </DialogTitle>
              <DialogDescription>
                Are you sure you want to delete this API key? This action cannot be undone and will immediately revoke access for any applications using this key.
              </DialogDescription>
            </DialogHeader>
            
            {selectedKey && (
              <div className="py-4">
                <div className="bg-gray-50 rounded p-3">
                  <p className="font-semibold text-gray-900">{selectedKey.name}</p>
                  <p className="text-sm text-gray-600 font-mono">{formatKey(selectedKey.key, false)}</p>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleDeleteKey} 
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                Delete API Key
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default ApiKeyManagement;