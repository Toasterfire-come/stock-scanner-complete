import React, { useState, useEffect } from 'react';
import { Badge } from './ui/badge';
import { Clock, AlertCircle } from 'lucide-react';

const MarketStatus = ({ showNotice = false }) => {
  const [marketStatus, setMarketStatus] = useState({
    isOpen: false,
    status: 'Closed',
    nextOpen: null,
    nextClose: null,
    timezone: 'ET'
  });

  useEffect(() => {
    const checkMarketStatus = () => {
      const now = new Date();
      
      // Convert to ET timezone
      const etTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
      const day = etTime.getDay(); // 0 = Sunday, 6 = Saturday
      const hours = etTime.getHours();
      const minutes = etTime.getMinutes();
      const currentTime = hours * 60 + minutes; // Convert to minutes since midnight
      
      // Market hours: 9:30 AM - 4:00 PM ET, Monday to Friday
      const marketOpen = 9 * 60 + 30; // 9:30 AM in minutes
      const marketClose = 16 * 60; // 4:00 PM in minutes
      
      let isOpen = false;
      let status = 'Closed';
      let nextOpen = null;
      let nextClose = null;
      
      // Check if it's a weekday (Monday = 1, Friday = 5)
      if (day >= 1 && day <= 5) {
        if (currentTime >= marketOpen && currentTime < marketClose) {
          isOpen = true;
          status = 'Open';
          
          // Calculate next close time
          const closeTime = new Date(etTime);
          closeTime.setHours(16, 0, 0, 0);
          nextClose = closeTime;
        } else if (currentTime < marketOpen) {
          status = 'Pre-Market';
          
          // Calculate market open time for today
          const openTime = new Date(etTime);
          openTime.setHours(9, 30, 0, 0);
          nextOpen = openTime;
        } else {
          status = 'After Hours';
          
          // Calculate next market open (next business day)
          const nextDay = new Date(etTime);
          nextDay.setDate(nextDay.getDate() + 1);
          nextDay.setHours(9, 30, 0, 0);
          
          // If tomorrow is Saturday, move to Monday
          if (nextDay.getDay() === 6) {
            nextDay.setDate(nextDay.getDate() + 2);
          }
          // If tomorrow is Sunday, move to Monday  
          else if (nextDay.getDay() === 0) {
            nextDay.setDate(nextDay.getDate() + 1);
          }
          
          nextOpen = nextDay;
        }
      } else {
        status = 'Weekend';
        
        // Calculate next Monday opening
        const daysUntilMonday = day === 0 ? 1 : (8 - day); // If Sunday, 1 day; if Saturday, 2 days
        const nextMonday = new Date(etTime);
        nextMonday.setDate(nextMonday.getDate() + daysUntilMonday);
        nextMonday.setHours(9, 30, 0, 0);
        nextOpen = nextMonday;
      }
      
      setMarketStatus({
        isOpen,
        status,
        nextOpen,
        nextClose,
        timezone: 'ET'
      });
    };

    // Check immediately
    checkMarketStatus();
    
    // Update every minute
    const interval = setInterval(checkMarketStatus, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const formatTime = (date) => {
    if (!date) return '';
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZone: 'America/New_York'
    });
  };

  const formatDate = (date) => {
    if (!date) return '';
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      timeZone: 'America/New_York'
    });
  };

  const getStatusColor = () => {
    switch (marketStatus.status) {
      case 'Open':
        return 'bg-green-500 text-white';
      case 'Pre-Market':
        return 'bg-yellow-500 text-white';
      case 'After Hours':
        return 'bg-orange-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className="flex flex-col space-y-2">
      <Badge className={`inline-flex items-center space-x-2 ${getStatusColor()}`}>
        <Clock className="h-3 w-3" />
        <span>Market {marketStatus.status} ({marketStatus.timezone})</span>
      </Badge>
      
      {showNotice && !marketStatus.isOpen && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-2">
              <AlertCircle className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 text-base">
                Market {marketStatus.status} ({marketStatus.timezone})
              </p>
              <p className="text-sm text-gray-700 mt-1">
                Market is currently closed
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Data updates are paused outside trading hours for more accurate information.
              </p>
              {marketStatus.nextOpen && (
                <p className="text-sm font-medium text-blue-700 mt-2">
                  Next market open: {formatDate(marketStatus.nextOpen)} at {formatTime(marketStatus.nextOpen)} {marketStatus.timezone}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {marketStatus.nextClose && marketStatus.isOpen && (
        <p className="text-xs text-gray-600">
          Market closes at {formatTime(marketStatus.nextClose)} {marketStatus.timezone}
        </p>
      )}
    </div>
  );
};

export default MarketStatus;