import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Checkbox } from "../../components/ui/checkbox";
import { Badge } from "../../components/ui/badge";
import { X, Plus, Save, Settings } from "lucide-react";
import { toast } from "sonner";
import { getNewsPreferences, updateNewsPreferences, syncPortfolioNews } from "../../api/client";

const NewsPreferences = () => {
  const navigate = useNavigate();
  const [preferences, setPreferences] = useState({
    followedStocks: [],
    followedSectors: [],
    preferredCategories: [],
    newsFrequency: "realtime"
  });
  const [newStock, setNewStock] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const availableCategories = [
    { id: "earnings", label: "Earnings Reports" },
    { id: "markets", label: "Market Analysis" },
    { id: "breaking", label: "Breaking News" },
    { id: "analyst", label: "Analyst Ratings" },
    { id: "ipos", label: "IPOs & New Listings" },
    { id: "mergers", label: "Mergers & Acquisitions" },
    { id: "regulatory", label: "Regulatory Changes" },
    { id: "commodities", label: "Commodities" }
  ];

  const availableSectors = [
    "Technology",
    "Healthcare", 
    "Financial Services",
    "Consumer Discretionary",
    "Energy",
    "Industrials",
    "Real Estate",
    "Telecommunications",
    "Utilities",
    "Materials"
  ];

  const frequencyOptions = [
    { value: "realtime", label: "Real-time" },
    { value: "hourly", label: "Hourly Digest" },
    { value: "daily", label: "Daily Summary" },
    { value: "weekly", label: "Weekly Report" }
  ];

  useEffect(() => { fetchPreferences(); }, []);

  const fetchPreferences = async () => {
    setIsLoading(true);
    try {
      const res = await getNewsPreferences();
      const p = res?.data || res || {};
      setPreferences({
        followedStocks: Array.isArray(p.followedStocks) ? p.followedStocks : [],
        followedSectors: Array.isArray(p.followedSectors) ? p.followedSectors : [],
        preferredCategories: Array.isArray(p.preferredCategories) ? p.preferredCategories : [],
        newsFrequency: p.newsFrequency || "realtime"
      });
    } catch (error) {
      toast.error("Failed to load preferences");
      setPreferences({ followedStocks: [], followedSectors: [], preferredCategories: [], newsFrequency: "realtime" });
    } finally {
      setIsLoading(false);
    }
  };

  const addStock = () => {
    const ticker = newStock.trim().toUpperCase();
    if (ticker && !preferences.followedStocks.includes(ticker)) {
      setPreferences({
        ...preferences,
        followedStocks: [...preferences.followedStocks, ticker]
      });
      setNewStock("");
    } else if (preferences.followedStocks.includes(ticker)) {
      toast.error("Stock already in your watchlist");
    }
  };

  const removeStock = (ticker) => {
    setPreferences({
      ...preferences,
      followedStocks: preferences.followedStocks.filter(stock => stock !== ticker)
    });
  };

  const toggleSector = (sector) => {
    const isSelected = preferences.followedSectors.includes(sector);
    setPreferences({
      ...preferences,
      followedSectors: isSelected
        ? preferences.followedSectors.filter(s => s !== sector)
        : [...preferences.followedSectors, sector]
    });
  };

  const toggleCategory = (categoryId) => {
    const isSelected = preferences.preferredCategories.includes(categoryId);
    setPreferences({
      ...preferences,
      preferredCategories: isSelected
        ? preferences.preferredCategories.filter(c => c !== categoryId)
        : [...preferences.preferredCategories, categoryId]
    });
  };

  const savePreferences = async () => {
    setIsSaving(true);
    try {
      const payload = { ...preferences };
      await updateNewsPreferences(payload);
      toast.success("Preferences saved successfully");
      navigate("/app/news");
    } catch (error) {
      toast.error("Failed to save preferences");
    } finally {
      setIsSaving(false);
    }
  };

  const syncPortfolio = async () => {
    try {
      const res = await syncPortfolioNews();
      const newStocks = Array.isArray(res?.added) ? res.added : [];
      if (newStocks.length > 0) {
        setPreferences((prev) => ({
          ...prev,
          followedStocks: [...prev.followedStocks, ...newStocks.filter((s) => !prev.followedStocks.includes(s))]
        }));
        toast.success(`Added ${newStocks.length} stocks from your portfolio`);
      } else {
        toast.info("No new portfolio stocks to follow");
      }
    } catch (error) {
      toast.error("Failed to sync portfolio");
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">News Preferences</h1>
      <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        {/* preference controls */}
      </div>
    </div>
  );
};

export default NewsPreferences;