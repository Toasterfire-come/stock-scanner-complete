import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { getTrending, getMarketStats } from "../api/client";
import { TrendingUp, TrendingDown, BarChart3, Activity } from "lucide-react";

export default function Markets() {
  const [trending, setTrending] = useState({ high_volume: [], top_gainers: [], most_active: [] });
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [trendingData, statsData] = await Promise.all([
          getTrending().catch(() => ({ high_volume: [], top_gainers: [], most_active: [] })),
          getMarketStats().catch(() => null)
        ]);
        setTrending(trendingData);
        setStats(statsData);
      } catch (error) {
        console.error("Failed to fetch market data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="space-y-8 p-6">
      {/* Page Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Market Overview</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Real-time market data and trending stocks to help you make informed trading decisions
        </p>
      </div>

      {/* Market Stats Card */}
      <Card className="shadow-lg border-0 bg-gradient-to-br from-blue-50 to-indigo-50">
        <CardHeader className="pb-4">
          <CardTitle className="text-2xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="h-6 w-6 mr-3 text-blue-600" />
            Market Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-white rounded-xl shadow-sm">
              <div className="text-gray-600 text-sm font-medium mb-2">Total Stocks</div>
              <div className="text-3xl font-bold text-gray-900">
                {isLoading ? (
                  <div className="animate-pulse bg-gray-200 h-8 w-16 mx-auto rounded"></div>
                ) : (
                  stats?.market_overview?.total_stocks?.toLocaleString() ?? "—"
                )}
              </div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-xl shadow-sm">
              <div className="text-gray-600 text-sm font-medium mb-2">Gainers</div>
              <div className="text-3xl font-bold text-green-600 flex items-center justify-center">
                {isLoading ? (
                  <div className="animate-pulse bg-gray-200 h-8 w-16 rounded"></div>
                ) : (
                  <>
                    <TrendingUp className="h-6 w-6 mr-2" />
                    {stats?.market_overview?.gainers?.toLocaleString() ?? "—"}
                  </>
                )}
              </div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-xl shadow-sm">
              <div className="text-gray-600 text-sm font-medium mb-2">Losers</div>
              <div className="text-3xl font-bold text-red-600 flex items-center justify-center">
                {isLoading ? (
                  <div className="animate-pulse bg-gray-200 h-8 w-16 rounded"></div>
                ) : (
                  <>
                    <TrendingDown className="h-6 w-6 mr-2" />
                    {stats?.market_overview?.losers?.toLocaleString() ?? "—"}
                  </>
                )}
              </div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-xl shadow-sm">
              <div className="text-gray-600 text-sm font-medium mb-2">Unchanged</div>
              <div className="text-3xl font-bold text-gray-600">
                {isLoading ? (
                  <div className="animate-pulse bg-gray-200 h-8 w-16 mx-auto rounded"></div>
                ) : (
                  stats?.market_overview?.unchanged?.toLocaleString() ?? "—"
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Trending Stocks */}
      <div className="grid md:grid-cols-3 gap-6">
        {[
          { 
            title: "High Volume", 
            key: "high_volume", 
            icon: <Activity className="h-5 w-5" />,
            color: "border-purple-200 bg-purple-50",
            iconColor: "text-purple-600"
          }, 
          { 
            title: "Top Gainers", 
            key: "top_gainers", 
            icon: <TrendingUp className="h-5 w-5" />,
            color: "border-green-200 bg-green-50",
            iconColor: "text-green-600"
          }, 
          { 
            title: "Most Active", 
            key: "most_active", 
            icon: <BarChart3 className="h-5 w-5" />,
            color: "border-blue-200 bg-blue-50",
            iconColor: "text-blue-600"
          }
        ].map((section) => (
          <Card key={section.key} className={`shadow-lg border-2 ${section.color} hover:shadow-xl transition-shadow duration-300`}>
            <CardHeader className="pb-4">
              <CardTitle className={`text-lg font-bold flex items-center ${section.iconColor}`}>
                {section.icon}
                <span className="ml-2 text-gray-900">{section.title}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {isLoading ? (
                // Loading skeleton
                Array.from({ length: 5 }).map((_, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg">
                    <div className="animate-pulse bg-gray-200 h-4 w-16 rounded"></div>
                    <div className="animate-pulse bg-gray-200 h-4 w-12 rounded"></div>
                  </div>
                ))
              ) : trending[section.key]?.length > 0 ? (
                trending[section.key].slice(0, 10).map((stock, index) => (
                  <div key={stock.ticker || index} className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center text-xs font-bold text-gray-600">
                        {index + 1}
                      </div>
                      <span className="font-semibold text-gray-900">{stock.ticker}</span>
                    </div>
                    <div className="text-right">
                      {stock.change_percent !== undefined && (
                        <Badge 
                          variant={stock.change_percent > 0 ? "default" : "destructive"}
                          className={`font-semibold ${
                            stock.change_percent > 0 
                              ? "bg-green-100 text-green-800 hover:bg-green-200" 
                              : "bg-red-100 text-red-800 hover:bg-red-200"
                          }`}
                        >
                          {stock.change_percent > 0 ? "+" : ""}{stock.change_percent.toFixed(2)}%
                        </Badge>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p className="text-sm">No data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Market Status Banner */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-2xl shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-4 h-4 bg-green-300 rounded-full animate-pulse"></div>
            <div>
              <h3 className="text-xl font-bold">Markets Are Open</h3>
              <p className="text-green-100">Real-time data updating continuously</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">NYSE • NASDAQ</div>
            <div className="text-green-100 text-sm">9:30 AM - 4:00 PM EST</div>
          </div>
        </div>
      </div>

      {/* Professional Notice */}
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
        <p className="text-gray-600 text-sm">
          <strong>Professional Trading Platform:</strong> Market data is provided for informational purposes only. 
          Always consult with qualified financial advisors before making investment decisions.
        </p>
      </div>
    </div>
  );
}