import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Newspaper, 
  TrendingUp, 
  TrendingDown, 
  Clock,
  RefreshCw,
  Filter,
  Search,
  ExternalLink,
  Settings,
  Bell
} from 'lucide-react';
import { 
  getNewsFeed, 
  markNewsRead, 
  markNewsClicked, 
  updateNewsPreferences,
  syncPortfolioNews
} from '../api/client';
import { Link } from 'react-router-dom';
import logger from '../lib/logger';

const RealTimeNewsFeed = ({ 
  maxItems = 20, 
  showHeader = true,
  category = null,
  autoRefresh = true 
}) => {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(category);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetchNews();
    
    if (autoRefresh) {
      // Refresh news every 5 minutes
      const interval = setInterval(fetchNews, 5 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [selectedCategory, maxItems, autoRefresh]);

  const fetchNews = async (loadMore = false) => {
    const loading = loadMore ? setIsLoadingMore : setIsLoading;
    loading(true);
    setError(null);
    
    try {
      const params = {
        limit: maxItems,
        ...(selectedCategory && { category: selectedCategory })
      };
      
      const response = await getNewsFeed(params);
      
      if (response.success && response.data?.news_items) {
        const newItems = response.data.news_items;
        
        if (loadMore) {
          // Filter out duplicates when loading more
          const existingIds = new Set(news.map(item => item.id));
          const uniqueItems = newItems.filter(item => !existingIds.has(item.id));
          setNews(prev => [...prev, ...uniqueItems]);
          setHasMore(uniqueItems.length === maxItems);
        } else {
          setNews(newItems);
          setHasMore(newItems.length === maxItems);
        }
        
        setLastUpdated(new Date());
      } else {
        if (!loadMore) setNews([]);
      }
    } catch (err) {
      setError('Failed to load news feed');
      logger.error('News feed error:', err);
    } finally {
      loading(false);
    }
  };

  const handleNewsClick = async (newsItem) => {
    try {
      // Mark news as clicked for analytics
      await markNewsClicked(newsItem.id);
      // Open news article
      window.open(newsItem.url, '_blank', 'noopener,noreferrer');
    } catch (err) {
      logger.error('Mark news clicked error:', err);
      // Still open the link even if tracking fails
      window.open(newsItem.url, '_blank', 'noopener,noreferrer');
    }
  };

  const handleMarkAsRead = async (newsId) => {
    try {
      await markNewsRead(newsId);
      setNews(prev => prev.map(item => 
        item.id === newsId ? { ...item, is_read: true } : item
      ));
    } catch (err) {
      logger.error('Mark as read error:', err);
    }
  };

  const handleSyncPortfolioNews = async () => {
    try {
      await syncPortfolioNews();
      await fetchNews(); // Refresh after sync
    } catch (err) {
      logger.error('Sync portfolio news error:', err);
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

  const filteredNews = news.filter(item =>
    !searchTerm || 
    item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.source?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const categories = [
    { value: null, label: 'All News' },
    { value: 'market', label: 'Market' },
    { value: 'earnings', label: 'Earnings' },
    { value: 'technology', label: 'Technology' },
    { value: 'finance', label: 'Finance' },
    { value: 'energy', label: 'Energy' },
    { value: 'healthcare', label: 'Healthcare' }
  ];

  if (isLoading && news.length === 0) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5" />
              Market News Feed
            </CardTitle>
            <CardDescription>Latest market news and analysis</CardDescription>
          </CardHeader>
        )}
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading news feed...</p>
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
              Market News Feed
              {lastUpdated && (
                <Badge variant="secondary" className="text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  Updated {formatTimeAgo(lastUpdated)}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>Real-time market news and analysis</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={handleSyncPortfolioNews}>
              <Bell className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => fetchNews()} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/app/news/preferences">
                <Settings className="h-4 w-4" />
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

        {/* Search and Filter Controls */}
        <div className="flex flex-col gap-4 mb-6">
          <div className="flex gap-2">
            <div className="flex-1">
              <Input
                placeholder="Search news..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button variant="outline" size="icon">
              <Search className="h-4 w-4" />
            </Button>
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <Button
                key={cat.value || 'all'}
                variant={selectedCategory === cat.value ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(cat.value)}
              >
                {cat.label}
              </Button>
            ))}
          </div>
        </div>

        {filteredNews.length > 0 ? (
          <div className="space-y-4">
            {filteredNews.map((newsItem, index) => (
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

                <div className="flex items-center justify-between">
                  {newsItem.sentiment_score !== null && newsItem.sentiment_score !== undefined && (
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>Sentiment:</span>
                      <span className={`font-medium ${
                        newsItem.sentiment_score > 0 ? 'text-green-600' : 
                        newsItem.sentiment_score < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {newsItem.sentiment_score > 0 ? '+' : ''}{newsItem.sentiment_score.toFixed(2)}
                      </span>
                    </div>
                  )}

                  {!newsItem.is_read && (
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
                  )}
                </div>
              </div>
            ))}

            {/* Load More Button */}
            {hasMore && (
              <div className="text-center pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => fetchNews(true)}
                  disabled={isLoadingMore}
                >
                  {isLoadingMore ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Load More News'
                  )}
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <Newspaper className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p>No news articles found</p>
              <p className="text-sm">
                {searchTerm ? 'Try adjusting your search terms' : 'Check back later for updates'}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RealTimeNewsFeed;