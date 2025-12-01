import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Alert, AlertDescription } from "../../components/ui/alert";
import {
  Eye,
  Copy,
  TrendingUp,
  TrendingDown,
  Loader2,
  AlertCircle,
  User,
  Calendar,
  List,
  Share2,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { toast } from "sonner";
import { getSharedWatchlist, copySharedWatchlist } from "../../api/client";
import SEO from "../../components/SEO";

export default function SharedWatchlist() {
  const { slug } = useParams();
  const [watchlist, setWatchlist] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copying, setCopying] = useState(false);

  useEffect(() => {
    loadWatchlist();
  }, [slug]);

  const loadWatchlist = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSharedWatchlist(slug);
      if (data?.success) {
        setWatchlist(data.watchlist || data.data);
      } else {
        setError(data?.message || "Watchlist not found");
      }
    } catch (err) {
      setError("Unable to load watchlist");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    setCopying(true);
    try {
      const result = await copySharedWatchlist(slug);
      if (result?.success) {
        toast.success("Watchlist copied to your account!");
      } else {
        toast.error(result?.message || "Failed to copy watchlist");
      }
    } catch {
      toast.error("Please sign in to copy this watchlist");
    } finally {
      setCopying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <Loader2 className="h-12 w-12 mx-auto animate-spin text-blue-500 mb-4" />
        <p className="text-gray-500">Loading shared watchlist...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12 max-w-2xl">
        <SEO title="Watchlist Not Found | Trade Scan Pro" robots="noindex" />
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="text-center mt-6">
          <Link to="/">
            <Button>Go to Homepage</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl" data-testid="shared-watchlist-page">
      <SEO 
        title={`${watchlist?.name || "Shared Watchlist"} | Trade Scan Pro`}
        description={`View shared watchlist with ${watchlist?.items?.length || 0} stocks`}
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <Badge variant="outline" className="mb-2">
              <Share2 className="h-3 w-3 mr-1" />
              Shared Watchlist
            </Badge>
            <h1 className="text-3xl font-bold text-gray-900">{watchlist?.name}</h1>
            {watchlist?.description && (
              <p className="text-gray-600 mt-2">{watchlist.description}</p>
            )}
          </div>
          <Button onClick={handleCopy} disabled={copying} className="gap-2">
            <Copy className="h-4 w-4" />
            {copying ? "Copying..." : "Copy to My Watchlists"}
          </Button>
        </div>

        {/* Meta Info */}
        <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
          {watchlist?.owner && (
            <span className="flex items-center gap-1">
              <User className="h-4 w-4" />
              {watchlist.owner.username || "Anonymous"}
            </span>
          )}
          <span className="flex items-center gap-1">
            <List className="h-4 w-4" />
            {watchlist?.items?.length || 0} stocks
          </span>
          {watchlist?.created_at && (
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {new Date(watchlist.created_at).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      {/* Stocks List */}
      <Card>
        <CardHeader>
          <CardTitle>Stocks in Watchlist</CardTitle>
          <CardDescription>Click on any stock to view details</CardDescription>
        </CardHeader>
        <CardContent>
          {watchlist?.items?.length > 0 ? (
            <div className="divide-y">
              {watchlist.items.map((item, index) => (
                <div
                  key={item.symbol || index}
                  className="py-4 flex items-center justify-between hover:bg-gray-50 px-2 rounded"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center font-bold text-blue-600">
                      {(item.symbol || "?").charAt(0)}
                    </div>
                    <div>
                      <p className="font-semibold">{item.symbol}</p>
                      <p className="text-sm text-gray-500">{item.name || "Stock"}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    {item.current_price && (
                      <p className="font-semibold">${item.current_price.toFixed(2)}</p>
                    )}
                    {item.change_percent !== undefined && (
                      <p className={`text-sm flex items-center justify-end gap-1 ${
                        item.change_percent >= 0 ? "text-green-600" : "text-red-600"
                      }`}>
                        {item.change_percent >= 0 ? (
                          <ArrowUpRight className="h-3 w-3" />
                        ) : (
                          <ArrowDownRight className="h-3 w-3" />
                        )}
                        {item.change_percent >= 0 ? "+" : ""}
                        {item.change_percent.toFixed(2)}%
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <List className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p>This watchlist is empty</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* CTA */}
      <div className="mt-8 text-center">
        <p className="text-gray-600 mb-4">Want to create your own watchlists?</p>
        <Link to="/auth/sign-up">
          <Button size="lg">Get Started Free</Button>
        </Link>
      </div>
    </div>
  );
}
