import React, { useEffect, useMemo, useRef, useState } from 'react';
import SEO from '../../components/SEO';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Newspaper, RefreshCw, Search, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../../components/ui/select';
import { getAllNews } from '../../api/client';

const NewsFeed = () => {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [sort, setSort] = useState('recent');
  const pageSize = 20;

  useEffect(() => {
    let mounted = true;
    (async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await getAllNews({ page, limit: pageSize, sort });
        const raws = res?.data?.news_items || [];
        const totalCount = Number(res?.total_count || raws.length);
        if (mounted) {
          setItems(raws);
          setTotal(totalCount);
        }
      } catch (e) {
        if (mounted) setError('Failed to load news');
      } finally {
        if (mounted) setIsLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [page, sort]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const getPageWindow = () => {
    if (totalPages <= 3) return Array.from({ length: totalPages }, (_, i) => i + 1);
    if (page <= 2) return [1, 2, 3];
    if (page >= totalPages - 1) return [totalPages - 2, totalPages - 1, totalPages];
    return [page - 1, page, page + 1];
  };

  const filtered = useMemo(() => {
    if (!searchTerm.trim()) return items;
    const q = searchTerm.toLowerCase();
    return items.filter(n =>
      (n.title || '').toLowerCase().includes(q) ||
      (n.content || '').toLowerCase().includes(q) ||
      (n.source || '').toLowerCase().includes(q)
    );
  }, [items, searchTerm]);

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

  const getSentimentInfo = (grade, score) => {
    const g = (grade || '').toString().toLowerCase();
    if (g.includes('bull') || g.startsWith('p') || g.startsWith('pos')) {
      return { label: 'Bullish', className: 'bg-green-50 text-green-700 border-green-200' };
    }
    if (g.includes('bear') || g.startsWith('neg')) {
      return { label: 'Bearish', className: 'bg-red-50 text-red-700 border-red-200' };
    }
    return { label: 'Neutral', className: 'bg-gray-50 text-gray-700 border-gray-200' };
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <SEO title="Market News | Trade Scan Pro" robots="noindex,follow" />
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Market News</h1>
          <p className="text-gray-600">Latest headlines and analysis from multiple sources</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>All News</span>
              <div className="flex gap-2 items-center">
                <div className="relative">
                  <Input
                    placeholder="Search news..."
                    value={searchTerm}
                    onChange={(e) => { setPage(1); setSearchTerm(e.target.value); }}
                    className="pr-8"
                  />
                  <Search className="h-4 w-4 text-gray-400 absolute right-2 top-2.5" />
                </div>
                <div className="w-48">
                  <Select value={sort} onValueChange={(v) => { setPage(1); setSort(v); }}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="recent">Most Recent</SelectItem>
                      <SelectItem value="sentiment_desc">Most Bullish</SelectItem>
                      <SelectItem value="sentiment_asc">Most Bearish</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button variant="outline" size="sm" onClick={() => { setIsLoading(true); setPage(1); }} disabled={isLoading}>
                  <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </CardTitle>
            <CardDescription>Showing page {page} of {totalPages}</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert className="mb-4"><AlertDescription>{error}</AlertDescription></Alert>
            )}

            {isLoading ? (
              <div className="text-center py-10 text-gray-500">Loading news...</div>
            ) : (
              <div className="space-y-4">
                {filtered.map((n, i) => (
                  <div key={n.id || i} className="p-4 border rounded-lg bg-white hover:bg-gray-50">
                    <div className="flex items-start justify-between mb-2">
                      <div className="text-xs text-gray-500 flex items-center gap-2">
                        <Badge variant="outline">{n.source || 'Unknown'}</Badge>
                        <span>{formatTimeAgo(n.published_at)}</span>
                      </div>
                      <a href={n.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center text-xs">
                        Open <ExternalLink className="h-3 w-3 ml-1" />
                      </a>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">{n.title}</h3>
                    <div className="mt-2 flex items-center flex-wrap gap-2">
                      {(() => { const info = getSentimentInfo(n.sentiment_grade, n.sentiment_score); return (
                        <Badge variant="outline" className={info.className}>
                          {info.label}{Number.isFinite(Number(n.sentiment_score)) ? ` ${Number(n.sentiment_score).toFixed(2)}` : ''}
                        </Badge>
                      ); })()}
                      {(Array.isArray(n.tickers) ? n.tickers : []).slice(0, 6).map((t, idx) => (
                        <Link key={`${t}-${idx}`} to={`/app/stocks/${encodeURIComponent(t)}`}>
                          <Badge variant="secondary" className="cursor-pointer">{(t || '').toUpperCase()}</Badge>
                        </Link>
                      ))}
                      {Array.isArray(n.tickers) && n.tickers.length > 6 && (
                        <span className="text-xs text-gray-500">+{n.tickers.length - 6} more</span>
                      )}
                    </div>
                    {n.content && <p className="text-sm text-gray-700 line-clamp-3">{n.content}</p>}
                  </div>
                ))}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-6">
                    <div className="text-sm text-gray-600">Page {page} of {totalPages}</div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" disabled={page===1} onClick={() => setPage(p=>Math.max(1,p-1))}>Previous</Button>
                      {getPageWindow().map(p => (
                        <Button key={p} variant={p===page? 'default':'outline'} size="sm" onClick={() => setPage(p)}>{p}</Button>
                      ))}
                      <Button variant="outline" size="sm" disabled={page===totalPages} onClick={() => setPage(p=>Math.min(totalPages,p+1))}>Next</Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default NewsFeed;