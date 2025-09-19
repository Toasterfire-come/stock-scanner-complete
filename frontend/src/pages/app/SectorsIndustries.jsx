import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Progress } from "../../components/ui/progress";
import { TrendingUp, TrendingDown, Building2 } from "lucide-react";
import { toast } from "sonner";
import { getSectorsOverview } from "../../api/client";

const SectorsIndustries = () => {
  const [sectorsData, setSectorsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSectorsData();
  }, []);

  const fetchSectorsData = async () => {
    setIsLoading(true);
    setError("");
    try {
      const res = await getSectorsOverview();
      const items = Array.isArray(res?.data) ? res.data : Array.isArray(res) ? res : [];
      setSectorsData(items);
    } catch (error) {
      setError("Failed to fetch sectors data");
      toast.error("Failed to fetch sectors data");
      setSectorsData([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getSectorColor = (change) => {
    if (change > 1) return "text-green-600 bg-green-100";
    if (change > 0) return "text-green-500 bg-green-50";
    if (change > -1) return "text-red-500 bg-red-50";
    return "text-red-600 bg-red-100";
  };

  const getMaxMarketCap = () => {
    const vals = sectorsData.map((s) => s.marketCap || 0);
    const max = Math.max(...vals);
    return Number.isFinite(max) ? max : 1;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sectors & Industries</h1>
          <p className="text-gray-600 mt-2">Performance breakdown by market sectors</p>
        </div>
        <Button onClick={fetchSectorsData}><Building2 className="h-4 w-4 mr-2" /> Refresh Data</Button>
      </div>

      {error && (
        <Card className="border-l-4 border-l-yellow-500 bg-yellow-50/50 mb-6">
          <CardContent className="p-4 text-yellow-800 flex items-center justify-between">
            <span>{error}</span>
            <Button size="sm" variant="outline" onClick={fetchSectorsData}>Retry</Button>
          </CardContent>
        </Card>
      )}

      {!sectorsData.length ? (
        <Card>
          <CardHeader>
            <CardTitle>No sector data</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-gray-600">Please try refreshing. Sector data may not be available yet.</div>
            <Button variant="outline" className="mt-3" onClick={fetchSectorsData}>Retry</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sectorsData.map((sector) => (
              <Card key={sector.name} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{sector.name}</CardTitle>
                    <Badge className={getSectorColor(sector.avgChange)}>
                      {sector.avgChange >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                      {sector.avgChange >= 0 ? '+' : ''}{sector.avgChange.toFixed(2)}%
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Stocks</div>
                      <div className="font-semibold">{sector.stocks}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Volume</div>
                      <div className="font-semibold">{(sector.volume / 1e9).toFixed(1)}B</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 mb-2">Market Cap</div>
                    <div className="flex items-center gap-2">
                      <Progress value={(sector.marketCap / getMaxMarketCap()) * 100} className="flex-1" />
                      <span className="text-sm font-medium">${(sector.marketCap / 1e12).toFixed(1)}T</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 mb-2">Top Performers</div>
                    <div className="flex flex-wrap gap-1">
                      {(sector.topStocks || []).map((stock) => (
                        <Badge key={stock} variant="outline" className="text-xs">{stock}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SectorsIndustries;