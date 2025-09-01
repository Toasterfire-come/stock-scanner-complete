import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Search, ExternalLink, Clock, TrendingUp, Filter, RefreshCw } from "lucide-react";
import { toast } from "sonner";

const NewsFeed = () => {
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  const categories = [
    { value: "all", label: "All News" },
    { value: "earnings", label: "Earnings" },
    { value: "markets", label: "Markets" },
    { value: "analysis", label: "Analysis" },
    { value: "breaking", label: "Breaking News" }
  ];

  useEffect(() => {
    fetchNews();
  }, []);

  useEffect(() => {
    filterNews();
  }, [news, searchTerm, selectedCategory]);

  const fetchNews = async () => {
    setIsLoading(true);
    try {
      // Since the API might not have news data, simulate news feed
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockNews = [
        {
          id: 1,
          title: "Apple Reports Strong Q4 Earnings, Beats Revenue Expectations",
          summary: "Apple Inc. reported quarterly revenue of $117.2 billion, surpassing analyst expectations of $115.8 billion. iPhone sales were particularly strong in international markets.",
          source: "MarketWatch",
          category: "earnings",
          publishedAt: "2024-01-15T14:30:00Z",
          url: "https://example.com/news/1",
          tickers: ["AAPL"],
          sentiment: "positive"
        },
        {
          id: 2,
          title: "Federal Reserve Hints at Potential Rate Cut in March",
          summary: "Fed officials suggested they may consider reducing interest rates if inflation continues to moderate, providing potential relief for growth stocks.",
          source: "Reuters",
          category: "markets",
          publishedAt: "2024-01-15T13:15:00Z",
          url: "https://example.com/news/2",
          tickers: [],
          sentiment: "positive"
        },
        {
          id: 3,
          title: "Microsoft Announces Major AI Partnership with OpenAI",
          summary: "Microsoft extends its partnership with OpenAI, integrating advanced AI capabilities across its enterprise software suite, potentially boosting cloud revenue.",
          source: "TechCrunch",
          category: "analysis",
          publishedAt: "2024-01-15T11:45:00Z",
          url: "https://example.com/news/3",
          tickers: ["MSFT"],
          sentiment: "positive"
        },
        {
          id: 4,
          title: "Tesla Recalls 200,000 Vehicles Over Safety Concerns",
          summary: "Tesla is recalling Model S, X, and Y vehicles due to potential brake issues. The company says the fix will be delivered via over-the-air update.",
          source: "CNN Business",
          category: "breaking",
          publishedAt: "2024-01-15T10:20:00Z",
          url: "https://example.com/news/4",
          tickers: ["TSLA"],
          sentiment: "negative"
        },
        {
          id: 5,
          title: "NVIDIA Stock Surges on AI Chip Demand Outlook",
          summary: "NVIDIA shares jumped 8% in after-hours trading following reports of increased demand for AI chips from major cloud providers.",
          source: "Yahoo Finance",
          category: "markets",
          publishedAt: "2024-01-15T09:30:00Z",
          url: "https://example.com/news/5",
          tickers: ["NVDA"],
          sentiment: "positive"
        }
      ];

      setNews(mockNews);
    } catch (error) {
      toast.error("Failed to fetch news");
    } finally {
      setIsLoading(false);
    }
  };

  const filterNews = () => {
    let filtered = [...news];

    if (searchTerm) {
      filtered = filtered.filter(article =>
        article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.tickers.some(ticker => ticker.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter(article => article.category === selectedCategory);
    }

    setFilteredNews(filtered);
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive":
        return "bg-green-100 text-green-800";
      case "negative":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case "earnings":
        return "bg-blue-100 text-blue-800";
      case "markets":
        return "bg-purple-100 text-purple-800";
      case "analysis":
        return "bg-orange-100 text-orange-800";
      case "breaking":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatTimeAgo = (dateString) => {
    const now = new Date();
    const publishedTime = new Date(dateString);
    const diffInHours = Math.floor((now - publishedTime) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return "Just now";
    if (diffInHours === 1) return "1 hour ago";
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays === 1) return "1 day ago";
    return `${diffInDays} days ago`;
  };

  const markAsRead = async (newsId) => {
    try {
      // In a real implementation, this would call the API
      toast.success("Article marked as read");
    } catch (error) {
      toast.error("Failed to mark as read");
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          {[1, 2, 3].map(i => (
            <div key={i} className="h-32 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">News Feed</h1>
          <p className="text-gray-600 mt-2">Stay updated with the latest market news and analysis</p>
        </div>
        <Button onClick={fetchNews}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="flex flex-col lg:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search news, tickers, or topics..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-full lg:w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {categories.map((category) => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-6">
        {filteredNews.map((article) => (
          <Card key={article.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={getCategoryColor(article.category)}>
                      {article.category}
                    </Badge>
                    <Badge className={getSentimentColor(article.sentiment)}>
                      {article.sentiment}
                    </Badge>
                    {article.tickers.length > 0 && (
                      <div className="flex items-center gap-1">
                        {article.tickers.map((ticker) => (
                          <Badge key={ticker} variant="outline" className="text-xs">
                            {ticker}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <CardTitle className="text-xl leading-tight">
                    {article.title}
                  </CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4 leading-relaxed">
                {article.summary}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="font-medium">{article.source}</span>
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatTimeAgo(article.publishedAt)}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => markAsRead(article.id)}
                  >
                    Mark Read
                  </Button>
                  <Button size="sm" asChild>
                    <a 
                      href={article.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-1"
                    >
                      <ExternalLink className="h-3 w-3" />
                      Read More
                    </a>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredNews.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-gray-500 mb-4">No news found</div>
              <Button onClick={() => {
                setSearchTerm("");
                setSelectedCategory("all");
              }}>
                Clear Filters
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="mt-8 text-center">
        <Button variant="outline" onClick={fetchNews}>
          Load More Articles
        </Button>
      </div>
    </div>
  );
};

export default NewsFeed;