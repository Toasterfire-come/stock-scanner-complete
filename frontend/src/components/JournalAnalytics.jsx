// Journal Analytics Dashboard - Phase 9 Enhancement
import React, { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Target,
  Calendar,
  DollarSign,
  Activity,
  Award,
  AlertTriangle,
  CheckCircle,
  Clock,
  Flame,
} from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  Legend,
} from "recharts";
import { format, subDays, startOfWeek, endOfWeek, isWithinInterval, parseISO, differenceInDays } from "date-fns";

const COLORS = ["#10B981", "#EF4444", "#F59E0B", "#3B82F6", "#8B5CF6", "#EC4899", "#06B6D4"];

/**
 * Journal Analytics Dashboard
 * Provides comprehensive analysis of trading journal entries
 * Phase 9 - Retention Features
 */
export function JournalAnalytics({ entries = [] }) {
  const [timeRange, setTimeRange] = useState("30d");
  const [activeTab, setActiveTab] = useState("overview");

  // Filter entries by time range
  const filteredEntries = useMemo(() => {
    const now = new Date();
    const ranges = {
      "7d": 7,
      "30d": 30,
      "90d": 90,
      "all": 9999,
    };
    const days = ranges[timeRange] || 30;
    const cutoff = subDays(now, days);
    
    return entries.filter((entry) => {
      try {
        const entryDate = parseISO(entry.date);
        return entryDate >= cutoff;
      } catch {
        return false;
      }
    });
  }, [entries, timeRange]);

  // Calculate comprehensive statistics
  const stats = useMemo(() => {
    const closed = filteredEntries.filter((e) => e.status !== "open");
    const wins = closed.filter((e) => e.status === "win");
    const losses = closed.filter((e) => e.status === "loss");
    
    const totalPnl = closed.reduce((sum, e) => sum + (e.pnl || 0), 0);
    const winPnl = wins.reduce((sum, e) => sum + (e.pnl || 0), 0);
    const lossPnl = losses.reduce((sum, e) => sum + Math.abs(e.pnl || 0), 0);
    
    const avgWin = wins.length > 0 ? winPnl / wins.length : 0;
    const avgLoss = losses.length > 0 ? lossPnl / losses.length : 0;
    const expectancy = closed.length > 0 
      ? (wins.length / closed.length) * avgWin - (losses.length / closed.length) * avgLoss
      : 0;
    
    const profitFactor = lossPnl > 0 ? winPnl / lossPnl : winPnl > 0 ? Infinity : 0;
    
    // Calculate win streaks
    let currentStreak = 0;
    let maxWinStreak = 0;
    let maxLossStreak = 0;
    let tempLossStreak = 0;
    
    closed.forEach((trade) => {
      if (trade.status === "win") {
        currentStreak++;
        maxWinStreak = Math.max(maxWinStreak, currentStreak);
        tempLossStreak = 0;
      } else if (trade.status === "loss") {
        tempLossStreak++;
        maxLossStreak = Math.max(maxLossStreak, tempLossStreak);
        currentStreak = 0;
      }
    });

    // Biggest win/loss
    const biggestWin = wins.length > 0 ? Math.max(...wins.map((w) => w.pnl || 0)) : 0;
    const biggestLoss = losses.length > 0 ? Math.min(...losses.map((l) => l.pnl || 0)) : 0;

    return {
      totalTrades: filteredEntries.length,
      closedTrades: closed.length,
      openTrades: filteredEntries.filter((e) => e.status === "open").length,
      wins: wins.length,
      losses: losses.length,
      winRate: closed.length > 0 ? (wins.length / closed.length) * 100 : 0,
      totalPnl,
      avgWin,
      avgLoss,
      expectancy,
      profitFactor,
      maxWinStreak,
      maxLossStreak,
      biggestWin,
      biggestLoss,
      avgTradeSize: closed.length > 0 ? totalPnl / closed.length : 0,
    };
  }, [filteredEntries]);

  // Daily P&L data for chart
  const dailyPnlData = useMemo(() => {
    const daily = {};
    filteredEntries.filter((e) => e.status !== "open").forEach((entry) => {
      try {
        const date = format(parseISO(entry.date), "MMM d");
        if (!daily[date]) daily[date] = { date, pnl: 0, trades: 0 };
        daily[date].pnl += entry.pnl || 0;
        daily[date].trades++;
      } catch {}
    });
    return Object.values(daily).slice(-30);
  }, [filteredEntries]);

  // Cumulative P&L for equity curve
  const equityCurve = useMemo(() => {
    let cumulative = 0;
    return filteredEntries
      .filter((e) => e.status !== "open")
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .map((entry) => {
        cumulative += entry.pnl || 0;
        return {
          date: format(parseISO(entry.date), "MMM d"),
          equity: cumulative,
        };
      });
  }, [filteredEntries]);

  // Strategy performance breakdown
  const strategyPerformance = useMemo(() => {
    const strategies = {};
    filteredEntries.filter((e) => e.status !== "open").forEach((entry) => {
      const strategy = entry.strategy || "No Strategy";
      if (!strategies[strategy]) {
        strategies[strategy] = { name: strategy, wins: 0, losses: 0, pnl: 0 };
      }
      strategies[strategy].pnl += entry.pnl || 0;
      if (entry.status === "win") strategies[strategy].wins++;
      else if (entry.status === "loss") strategies[strategy].losses++;
    });
    return Object.values(strategies)
      .map((s) => ({
        ...s,
        winRate: s.wins + s.losses > 0 ? (s.wins / (s.wins + s.losses)) * 100 : 0,
      }))
      .sort((a, b) => b.pnl - a.pnl);
  }, [filteredEntries]);

  // Win/Loss distribution for pie chart
  const winLossData = useMemo(() => [
    { name: "Wins", value: stats.wins, color: "#10B981" },
    { name: "Losses", value: stats.losses, color: "#EF4444" },
    { name: "Breakeven", value: filteredEntries.filter((e) => e.status === "breakeven").length, color: "#9CA3AF" },
  ], [stats, filteredEntries]);

  // Day of week analysis
  const dayOfWeekData = useMemo(() => {
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const dayStats = days.map((day) => ({ day, pnl: 0, trades: 0 }));
    
    filteredEntries.filter((e) => e.status !== "open").forEach((entry) => {
      try {
        const dayIndex = parseISO(entry.date).getDay();
        dayStats[dayIndex].pnl += entry.pnl || 0;
        dayStats[dayIndex].trades++;
      } catch {}
    });
    
    return dayStats.slice(1, 6); // Mon-Fri only
  }, [filteredEntries]);

  if (filteredEntries.length === 0) {
    return (
      <Card className="p-12 text-center">
        <BarChart3 className="h-16 w-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data</h3>
        <p className="text-gray-500">Start logging trades to see performance analytics</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6" data-testid="journal-analytics">
      {/* Header with Time Range Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Performance Analytics</h2>
          <p className="text-gray-500">Analyze your trading performance over time</p>
        </div>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-32">
            <Calendar className="h-4 w-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">7 Days</SelectItem>
            <SelectItem value="30d">30 Days</SelectItem>
            <SelectItem value="90d">90 Days</SelectItem>
            <SelectItem value="all">All Time</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Win Rate</p>
                <p className="text-2xl font-bold">{stats.winRate.toFixed(1)}%</p>
              </div>
              <Target className={`h-8 w-8 ${stats.winRate >= 50 ? "text-green-500" : "text-red-500"}`} />
            </div>
            <p className="text-xs text-gray-400 mt-1">{stats.wins}W / {stats.losses}L</p>
          </CardContent>
        </Card>
        
        <Card className={stats.totalPnl >= 0 ? "bg-green-50" : "bg-red-50"}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total P&L</p>
                <p className={`text-2xl font-bold ${stats.totalPnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                  ${stats.totalPnl.toFixed(2)}
                </p>
              </div>
              {stats.totalPnl >= 0 ? (
                <TrendingUp className="h-8 w-8 text-green-500" />
              ) : (
                <TrendingDown className="h-8 w-8 text-red-500" />
              )}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Profit Factor</p>
                <p className="text-2xl font-bold">
                  {stats.profitFactor === Infinity ? "∞" : stats.profitFactor.toFixed(2)}
                </p>
              </div>
              <Activity className="h-8 w-8 text-blue-500" />
            </div>
            <p className="text-xs text-gray-400 mt-1">
              {stats.profitFactor >= 1.5 ? "Strong" : stats.profitFactor >= 1 ? "Positive" : "Needs work"}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Expectancy</p>
                <p className={`text-2xl font-bold ${stats.expectancy >= 0 ? "text-green-600" : "text-red-600"}`}>
                  ${stats.expectancy.toFixed(2)}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-purple-500" />
            </div>
            <p className="text-xs text-gray-400 mt-1">Per trade expected</p>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <Card className="p-3 text-center">
          <p className="text-xs text-gray-500">Avg Win</p>
          <p className="text-lg font-semibold text-green-600">${stats.avgWin.toFixed(2)}</p>
        </Card>
        <Card className="p-3 text-center">
          <p className="text-xs text-gray-500">Avg Loss</p>
          <p className="text-lg font-semibold text-red-600">${stats.avgLoss.toFixed(2)}</p>
        </Card>
        <Card className="p-3 text-center">
          <p className="text-xs text-gray-500">Biggest Win</p>
          <p className="text-lg font-semibold text-green-600">${stats.biggestWin.toFixed(2)}</p>
        </Card>
        <Card className="p-3 text-center">
          <p className="text-xs text-gray-500">Biggest Loss</p>
          <p className="text-lg font-semibold text-red-600">${Math.abs(stats.biggestLoss).toFixed(2)}</p>
        </Card>
        <Card className="p-3 text-center">
          <p className="text-xs text-gray-500">Win Streak</p>
          <p className="text-lg font-semibold flex items-center justify-center gap-1">
            <Flame className="h-4 w-4 text-orange-500" />
            {stats.maxWinStreak}
          </p>
        </Card>
        <Card className="p-3 text-center">
          <p className="text-xs text-gray-500">Loss Streak</p>
          <p className="text-lg font-semibold flex items-center justify-center gap-1">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            {stats.maxLossStreak}
          </p>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="equity">Equity Curve</TabsTrigger>
          <TabsTrigger value="strategies">By Strategy</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Daily P&L Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Daily P&L</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dailyPnlData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" fontSize={12} />
                      <YAxis fontSize={12} />
                      <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                      <Bar
                        dataKey="pnl"
                        fill="#3B82F6"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Win/Loss Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Win/Loss Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={winLossData.filter((d) => d.value > 0)}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {winLossData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="equity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Equity Curve</CardTitle>
              <CardDescription>Cumulative profit/loss over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={equityCurve}>
                    <defs>
                      <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                    <Area
                      type="monotone"
                      dataKey="equity"
                      stroke="#10B981"
                      fill="url(#equityGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="strategies" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Performance by Strategy</CardTitle>
            </CardHeader>
            <CardContent>
              {strategyPerformance.length > 0 ? (
                <div className="space-y-4">
                  {strategyPerformance.map((strategy, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <div>
                          <p className="font-medium">{strategy.name}</p>
                          <p className="text-sm text-gray-500">
                            {strategy.wins}W / {strategy.losses}L ({strategy.winRate.toFixed(0)}%)
                          </p>
                        </div>
                      </div>
                      <div className={`text-lg font-bold ${strategy.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                        ${strategy.pnl.toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">
                  No strategy data available. Add strategies to your trades.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="patterns" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Performance by Day of Week</CardTitle>
              <CardDescription>Find your most profitable trading days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dayOfWeekData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                    <Bar
                      dataKey="pnl"
                      radius={[4, 4, 0, 0]}
                    >
                      {dayOfWeekData.map((entry, index) => (
                        <Cell key={index} fill={entry.pnl >= 0 ? "#10B981" : "#EF4444"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default JournalAnalytics;
