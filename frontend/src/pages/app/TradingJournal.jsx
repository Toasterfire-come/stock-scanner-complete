import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Textarea } from "../../components/ui/textarea";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Calendar } from "../../components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "../../components/ui/popover";
import {
  Plus,
  Trash2,
  Save,
  Edit,
  Loader2,
  BookOpen,
  TrendingUp,
  TrendingDown,
  Calendar as CalendarIcon,
  Target,
  DollarSign,
  BarChart3,
  Filter,
  Search,
  ImageIcon,
  Tag,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  PieChart,
} from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";
import { api } from "../../api/client";
import SEO from "../../components/SEO";
import { JournalAnalytics } from "../../components/JournalAnalytics";

// Trading Journal - Phase 9 Retention Feature
export default function TradingJournal() {
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("entries");
  const [editingEntry, setEditingEntry] = useState(null);
  const [saving, setSaving] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Form state
  const [formData, setFormData] = useState({
    date: new Date(),
    symbol: "",
    type: "long", // long or short
    entry_price: "",
    exit_price: "",
    shares: "",
    strategy: "",
    setup: "",
    notes: "",
    emotions: "",
    lessons: "",
    tags: [],
    status: "open", // open, win, loss, breakeven
    screenshot_url: "",
  });

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    setIsLoading(true);
    try {
      // Try API, fallback to localStorage for demo
      try {
        const { data } = await api.get("/journal/");
        if (data?.success) {
          setEntries(data.data || []);
          return;
        }
      } catch {}
      // Fallback to localStorage
      const stored = localStorage.getItem("trading_journal");
      if (stored) {
        setEntries(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load journal entries:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveToStorage = (updatedEntries) => {
    localStorage.setItem("trading_journal", JSON.stringify(updatedEntries));
  };

  const handleSave = async () => {
    if (!formData.symbol.trim()) {
      toast.error("Symbol is required");
      return;
    }

    setSaving(true);
    try {
      // Calculate P&L if both prices are provided
      let pnl = null;
      let pnlPercent = null;
      if (formData.entry_price && formData.exit_price && formData.shares) {
        const entry = parseFloat(formData.entry_price);
        const exit = parseFloat(formData.exit_price);
        const shares = parseFloat(formData.shares);
        const multiplier = formData.type === "short" ? -1 : 1;
        pnl = (exit - entry) * shares * multiplier;
        pnlPercent = ((exit - entry) / entry) * 100 * multiplier;
      }

      const entryData = {
        id: editingEntry?.id || Date.now().toString(),
        ...formData,
        date: formData.date.toISOString(),
        symbol: formData.symbol.toUpperCase(),
        pnl,
        pnl_percent: pnlPercent,
        updated_at: new Date().toISOString(),
      };

      let updatedEntries;
      if (editingEntry) {
        updatedEntries = entries.map((e) => (e.id === editingEntry.id ? entryData : e));
      } else {
        updatedEntries = [entryData, ...entries];
      }

      setEntries(updatedEntries);
      saveToStorage(updatedEntries);

      toast.success(editingEntry ? "Entry updated!" : "Entry added!");
      resetForm();
      setActiveTab("entries");
    } catch (error) {
      toast.error("Failed to save entry");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = (id) => {
    if (!confirm("Delete this journal entry?")) return;
    const updatedEntries = entries.filter((e) => e.id !== id);
    setEntries(updatedEntries);
    saveToStorage(updatedEntries);
    toast.success("Entry deleted");
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setFormData({
      ...entry,
      date: new Date(entry.date),
      tags: entry.tags || [],
    });
    setActiveTab("new");
  };

  const resetForm = () => {
    setEditingEntry(null);
    setFormData({
      date: new Date(),
      symbol: "",
      type: "long",
      entry_price: "",
      exit_price: "",
      shares: "",
      strategy: "",
      setup: "",
      notes: "",
      emotions: "",
      lessons: "",
      tags: [],
      status: "open",
      screenshot_url: "",
    });
  };

  // Filter entries
  const filteredEntries = entries.filter((entry) => {
    if (filterStatus !== "all" && entry.status !== filterStatus) return false;
    if (searchQuery && !entry.symbol.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Calculate stats
  const stats = {
    total: entries.length,
    wins: entries.filter((e) => e.status === "win").length,
    losses: entries.filter((e) => e.status === "loss").length,
    open: entries.filter((e) => e.status === "open").length,
    totalPnl: entries.reduce((sum, e) => sum + (e.pnl || 0), 0),
    winRate: entries.length > 0
      ? (entries.filter((e) => e.status === "win").length / entries.filter((e) => e.status !== "open").length) * 100
      : 0,
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "win":
        return <Badge className="bg-green-100 text-green-700"><CheckCircle className="h-3 w-3 mr-1" />Win</Badge>;
      case "loss":
        return <Badge className="bg-red-100 text-red-700"><XCircle className="h-3 w-3 mr-1" />Loss</Badge>;
      case "breakeven":
        return <Badge className="bg-gray-100 text-gray-700">Breakeven</Badge>;
      default:
        return <Badge className="bg-blue-100 text-blue-700"><Clock className="h-3 w-3 mr-1" />Open</Badge>;
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-6xl" data-testid="trading-journal-page">
      <SEO
        title="Trading Journal | Trade Scan Pro"
        description="Track and analyze your trades with our comprehensive trading journal"
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg">
            <BookOpen className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Trading Journal</h1>
            <p className="text-gray-500">Track, analyze, and improve your trading performance</p>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{stats.total}</p>
            <p className="text-sm text-gray-500">Total Trades</p>
          </CardContent>
        </Card>
        <Card className="bg-green-50">
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{stats.wins}</p>
            <p className="text-sm text-gray-500">Wins</p>
          </CardContent>
        </Card>
        <Card className="bg-red-50">
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-red-600">{stats.losses}</p>
            <p className="text-sm text-gray-500">Losses</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{stats.winRate.toFixed(0)}%</p>
            <p className="text-sm text-gray-500">Win Rate</p>
          </CardContent>
        </Card>
        <Card className={stats.totalPnl >= 0 ? "bg-green-50" : "bg-red-50"}>
          <CardContent className="p-4 text-center">
            <p className={`text-2xl font-bold ${stats.totalPnl >= 0 ? "text-green-600" : "text-red-600"}`}>
              ${stats.totalPnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className="text-sm text-gray-500">Total P&L</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <TabsList>
            <TabsTrigger value="entries" className="gap-2">
              <FileText className="h-4 w-4" />
              Entries
            </TabsTrigger>
            <TabsTrigger value="new" className="gap-2">
              <Plus className="h-4 w-4" />
              {editingEntry ? "Edit Entry" : "New Entry"}
            </TabsTrigger>
            <TabsTrigger value="analytics" className="gap-2">
              <PieChart className="h-4 w-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          {activeTab === "entries" && (
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search symbol..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-40"
                />
              </div>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-32">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="win">Wins</SelectItem>
                  <SelectItem value="loss">Losses</SelectItem>
                  <SelectItem value="breakeven">Breakeven</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <JournalAnalytics entries={entries} />
        </TabsContent>

        {/* Entries Tab */}
        <TabsContent value="entries" className="space-y-4">
          {isLoading ? (
            <Card className="p-12 text-center">
              <Loader2 className="h-12 w-12 mx-auto animate-spin text-blue-500 mb-4" />
              <p className="text-gray-500">Loading journal...</p>
            </Card>
          ) : filteredEntries.length > 0 ? (
            <div className="space-y-4">
              {filteredEntries.map((entry) => (
                <Card key={entry.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg ${entry.type === "long" ? "bg-green-100" : "bg-red-100"}`}>
                          {entry.type === "long" ? (
                            <TrendingUp className="h-5 w-5 text-green-600" />
                          ) : (
                            <TrendingDown className="h-5 w-5 text-red-600" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-bold text-lg">{entry.symbol}</h3>
                            {getStatusBadge(entry.status)}
                          </div>
                          <p className="text-sm text-gray-500">
                            {format(new Date(entry.date), "MMM d, yyyy")} • {entry.type.toUpperCase()}
                          </p>
                          {entry.strategy && (
                            <p className="text-sm text-gray-600 mt-1">Strategy: {entry.strategy}</p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-sm text-gray-500">Entry</p>
                          <p className="font-semibold">${entry.entry_price}</p>
                        </div>
                        {entry.exit_price && (
                          <div className="text-right">
                            <p className="text-sm text-gray-500">Exit</p>
                            <p className="font-semibold">${entry.exit_price}</p>
                          </div>
                        )}
                        {entry.pnl !== null && (
                          <div className="text-right">
                            <p className="text-sm text-gray-500">P&L</p>
                            <p className={`font-bold ${entry.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                              {entry.pnl >= 0 ? "+" : ""}${entry.pnl.toFixed(2)}
                            </p>
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" onClick={() => handleEdit(entry)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-500"
                            onClick={() => handleDelete(entry.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>

                    {(entry.notes || entry.lessons) && (
                      <div className="mt-4 pt-4 border-t grid md:grid-cols-2 gap-4 text-sm">
                        {entry.notes && (
                          <div>
                            <p className="text-gray-500 font-medium">Notes</p>
                            <p className="text-gray-700">{entry.notes}</p>
                          </div>
                        )}
                        {entry.lessons && (
                          <div>
                            <p className="text-gray-500 font-medium">Lessons Learned</p>
                            <p className="text-gray-700">{entry.lessons}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <BookOpen className="h-16 w-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Journal Entries</h3>
              <p className="text-gray-500 mb-4">Start documenting your trades to track performance</p>
              <Button onClick={() => setActiveTab("new")}>
                <Plus className="h-4 w-4 mr-2" />
                Add First Entry
              </Button>
            </Card>
          )}
        </TabsContent>

        {/* New Entry Tab */}
        <TabsContent value="new" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{editingEntry ? "Edit Trade Entry" : "Log New Trade"}</CardTitle>
              <CardDescription>Record the details of your trade for analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Date</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button variant="outline" className="w-full justify-start text-left font-normal">
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {format(formData.date, "PPP")}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar
                            mode="single"
                            selected={formData.date}
                            onSelect={(d) => d && setFormData((p) => ({ ...p, date: d }))}
                          />
                        </PopoverContent>
                      </Popover>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="symbol">Symbol *</Label>
                      <Input
                        id="symbol"
                        value={formData.symbol}
                        onChange={(e) => setFormData((p) => ({ ...p, symbol: e.target.value.toUpperCase() }))}
                        placeholder="AAPL"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Trade Type</Label>
                    <div className="flex gap-4">
                      <div
                        className={`flex-1 p-3 border rounded-lg cursor-pointer text-center ${formData.type === "long" ? "border-green-500 bg-green-50" : ""}`}
                        onClick={() => setFormData((p) => ({ ...p, type: "long" }))}
                      >
                        <TrendingUp className="h-5 w-5 mx-auto text-green-600" />
                        <p className="text-sm font-medium mt-1">Long</p>
                      </div>
                      <div
                        className={`flex-1 p-3 border rounded-lg cursor-pointer text-center ${formData.type === "short" ? "border-red-500 bg-red-50" : ""}`}
                        onClick={() => setFormData((p) => ({ ...p, type: "short" }))}
                      >
                        <TrendingDown className="h-5 w-5 mx-auto text-red-600" />
                        <p className="text-sm font-medium mt-1">Short</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="entry_price">Entry Price</Label>
                      <Input
                        id="entry_price"
                        type="number"
                        step="0.01"
                        value={formData.entry_price}
                        onChange={(e) => setFormData((p) => ({ ...p, entry_price: e.target.value }))}
                        placeholder="0.00"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="exit_price">Exit Price</Label>
                      <Input
                        id="exit_price"
                        type="number"
                        step="0.01"
                        value={formData.exit_price}
                        onChange={(e) => setFormData((p) => ({ ...p, exit_price: e.target.value }))}
                        placeholder="0.00"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="shares">Shares</Label>
                      <Input
                        id="shares"
                        type="number"
                        value={formData.shares}
                        onChange={(e) => setFormData((p) => ({ ...p, shares: e.target.value }))}
                        placeholder="100"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Trade Status</Label>
                    <Select value={formData.status} onValueChange={(v) => setFormData((p) => ({ ...p, status: v }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="open">Open</SelectItem>
                        <SelectItem value="win">Win</SelectItem>
                        <SelectItem value="loss">Loss</SelectItem>
                        <SelectItem value="breakeven">Breakeven</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="strategy">Strategy Used</Label>
                    <Input
                      id="strategy"
                      value={formData.strategy}
                      onChange={(e) => setFormData((p) => ({ ...p, strategy: e.target.value }))}
                      placeholder="e.g., Breakout, Mean Reversion"
                    />
                  </div>
                </div>

                {/* Right Column */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="setup">Setup Description</Label>
                    <Textarea
                      id="setup"
                      value={formData.setup}
                      onChange={(e) => setFormData((p) => ({ ...p, setup: e.target.value }))}
                      placeholder="Describe the trade setup..."
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="notes">Trade Notes</Label>
                    <Textarea
                      id="notes"
                      value={formData.notes}
                      onChange={(e) => setFormData((p) => ({ ...p, notes: e.target.value }))}
                      placeholder="Additional notes about the trade..."
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="emotions">Emotional State</Label>
                    <Input
                      id="emotions"
                      value={formData.emotions}
                      onChange={(e) => setFormData((p) => ({ ...p, emotions: e.target.value }))}
                      placeholder="e.g., Confident, Anxious, FOMO"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lessons">Lessons Learned</Label>
                    <Textarea
                      id="lessons"
                      value={formData.lessons}
                      onChange={(e) => setFormData((p) => ({ ...p, lessons: e.target.value }))}
                      placeholder="What did you learn from this trade?"
                      rows={3}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex gap-3">
              <Button onClick={handleSave} disabled={saving} className="gap-2">
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                {saving ? "Saving..." : "Save Entry"}
              </Button>
              {editingEntry && (
                <Button variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
              )}
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
