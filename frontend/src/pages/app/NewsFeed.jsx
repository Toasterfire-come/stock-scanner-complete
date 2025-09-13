import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Search, ExternalLink, Clock, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { getWordPressNews, markNewsRead, markNewsClicked } from "../../api/client";

const NewsFeed = () => {
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

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
    setError("");
    try {
      // Use public WordPress news endpoint for production consistency
      const res = await getWordPressNews({ limit: 20 });
      const items = res?.data || res?.news || [];
      setNews(Array.isArray(items) ? items : []);
    } catch (err) {
      setNews([]);
      setError("Failed to fetch news");
      toast.error("Failed to fetch news");
    } finally {
      setIsLoading(false);
    }
  };

  const filterNews = () => {
    let filtered = [...news];

    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      filtered = filtered.filter((article) =>
        (article.title || "").toLowerCase().includes(q) ||
        (article.summary || "").toLowerCase().includes(q) ||
        (
          Array.isArray(article.mentioned_tickers)
            ? article.mentioned_tickers
            : (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()))
        )
          .join(",")
          .toLowerCase()
          .includes(q)
      );
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter((article) => (article.category || "").toLowerCase() === selectedCategory);
    }

    setFilteredNews(filtered);
  };

  const getSentimentColor = (sentiment) => {
    switch ((sentiment || "").toLowerCase()) {
      case "positive":
        return "bg-green-100 text-green-800";
      case "negative":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getCategoryColor = (category) => {
    switch ((category || "").toLowerCase()) {
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
    if (!dateString) return "";
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

  const onMarkRead = async (newsId) => {
    try {
      await markNewsRead(newsId);
      toast.success("Article marked as read");
    } catch {
      toast.error("Failed to mark as read");
    }
  };

  const onReadMore = async (newsId, url) => {
    try {
      await markNewsClicked(newsId);
    } catch {
      // non-blocking
    } finally {
      if (url) window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          {[1, 2, 3].map((i) => (
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
        <Button onClick={fetchNews} variant="outline">
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
            <SelectValue placeholder="Filter category" />
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

      {error && (
        <Card className="mb-4">
          <CardContent className="text-sm text-red-600 py-3">{error}</CardContent>
        </Card>
      )}

      <div className="grid gap-6">
        {filteredNews.map((article) => (
          <Card key={article.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {article.category && (
                      <Badge className={getCategoryColor(article.category)}>
                        {article.category}
                      </Badge>
                    )}
                    {article.sentiment && (
                      <Badge className={getSentimentColor(article.sentiment)}>
                        {article.sentiment}
                      </Badge>
                    )}
                    {(
                      Array.isArray(article.mentioned_tickers) ? article.mentioned_tickers :
                      (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()).filter(Boolean))
                    )?.length > 0 && (
                      <div className="flex items-center gap-1">
                        {(
                          Array.isArray(article.mentioned_tickers) ? article.mentioned_tickers :
                          (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()).filter(Boolean))
                        ).map((ticker) => (
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
              {article.summary && (
                <p className="text-gray-600 mb-4 leading-relaxed">{article.summary}</p>
              )}

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  {article.source && <span className="font-medium">{article.source}</span>}
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatTimeAgo(article.published_at || article.publishedAt)}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline" onClick={() => onMarkRead(article.id)}>
                    Mark Read
                  </Button>
                  {article.url && (
                    <Button size="sm" onClick={() => onReadMore(article.id, article.url)}>
                      <span className="flex items-center gap-1">
                        <ExternalLink className="h-3 w-3" /> Read More
                      </span>
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {!filteredNews.length && !isLoading && (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-gray-500 mb-4">No news found</div>
              <Button
                onClick={() => {
                  setSearchTerm("");
                  setSelectedCategory("all");
                  fetchNews();
                }}
                variant="outline"
              >
                Clear Filters & Reload
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="mt-8 text-center">
        <Button variant="outline" onClick={fetchNews} disabled={isLoading}>
          Load Latest Articles
        </Button>
      </div>
    </div>
  );
};

export default NewsFeed;