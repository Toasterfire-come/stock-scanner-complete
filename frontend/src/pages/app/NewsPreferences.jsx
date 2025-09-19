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
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">News Preferences</h1>
            <p className="text-gray-600 mt-2">Customize your news feed to match your interests</p>
          </div>
          <Button onClick={savePreferences} disabled={isSaving}>
            <Save className="h-4 w-4 mr-2" />
            Save Preferences
          </Button>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Followed Stocks
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter stock ticker (e.g., AAPL)"
                  value={newStock}
                  onChange={(e) => setNewStock(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && addStock()}
                  className="flex-1"
                />
                <Button onClick={addStock}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add
                </Button>
                <Button variant="outline" onClick={syncPortfolio}>
                  Sync Portfolio
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-2">
                {preferences.followedStocks.map((ticker) => (
                  <Badge key={ticker} variant="secondary" className="px-3 py-1">
                    {ticker}
                    <button
                      onClick={() => removeStock(ticker)}
                      className="ml-2 hover:text-red-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
              
              {preferences.followedStocks.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No stocks selected. Add some tickers to get personalized news.
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Preferred Sectors</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-3">
                {availableSectors.map((sector) => (
                  <div key={sector} className="flex items-center space-x-2">
                    <Checkbox
                      id={sector}
                      checked={preferences.followedSectors.includes(sector)}
                      onCheckedChange={() => toggleSector(sector)}
                    />
                    <Label htmlFor={sector} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      {sector}
                    </Label>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>News Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-3">
                {availableCategories.map((category) => (
                  <div key={category.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={category.id}
                      checked={preferences.preferredCategories.includes(category.id)}
                      onCheckedChange={() => toggleCategory(category.id)}
                    />
                    <Label htmlFor={category.id} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      {category.label}
                    </Label>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Notification Frequency</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Label htmlFor="frequency">How often would you like to receive news updates?</Label>
                <Select value={preferences.newsFrequency} onValueChange={(value) => 
                  setPreferences({...preferences, newsFrequency: value})
                }>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {frequencyOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="text-sm text-gray-600">
                  {preferences.newsFrequency === "realtime" && "Get notified immediately when important news breaks"}
                  {preferences.newsFrequency === "hourly" && "Receive a digest of news every hour"}
                  {preferences.newsFrequency === "daily" && "Get a daily summary of the most important news"}
                  {preferences.newsFrequency === "weekly" && "Receive a weekly roundup of market news"}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {preferences.followedStocks.length}
                  </div>
                  <div className="text-sm text-gray-600">Followed Stocks</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    {preferences.followedSectors.length}
                  </div>
                  <div className="text-sm text-gray-600">Sectors</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {preferences.preferredCategories.length}
                  </div>
                  <div className="text-sm text-gray-600">Categories</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default NewsPreferences;