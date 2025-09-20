import React, { useState, useEffect } from "react";
import { api } from "../../api/client";
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

const Alerts = () => {
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
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const { data } = await api.get('/alerts/');
      setAlerts(Array.isArray(data) ? data : (data?.alerts || []));
    } catch (error) {
      toast.error("Failed to fetch alerts");
    } finally {
      setIsLoading(false);
    }
  };

  const createAlert = async () => {
    if (!newAlert.ticker || !newAlert.targetPrice || !newAlert.email) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsCreating(true);
    try {
      const { data } = await api.post('/alerts/create/', {
        ticker: newAlert.ticker.toUpperCase(),
        target_price: parseFloat(newAlert.targetPrice),
        condition: newAlert.condition,
        email: newAlert.email
      });
      if (data?.alert_id || data?.success) {
        toast.success("Alert created successfully");
        setNewAlert({ ticker: "", targetPrice: "", condition: "above", email: "" });
        fetchAlerts();
      } else {
        toast.error(data?.message || "Failed to create alert");
      }
    } catch (error) {
      toast.error("Failed to create alert");
    } finally {
      setIsCreating(false);
    }
  };

  const deleteAlert = async (alertId) => {
    if (!confirm("Are you sure you want to delete this alert?")) return;
    
    try {
      await api.delete(`/alerts/${alertId}/`);
      setAlerts(alerts.filter(alert => alert.id !== alertId));
      toast.success("Alert deleted successfully");
    } catch (error) {
      toast.error("Failed to delete alert");
    }
  };

  const toggleAlert = async (alertId) => {
    try {
      await api.post(`/alerts/${alertId}/toggle/`);
      setAlerts(alerts.map(alert => 
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
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Alerts</h1>
      <div className="table-responsive">
        {/* alerts list */}
      </div>
    </div>
  );
};

export default Alerts;