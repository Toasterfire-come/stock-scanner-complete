import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Clock, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw,
  Globe,
  Calendar,
  Bell
} from 'lucide-react';
import { getMarketStatus, getMarketStatsSafe } from '../api/client';

const MarketStatusIndicator = ({ compact = false }) => {
  const [marketStatus, setMarketStatus] = useState(null);
  const [marketStats, setMarketStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchMarketData();
    // Update market status every 30 seconds
    const interval = setInterval(fetchMarketData, 30 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchMarketData = async () => {
    try {
      const [statusRes, statsRes] = await Promise.all([
        getMarketStatus().catch(() => null),
        getMarketStatsSafe().catch(() => ({ success: false }))
      ]);

      // Accept both {success:true, market:{...}} and {market:{...}}
      if (statusRes?.market || statusRes?.success) {
        setMarketStatus(statusRes.market || statusRes?.data?.market || statusRes);
      }
      
      if (statsRes?.success && statsRes?.data) {
        setMarketStats(statsRes.data);
      }
      
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError('Failed to load market status');
      console.error('Market status error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getMarketStatusInfo = () => {
    if (!marketStatus) return { status: 'unknown', color: 'gray', text: 'Unknown' };
    
    const now = new Date();
    const marketOpen = new Date(marketStatus.open);
    const marketClose = new Date(marketStatus.close);
    
    if (marketStatus.status === 'open') {
      return { 
        status: 'open', 
        color: 'green', 
        text: 'Market Open',
        timeInfo: `Closes at ${marketClose.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
      };
    } else {
      const nextOpen = new Date(marketOpen);
      nextOpen.setDate(nextOpen.getDate() + 1);
      
      return { 
        status: 'closed', 
        color: 'red', 
        text: 'Market Closed',
        timeInfo: `Opens at ${marketOpen.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
      };
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    return new Date(timeString).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  const statusInfo = getMarketStatusInfo();

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${
          statusInfo.status === 'open' ? 'bg-green-500' : 'bg-red-500'
        } ${statusInfo.status === 'open' ? 'animate-pulse' : ''}`} />
        <Badge variant={statusInfo.status === 'open' ? 'default' : 'secondary'} 
               className={statusInfo.status === 'open' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
          {statusInfo.text}
        </Badge>
        {lastUpdated && (
          <span className="text-xs text-gray-500">
            {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Market Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Market Status
            <div className={`w-2 h-2 rounded-full ${
              statusInfo.status === 'open' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`} />
          </CardTitle>
          <CardDescription>NYSE & NASDAQ trading status</CardDescription>
        </div>
        <Button variant="ghost" size="sm" onClick={fetchMarketData} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      
      <CardContent>
        {error && (
          <Alert className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          {/* Current Status */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <Badge 
                variant={statusInfo.status === 'open' ? 'default' : 'secondary'}
                className={`${statusInfo.status === 'open' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} mb-2`}
              >
                {statusInfo.text}
              </Badge>
              <p className="text-sm text-gray-600">{statusInfo.timeInfo}</p>
            </div>
            <Clock className={`h-6 w-6 ${statusInfo.status === 'open' ? 'text-green-600' : 'text-red-600'}`} />
          </div>

          {/* Market Hours */}
          {marketStatus && (
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-sm font-medium text-blue-900 mb-1">Market Open</div>
                <div className="text-lg font-bold text-blue-700">
                  {formatTime(marketStatus.open)}
                </div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-sm font-medium text-blue-900 mb-1">Market Close</div>
                <div className="text-lg font-bold text-blue-700">
                  {formatTime(marketStatus.close)}
                </div>
              </div>
            </div>
          )}

          {/* Market Overview */}
          {marketStats && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-900">Today's Market</h4>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-2 bg-green-50 rounded">
                  <TrendingUp className="h-4 w-4 text-green-600 mx-auto mb-1" />
                  <div className="text-sm font-bold text-green-700">
                    {marketStats.market_overview?.gainers?.toLocaleString() || '0'}
                  </div>
                  <div className="text-xs text-green-600">Gainers</div>
                </div>
                <div className="text-center p-2 bg-red-50 rounded">
                  <TrendingDown className="h-4 w-4 text-red-600 mx-auto mb-1" />
                  <div className="text-sm font-bold text-red-700">
                    {marketStats.market_overview?.losers?.toLocaleString() || '0'}
                  </div>
                  <div className="text-xs text-red-600">Losers</div>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded">
                  <Calendar className="h-4 w-4 text-gray-600 mx-auto mb-1" />
                  <div className="text-sm font-bold text-gray-700">
                    {marketStats.market_overview?.unchanged?.toLocaleString() || '0'}
                  </div>
                  <div className="text-xs text-gray-600">Unchanged</div>
                </div>
              </div>
            </div>
          )}

          {/* Last Updated */}
          {lastUpdated && (
            <div className="flex items-center justify-center pt-2 border-t">
              <div className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MarketStatusIndicator;