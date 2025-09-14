import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Search, ExternalLink, Clock, RefreshCw, ArrowUp, Newspaper } from "lucide-react";
import { toast } from "sonner";
import { getWordPressNews, markNewsRead, markNewsClicked } from "../../api/client";

const NewsFeed = () => {
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showScrollTop, setShowScrollTop] = useState(false);

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

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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

  const getSentimentColor = (sentimentScore, sentimentGrade) => {
    // Handle numeric sentiment score (from Apple news JSON structure)
    if (typeof sentimentScore === 'number') {
      if (sentimentScore > 0.3) return "bg-green-100 text-green-800 border-green-300";
      if (sentimentScore < -0.3) return "bg-red-100 text-red-800 border-red-300";
      return "bg-gray-100 text-gray-800 border-gray-300";
    }
    
    // Handle text sentiment grade
    const grade = (sentimentGrade || sentimentScore || "").toLowerCase();
    switch (grade) {
      case "a":
      case "positive":
        return "bg-green-100 text-green-800 border-green-300";
      case "d":
      case "f":
      case "negative":
        return "bg-red-100 text-red-800 border-red-300";
      case "b":
      case "c":
      case "neutral":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
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

      {/* Scrollable news container */}
      <div className="max-h-screen overflow-y-auto space-y-6 pr-2">
        {filteredNews.map((article) => (
          <Card key={article.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    {/* Category Badge */}
                    {article.category && (
                      <Badge className={getCategoryColor(article.category)}>
                        {article.category}
                      </Badge>
                    )}
                    
                    {/* Enhanced Sentiment Badge with score */}
                    {(article.sentiment_score !== undefined || article.sentiment_grade || article.sentiment) && (
                      <Badge className={getSentimentColor(article.sentiment_score, article.sentiment_grade || article.sentiment)}>
                        {article.sentiment_grade || 
                         (article.sentiment_score > 0.3 ? 'Positive' : 
                          article.sentiment_score < -0.3 ? 'Negative' : 'Neutral') || 
                         article.sentiment}
                        {article.sentiment_score !== undefined && (
                          <span className="ml-1 opacity-75">
                            ({article.sentiment_score > 0 ? '+' : ''}{article.sentiment_score.toFixed(2)})
                          </span>
                        )}
                      </Badge>
                    )}
                    
                    {/* Ticker Badges */}
                    {(
                      Array.isArray(article.mentioned_tickers) ? article.mentioned_tickers :
                      (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()).filter(Boolean))
                    )?.length > 0 && (
                      <div className="flex items-center gap-1 flex-wrap">
                        {(
                          Array.isArray(article.mentioned_tickers) ? article.mentioned_tickers :
                          (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()).filter(Boolean))
                        ).slice(0, 5).map((ticker) => (
                          <Badge key={ticker} variant="outline" className="text-xs">
                            {ticker}
                          </Badge>
                        ))}
                        {(
                          Array.isArray(article.mentioned_tickers) ? article.mentioned_tickers :
                          (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()).filter(Boolean))
                        ).length > 5 && (
                          <Badge variant="outline" className="text-xs opacity-60">
                            +{(Array.isArray(article.mentioned_tickers) ? article.mentioned_tickers : (Array.isArray(article.tickers) ? article.tickers : String(article.mentioned_tickers || article.tickers || "").split(',').map(s => s.trim()).filter(Boolean))).length - 5} more
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <CardTitle className="text-xl leading-tight hover:text-blue-600 transition-colors">
                    {article.title}
                  </CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Enhanced content display with excerpt fallback */}
              {(article.summary || article.excerpt || article.content) && (
                <p className="text-gray-600 mb-4 leading-relaxed">
                  {(article.summary || article.excerpt || article.content).substring(0, 300)}
                  {(article.summary || article.excerpt || article.content).length > 300 ? '...' : ''}
                </p>
              )}

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  {article.source && <span className="font-medium">{article.source}</span>}
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatTimeAgo(article.published_at || article.publishedAt || article.pubDate)}
                  </div>
                  {/* Show creation date if different from publish date */}
                  {article.created_at && article.created_at !== article.published_at && (
                    <div className="flex items-center gap-1 opacity-60">
                      <span>•</span>
                      <span>Added {formatTimeAgo(article.created_at)}</span>
                    </div>
                  )}
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
              <Newspaper className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="text-lg font-medium text-gray-500 mb-2">No news found</div>
              <div className="text-sm text-gray-400 mb-4">
                {searchTerm || selectedCategory !== "all" 
                  ? "Try adjusting your search or filters" 
                  : "No articles are currently available"}
              </div>
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
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
              Loading...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Load Latest Articles
            </>
          )}
        </Button>
      </div>

      {/* Scroll to top button */}
      {showScrollTop && (
        <div className="fixed bottom-6 right-6 z-50">
          <Button
            size="sm"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="rounded-full shadow-lg"
          >
            <ArrowUp className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;