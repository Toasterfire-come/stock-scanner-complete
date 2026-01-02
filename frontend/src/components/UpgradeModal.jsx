/**
 * UpgradeModal Component
 *
 * Displays when users hit quota limits, showing:
 * - Current plan and usage
 * - Limit reached
 * - Upgrade options
 * - Clear CTAs
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import {
  AlertTriangle,
  TrendingUp,
  Zap,
  Crown,
  Award,
  ArrowRight,
  X
} from "lucide-react";

const UpgradeModal = ({
  isOpen,
  onClose,
  currentPlan = "basic",
  resourceType = "api_calls",
  currentUsage = 0,
  quotaLimit = 0,
  usagePercentage = 100
}) => {
  const navigate = useNavigate();

  // Resource type display names
  const resourceNames = {
    api_calls: "API Calls",
    screener_runs: "Screener Runs",
    chart_exports: "Chart Exports",
    ai_backtests: "AI Backtests",
    watchlists: "Watchlists",
    portfolios: "Portfolios",
    alerts: "Alerts"
  };

  const resourceName = resourceNames[resourceType] || resourceType;

  // Upgrade options based on current plan
  const getUpgradeOptions = () => {
    if (currentPlan === "basic" || currentPlan === "free") {
      return [
        {
          id: "pro",
          name: "Pro",
          icon: <Crown className="h-6 w-6" />,
          price: "$24.99/month",
          color: "blue",
          description: "10,000 API calls/month + all premium features",
          recommended: true,
          benefits: [
            "10,000 API calls/month (4x more)",
            "500 screener runs/month",
            "150 active alerts",
            "AI backtesting & strategy scoring",
            "TradingView Premium charting",
            "Options analytics (Greeks, IV surfaces)"
          ]
        },
        {
          id: "pay-per-use",
          name: "Pay-Per-Use",
          icon: <Zap className="h-6 w-6" />,
          price: "$24.99/month + usage",
          color: "purple",
          description: "Same base as Pro + transparent overage pricing",
          recommended: false,
          benefits: [
            "10,000 API calls base allocation",
            "Overage: $1 per 1,000 additional calls",
            "Hard cap: $124.99/month maximum",
            "Auto-pause at cap (no surprise bills)",
            "Usage notifications at 50%, 75%, 90%",
            "Perfect for seasonal trading"
          ]
        }
      ];
    } else if (currentPlan === "pro") {
      return [
        {
          id: "pay-per-use",
          name: "Pay-Per-Use",
          icon: <Zap className="h-6 w-6" />,
          price: "$24.99/month + usage",
          color: "purple",
          description: "Same base as Pro + overage billing when needed",
          recommended: true,
          benefits: [
            "Same 10,000 API call base as Pro",
            "Additional usage: $1 per 1,000 calls",
            "Screener runs: $0.10 per run",
            "AI backtests: $0.25 per test",
            "Hard cap: $124.99/month total",
            "Pause/resume usage control"
          ]
        }
      ];
    }
    return [];
  };

  const upgradeOptions = getUpgradeOptions();

  const handleUpgrade = (planId) => {
    navigate("/billing/checkout", {
      state: {
        plan: planId,
        cycle: "monthly",
        source: "quota_limit_upgrade"
      }
    });
    onClose();
  };

  const getColorClasses = (color) => {
    switch (color) {
      case 'blue': return 'bg-blue-100 text-blue-600 border-blue-500';
      case 'purple': return 'bg-purple-100 text-purple-600 border-purple-500';
      default: return 'bg-gray-100 text-gray-600 border-gray-500';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <DialogTitle className="text-2xl">Usage Limit Reached</DialogTitle>
                <DialogDescription className="text-base mt-1">
                  You've hit your {resourceName.toLowerCase()} quota
                </DialogDescription>
              </div>
            </div>
          </div>
        </DialogHeader>

        {/* Current Usage Display */}
        <div className="bg-gray-50 rounded-lg p-4 my-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Current Usage</span>
            <Badge variant="secondary" className="capitalize">
              {currentPlan} Plan
            </Badge>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{resourceName}</span>
              <span className="font-semibold">
                {currentUsage.toLocaleString()} / {quotaLimit.toLocaleString()}
              </span>
            </div>
            <Progress value={usagePercentage} className="h-2" />
            <p className="text-xs text-gray-500">
              You've reached {usagePercentage}% of your monthly allocation
            </p>
          </div>
        </div>

        {/* Upgrade Options */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Upgrade to Continue</h3>
          </div>

          <div className="grid gap-4">
            {upgradeOptions.map((option) => (
              <div
                key={option.id}
                className={`border-2 rounded-lg p-4 hover:shadow-md transition-all ${
                  option.recommended ? 'border-blue-500 bg-blue-50/50' : 'border-gray-200'
                }`}
              >
                {option.recommended && (
                  <Badge className="mb-2 bg-blue-600">Recommended</Badge>
                )}

                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getColorClasses(option.color)}`}>
                      {option.icon}
                    </div>
                    <div>
                      <h4 className="font-semibold text-lg">{option.name}</h4>
                      <p className="text-sm text-gray-600">{option.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-lg">{option.price}</div>
                  </div>
                </div>

                <ul className="space-y-2 mb-4">
                  {option.benefits.map((benefit, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <TrendingUp className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => handleUpgrade(option.id)}
                  className="w-full"
                  variant={option.recommended ? "default" : "outline"}
                >
                  Upgrade to {option.name}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            ))}
          </div>
        </div>

        <DialogFooter className="mt-4">
          <Button variant="ghost" onClick={onClose}>
            Maybe Later
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default UpgradeModal;
