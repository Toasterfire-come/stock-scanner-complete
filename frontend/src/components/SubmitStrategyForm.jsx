// Submit Strategy Form Component - Phase 6
import React, { useState } from "react";
import { api } from "../api/client";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { toast } from "sonner";
import { Plus, Loader2, Upload, Lightbulb } from "lucide-react";
import logger from '../lib/logger';

/**
 * Submit Strategy Form - Allows users to submit their own strategies
 * Phase 6 - Strategy Ranking System
 */
export function SubmitStrategyForm({ onSuccess }) {
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "",
    strategy_text: "",
    symbols: "",
    timeframe: "1d",
    risk_level: "moderate",
    tags: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.category || !formData.strategy_text) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    setSubmitting(true);
    try {
      const payload = {
        ...formData,
        symbols: formData.symbols.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean),
        tags: formData.tags.split(",").map((t) => t.trim()).filter(Boolean),
      };
      
      await api.post("/api/strategy-ranking/submit/", payload);
      toast.success("Strategy submitted successfully! It will be reviewed before appearing on the leaderboard.");
      setOpen(false);
      setFormData({
        name: "",
        description: "",
        category: "",
        strategy_text: "",
        symbols: "",
        timeframe: "1d",
        risk_level: "moderate",
        tags: "",
      });
      onSuccess?.();
    } catch (error) {
      logger.error("Strategy submission error:", error);
      toast.error(error.response?.data?.message || "Failed to submit strategy");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="gap-2" data-testid="submit-strategy-button">
          <Plus className="h-4 w-4" />
          Submit Strategy
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            Submit Your Strategy
          </DialogTitle>
          <DialogDescription>
            Share your trading strategy with the community. Successful strategies can earn recognition on the leaderboard.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Strategy Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., RSI Momentum Swing"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select
                value={formData.category}
                onValueChange={(v) => setFormData({ ...formData, category: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="day_trading">Day Trading</SelectItem>
                  <SelectItem value="swing_trading">Swing Trading</SelectItem>
                  <SelectItem value="long_term">Long-Term Investing</SelectItem>
                  <SelectItem value="value_investing">Value Investing</SelectItem>
                  <SelectItem value="momentum">Momentum</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Briefly describe what makes this strategy unique..."
              rows={2}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="strategy_text">Strategy Rules *</Label>
            <Textarea
              id="strategy_text"
              value={formData.strategy_text}
              onChange={(e) => setFormData({ ...formData, strategy_text: e.target.value })}
              placeholder="Describe your entry/exit rules in detail. For example:
Entry: Buy when RSI crosses above 30 and price is above 50 SMA
Exit: Sell when RSI exceeds 70 or stop loss at 5%"
              rows={5}
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="symbols">Symbols (comma-separated)</Label>
              <Input
                id="symbols"
                value={formData.symbols}
                onChange={(e) => setFormData({ ...formData, symbols: e.target.value })}
                placeholder="e.g., AAPL, MSFT, NVDA"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="timeframe">Preferred Timeframe</Label>
              <Select
                value={formData.timeframe}
                onValueChange={(v) => setFormData({ ...formData, timeframe: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1m">1 Minute</SelectItem>
                  <SelectItem value="5m">5 Minutes</SelectItem>
                  <SelectItem value="15m">15 Minutes</SelectItem>
                  <SelectItem value="1h">1 Hour</SelectItem>
                  <SelectItem value="4h">4 Hours</SelectItem>
                  <SelectItem value="1d">Daily</SelectItem>
                  <SelectItem value="1w">Weekly</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="risk_level">Risk Level</Label>
              <Select
                value={formData.risk_level}
                onValueChange={(v) => setFormData({ ...formData, risk_level: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="conservative">Conservative</SelectItem>
                  <SelectItem value="moderate">Moderate</SelectItem>
                  <SelectItem value="aggressive">Aggressive</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="tags">Tags (comma-separated)</Label>
              <Input
                id="tags"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                placeholder="e.g., momentum, technical, stocks"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting} className="gap-2">
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Submit Strategy
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default SubmitStrategyForm;
