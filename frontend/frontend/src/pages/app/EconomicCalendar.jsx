import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Calendar, Clock, TrendingUp, AlertTriangle, Info } from "lucide-react";
import { toast } from "sonner";

const EconomicCalendar = () => {
  const [calendarData, setCalendarData] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchCalendarData();
  }, [selectedDate]);

  const fetchCalendarData = async () => {
    setIsLoading(true);
    try {
      // Simulate economic calendar data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const today = new Date();
      const events = [
        {
          id: 1,
          time: "08:30",
          title: "Consumer Price Index (CPI)",
          country: "US",
          impact: "high",
          forecast: "0.3%",
          previous: "0.4%",
          actual: null,
          description: "Monthly change in consumer prices"
        },
        {
          id: 2,
          time: "10:00",
          title: "University of Michigan Consumer Sentiment",
          country: "US", 
          impact: "medium",
          forecast: "69.5",
          previous: "69.7",
          actual: "70.1",
          description: "Consumer confidence survey"
        },
        {
          id: 3,
          time: "14:00",
          title: "Federal Reserve Chair Speech",
          country: "US",
          impact: "high",
          forecast: null,
          previous: null,
          actual: null,
          description: "Monetary policy outlook discussion"
        },
        {
          id: 4,
          time: "09:00",
          title: "Retail Sales",
          country: "US",
          impact: "medium",
          forecast: "0.2%",
          previous: "-0.1%",
          actual: null,
          description: "Monthly retail sales data"
        },
        {
          id: 5,
          time: "15:30",
          title: "API Crude Oil Stock Change",
          country: "US",
          impact: "low",
          forecast: "-2.1M",
          previous: "-0.5M",
          actual: "-1.8M",
          description: "Weekly crude oil inventory change"
        }
      ];

      setCalendarData(events);
    } catch (error) {
      toast.error("Failed to fetch economic calendar data");
    } finally {
      setIsLoading(false);
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getImpactIcon = (impact) => {
    switch (impact) {
      case "high":
        return <AlertTriangle className="h-3 w-3" />;
      case "medium":
        return <TrendingUp className="h-3 w-3" />;
      case "low":
        return <Info className="h-3 w-3" />;
      default:
        return <Info className="h-3 w-3" />;
    }
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getDatesForWeek = () => {
    const dates = [];
    const today = new Date();
    const startOfWeek = new Date(today.setDate(today.getDate() - today.getDay()));
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  const filterEventsByImpact = (events, impact) => {
    return events.filter(event => event.impact === impact);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Economic Calendar</h1>
          <p className="text-gray-600 mt-2">Track important economic events and data releases</p>
        </div>
        <Button onClick={fetchCalendarData}>
          <Calendar className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Today's Events - {formatDate(selectedDate)}</span>
              <Badge variant="outline" className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {calendarData.length} events
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-7 gap-2 mb-6">
              {getDatesForWeek().map((date, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedDate(date)}
                  className={`p-2 text-center rounded-lg border transition-colors ${
                    date.toDateString() === selectedDate.toDateString()
                      ? 'bg-blue-100 text-blue-700 border-blue-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="text-xs text-gray-500">
                    {date.toLocaleDateString('en-US', { weekday: 'short' })}
                  </div>
                  <div className="font-semibold">
                    {date.getDate()}
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="all" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">All Events</TabsTrigger>
            <TabsTrigger value="high" className="text-red-600">High Impact</TabsTrigger>
            <TabsTrigger value="medium" className="text-yellow-600">Medium Impact</TabsTrigger>
            <TabsTrigger value="low" className="text-green-600">Low Impact</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            <div className="space-y-4">
              {calendarData.map((event) => (
                <Card key={event.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge className={`${getImpactColor(event.impact)} flex items-center gap-1`}>
                            {getImpactIcon(event.impact)}
                            {event.impact.toUpperCase()}
                          </Badge>
                          <Badge variant="outline">{event.country}</Badge>
                          <span className="text-sm text-gray-500 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {event.time}
                          </span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {event.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-3">
                          {event.description}
                        </p>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Forecast:</span>
                            <div className="font-medium">
                              {event.forecast || 'N/A'}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-500">Previous:</span>
                            <div className="font-medium">
                              {event.previous || 'N/A'}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-500">Actual:</span>
                            <div className={`font-medium ${event.actual ? 'text-blue-600' : 'text-gray-400'}`}>
                              {event.actual || 'Pending'}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="high">
            <div className="space-y-4">
              {filterEventsByImpact(calendarData, 'high').map((event) => (
                <Card key={event.id} className="border-red-200 hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge className="bg-red-100 text-red-800 border-red-200 flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" />
                        HIGH IMPACT
                      </Badge>
                      <Badge variant="outline">{event.country}</Badge>
                      <span className="text-sm text-gray-500 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {event.time}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {event.title}
                    </h3>
                    <p className="text-sm text-gray-600">{event.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="medium">
            <div className="space-y-4">
              {filterEventsByImpact(calendarData, 'medium').map((event) => (
                <Card key={event.id} className="border-yellow-200 hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200 flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        MEDIUM IMPACT
                      </Badge>
                      <Badge variant="outline">{event.country}</Badge>
                      <span className="text-sm text-gray-500 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {event.time}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {event.title}
                    </h3>
                    <p className="text-sm text-gray-600">{event.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="low">
            <div className="space-y-4">
              {filterEventsByImpact(calendarData, 'low').map((event) => (
                <Card key={event.id} className="border-green-200 hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge className="bg-green-100 text-green-800 border-green-200 flex items-center gap-1">
                        <Info className="h-3 w-3" />
                        LOW IMPACT
                      </Badge>
                      <Badge variant="outline">{event.country}</Badge>
                      <span className="text-sm text-gray-500 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {event.time}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {event.title}
                    </h3>
                    <p className="text-sm text-gray-600">{event.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default EconomicCalendar;