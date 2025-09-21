import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { 
  ExternalLink, 
  Newspaper, 
  TrendingUp, 
  TrendingDown, 
  Clock,
  RefreshCw,
  Filter,
  Search
} from 'lucide-react';
import { getStockNews, markNewsRead, markNewsClicked } from '../api/client';
import { Link } from 'react-router-dom';

const StockNewsIntegration = ({ symbol, maxItems = 10, showHeader = true }) => {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    if (symbol) {
      fetchStockNews();
      // Refresh news every 10 minutes
      const interval = setInterval(fetchStockNews, 10 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [symbol, maxItems]);

  const fetchStockNews = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getStockNews(symbol);
      if (response.success && response.data?.news_items?.length) {
        setNews(response.data.news_items.slice(0, maxItems));
        setLastUpdated(new Date());
        return;
      }
      // Fallback: fetch from Yahoo Finance in-browser
      try {
        const html = await fetch(`https://finance.yahoo.com/quote/${encodeURIComponent(symbol)}/news/`, { mode: 'cors' }).then(r => r.text());
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const cards = Array.from(doc.querySelectorAll('h3 a, a[href*="/news/"]')).slice(0, 12);
        const items = [];
        const seen = new Set();
        for (const a of cards) {
          const href = a.getAttribute('href') || '';
          const title = (a.textContent || '').trim();
          if (!title || seen.has(title)) continue;
          seen.add(title);
          const url = href.startsWith('http') ? href : `https://finance.yahoo.com${href}`;
          items.push({ id: url, title, url, source: 'Yahoo Finance', published_at: new Date().toISOString() });
          if (items.length >= maxItems) break;
        }
        setNews(items);
        setLastUpdated(new Date());
      } catch (_) {
        setNews([]);
      }
    } catch (err) {
      setError(`Failed to load news for ${symbol}`);
      console.error('Stock news error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewsClick = async (newsItem) => {
    try {
      // Mark news as clicked for analytics (only if ID is numeric from backend DB)
      const numericId = Number(newsItem.id);
      if (Number.isFinite(numericId)) {
        await markNewsClicked(numericId);
      }
      // Open news article
      window.open(newsItem.url, '_blank', 'noopener,noreferrer');
    } catch (err) {
      console.error('Mark news clicked error:', err);
      // Still open the link even if tracking fails
      window.open(newsItem.url, '_blank', 'noopener,noreferrer');
    }
  };

  const handleMarkAsRead = async (newsId) => {
    try {
      const numericId = Number(newsId);
      if (Number.isFinite(numericId)) {
        await markNewsRead(numericId);
        setNews(prev => prev.map(item => 
          item.id === newsId ? { ...item, is_read: true } : item
        ));
      }
    } catch (err) {
      console.error('Mark as read error:', err);
    }
  };

  const getSentimentColor = (sentimentGrade) => {
    switch (sentimentGrade?.toLowerCase()) {
      case 'positive':
        return 'text-green-600 bg-green-100';
      case 'negative':  
        return 'text-red-600 bg-red-100';
      case 'neutral':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSentimentIcon = (sentimentGrade) => {
    switch (sentimentGrade?.toLowerCase()) {
      case 'positive':
        return <TrendingUp className="h-3 w-3" />;
      case 'negative':
        return <TrendingDown className="h-3 w-3" />;
      default:
        return <Clock className="h-3 w-3" />;
    }
  };

  const formatTimeAgo = (publishedAt) => {
    if (!publishedAt) return 'Unknown time';
    
    const date = new Date(publishedAt);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  if (!symbol) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-gray-500">
            <Newspaper className="h-8 w-8 mx-auto mb-2 text-gray-400" />
            <p>Select a stock to view related news</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading && news.length === 0) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5" />
              News for {symbol}
            </CardTitle>
            <CardDescription>Latest news and analysis</CardDescription>
          </CardHeader>
        )}
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading news...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      {showHeader && (
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5" />
              News for {symbol}
              {lastUpdated && (
                <Badge variant="secondary" className="text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  {formatTimeAgo(lastUpdated)}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>Latest news and market sentiment</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={fetchStockNews} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/app/news">
                <Search className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </CardHeader>
      )}
      
      <CardContent>
        {error && (
          <Alert className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {news.length > 0 ? (
          <div className="space-y-4">
            {news.map((newsItem, index) => (
              <div 
                key={newsItem.id || index} 
                className={`p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer ${
                  newsItem.is_read ? 'opacity-70' : ''
                }`}
                onClick={() => handleNewsClick(newsItem)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {newsItem.sentiment_grade && (
                      <Badge 
                        variant="secondary" 
                        className={`text-xs ${getSentimentColor(newsItem.sentiment_grade)}`}
                      >
                        {getSentimentIcon(newsItem.sentiment_grade)}
                        <span className="ml-1">{newsItem.sentiment_grade}</span>
                      </Badge>
                    )}
                    {newsItem.source && (
                      <Badge variant="outline" className="text-xs">
                        {newsItem.source}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">
                      {formatTimeAgo(newsItem.published_at)}
                    </span>
                    <ExternalLink className="h-3 w-3 text-gray-400" />
                  </div>
                </div>
                
                <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                  {newsItem.title}
                </h4>
                
                {newsItem.content && (
                  <p className="text-sm text-gray-600 line-clamp-3 mb-2">
                    {newsItem.content}
                  </p>
                )}

                {newsItem.sentiment_score !== null && newsItem.sentiment_score !== undefined && (
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>Sentiment Score:</span>
                    <span className={`font-medium ${
                      newsItem.sentiment_score > 0 ? 'text-green-600' : 
                      newsItem.sentiment_score < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {newsItem.sentiment_score > 0 ? '+' : ''}{newsItem.sentiment_score.toFixed(2)}
                    </span>
                  </div>
                )}

                {!newsItem.is_read && (
                  <div className="mt-2">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMarkAsRead(newsItem.id);
                      }}
                    >
                      Mark as Read
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <Newspaper className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p>No news available for {symbol}</p>
              <p className="text-sm">Check back later for updates</p>
            </div>
          </div>
        )}

        {news.length >= maxItems && (
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm" asChild>
              <Link to={`/app/news?symbol=${symbol}`}>
                View All News for {symbol}
                <ExternalLink className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StockNewsIntegration;