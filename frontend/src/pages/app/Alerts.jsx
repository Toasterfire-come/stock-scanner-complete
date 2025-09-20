import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Badge } from "../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Plus, Bell, TrendingUp, TrendingDown, Trash2, Edit, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "../../context/SecureAuthContext";
import { alertsMeta, createAlert, api } from "../../api/client";

const Alerts = () => {
  const { isAuthenticated } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [newAlert, setNewAlert] = useState({
    ticker: "",
    targetPrice: "",
    condition: "above",
    email: ""
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      setAlerts([]);
      setIsLoading(false);
      return;
    }
    fetchAlerts();
  }, [isAuthenticated]);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      // Use the proper API client function with quota tracking
      const data = await api.get('/alerts/');
      const rows = Array.isArray(data?.data?.alerts) ? data.data.alerts : (Array.isArray(data?.data) ? data.data : []);
      setAlerts(rows);
    } catch (error) {
      toast.error("Failed to fetch alerts");
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const createAlertHandler = async () => {
    if (!isAuthenticated) {
      toast.error("Please sign in to create alerts");
      return;
    }
    if (!newAlert.ticker || !newAlert.targetPrice || !newAlert.email) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsCreating(true);
    try {
      // Use the proper API client function with quota tracking
      const response = await createAlert({
        ticker: newAlert.ticker.toUpperCase(),
        target_price: parseFloat(newAlert.targetPrice),
        condition: newAlert.condition,
        email: newAlert.email
      });

      if (response.alert_id || response.success) {
        toast.success("Alert created successfully");
        setNewAlert({ ticker: "", targetPrice: "", condition: "above", email: "" });
        fetchAlerts(); // Refresh the list
      } else {
        toast.error("Failed to create alert");
      }
    } catch (error) {
      const errorMessage = error.message || "Failed to create alert";
      toast.error(errorMessage);
    } finally {
      setIsCreating(false);
    }
  };

  const deleteAlert = async (alertId) => {
    if (!confirm("Are you sure you want to delete this alert?")) return;
    
    try {
      const resp = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/alerts/${encodeURIComponent(alertId)}/delete/`, { method: 'POST' });
      if (!resp.ok) throw new Error('delete failed');
      setAlerts((prev) => prev.filter(alert => alert.id !== alertId));
      toast.success("Alert deleted successfully");
    } catch (error) {
      toast.error("Failed to delete alert");
    }
  };

  const toggleAlert = async (alertId) => {
    if (!isAuthenticated) {
      toast.error("Please sign in to update alerts");
      return;
    }
    try {
      const resp = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/alerts/${encodeURIComponent(alertId)}/toggle/`, { method: 'POST' });
      if (!resp.ok) throw new Error('toggle failed');
      setAlerts((prev) => prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, isActive: !alert.isActive }
          : alert
      ));
      toast.success("Alert status updated");
    } catch (error) {
      toast.error("Failed to update alert");
    }
  };

  const getAlertStatus = (alert) => {
    if (alert.isTriggered) {
      return { label: "Triggered", color: "bg-red-100 text-red-800" };
    }
    if (alert.isActive) {
      return { label: "Active", color: "bg-green-100 text-green-800" };
    }
    return { label: "Inactive", color: "bg-gray-100 text-gray-800" };
  };

  const getConditionIcon = (condition) => {
    return condition === "above" ? (
      <TrendingUp className="h-4 w-4 text-green-600" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-600" />
    );
  };

  const formatPrice = (price) => `$${price.toFixed(2)}`;

  const activeAlerts = alerts.filter(alert => alert.isActive && !alert.isTriggered);
  const triggeredAlerts = alerts.filter(alert => alert.isTriggered);
  const inactiveAlerts = alerts.filter(alert => !alert.isActive);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Price Alerts</h1>
          <p className="text-gray-600 mt-2">Set up alerts to notify you when stocks reach target prices</p>
        </div>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Create New Alert
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-5 gap-4">
              <div>
                <Label htmlFor="ticker">Stock Ticker</Label>
                <Input
                  id="ticker"
                  placeholder="e.g., AAPL"
                  value={newAlert.ticker}
                  onChange={(e) => setNewAlert({...newAlert, ticker: e.target.value.toUpperCase()})}
                />
              </div>
              <div>
                <Label htmlFor="targetPrice">Target Price</Label>
                <Input
                  id="targetPrice"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={newAlert.targetPrice}
                  onChange={(e) => setNewAlert({...newAlert, targetPrice: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="condition">Condition</Label>
                <Select value={newAlert.condition} onValueChange={(value) => setNewAlert({...newAlert, condition: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="above">Above</SelectItem>
                    <SelectItem value="below">Below</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={newAlert.email}
                  onChange={(e) => setNewAlert({...newAlert, email: e.target.value})}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={createAlert} disabled={isCreating} className="w-full">
                  <Bell className="h-4 w-4 mr-2" />
                  Create Alert
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="active" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="active" className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Active ({activeAlerts.length})
            </TabsTrigger>
            <TabsTrigger value="triggered" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Triggered ({triggeredAlerts.length})
            </TabsTrigger>
            <TabsTrigger value="inactive" className="flex items-center gap-2">
              Inactive ({inactiveAlerts.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="active">
            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">Active Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                {activeAlerts.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticker</TableHead>
                        <TableHead>Current Price</TableHead>
                        <TableHead>Target Price</TableHead>
                        <TableHead>Condition</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {activeAlerts.map((alert) => {
                        const status = getAlertStatus(alert);
                        return (
                          <TableRow key={alert.id}>
                            <TableCell className="font-semibold">{alert.ticker}</TableCell>
                            <TableCell>{formatPrice(alert.currentPrice)}</TableCell>
                            <TableCell>{formatPrice(alert.targetPrice)}</TableCell>
                            <TableCell>
                              <div className="flex items-center gap-1">
                                {getConditionIcon(alert.condition)}
                                {alert.condition}
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge className={status.color}>{status.label}</Badge>
                            </TableCell>
                            <TableCell className="text-sm text-gray-600">
                              {new Date(alert.createdAt).toLocaleDateString()}
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <Button size="sm" variant="outline" onClick={() => toggleAlert(alert.id)}>
                                  Pause
                                </Button>
                                <Button size="sm" variant="destructive" onClick={() => deleteAlert(alert.id)}>
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-12">
                    <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <div className="text-gray-500 mb-2">No active alerts</div>
                    <div className="text-sm text-gray-400">Create an alert above to get started</div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="triggered">
            <Card>
              <CardHeader>
                <CardTitle className="text-red-600">Triggered Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                {triggeredAlerts.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticker</TableHead>
                        <TableHead>Target Price</TableHead>
                        <TableHead>Triggered Price</TableHead>
                        <TableHead>Condition</TableHead>
                        <TableHead>Triggered At</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {triggeredAlerts.map((alert) => (
                        <TableRow key={alert.id}>
                          <TableCell className="font-semibold">{alert.ticker}</TableCell>
                          <TableCell>{formatPrice(alert.targetPrice)}</TableCell>
                          <TableCell>{formatPrice(alert.currentPrice)}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              {getConditionIcon(alert.condition)}
                              {alert.condition}
                            </div>
                          </TableCell>
                          <TableCell className="text-sm">
                            {alert.triggeredAt ? new Date(alert.triggeredAt).toLocaleString() : 'N/A'}
                          </TableCell>
                          <TableCell>
                            <Button size="sm" variant="destructive" onClick={() => deleteAlert(alert.id)}>
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-12">
                    <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <div className="text-gray-500 mb-2">No triggered alerts</div>
                    <div className="text-sm text-gray-400">Alerts will appear here when they are triggered</div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="inactive">
            <Card>
              <CardHeader>
                <CardTitle className="text-gray-600">Inactive Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                {inactiveAlerts.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticker</TableHead>
                        <TableHead>Target Price</TableHead>
                        <TableHead>Condition</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {inactiveAlerts.map((alert) => (
                        <TableRow key={alert.id}>
                          <TableCell className="font-semibold">{alert.ticker}</TableCell>
                          <TableCell>{formatPrice(alert.targetPrice)}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              {getConditionIcon(alert.condition)}
                              {alert.condition}
                            </div>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {new Date(alert.createdAt).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button size="sm" variant="outline" onClick={() => toggleAlert(alert.id)}>
                                Activate
                              </Button>
                              <Button size="sm" variant="destructive" onClick={() => deleteAlert(alert.id)}>
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-gray-500 mb-2">No inactive alerts</div>
                    <div className="text-sm text-gray-400">Paused alerts will appear here</div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Card>
          <CardHeader>
            <CardTitle>Alert Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{alerts.length}</div>
                <div className="text-sm text-gray-600">Total Alerts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{activeAlerts.length}</div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{triggeredAlerts.length}</div>
                <div className="text-sm text-gray-600">Triggered</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">{inactiveAlerts.length}</div>
                <div className="text-sm text-gray-600">Inactive</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Alerts;