import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Search, ExternalLink, Clock, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { getNewsFeed, markNewsRead, markNewsClicked } from "../../api/client";

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
      const res = await getNewsFeed({ limit: 20 });
      // Accept both {success, data:{news_items}} and direct arrays
      const items = res?.data?.news_items || res?.data || res?.news || [];
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
        (article.mentioned_tickers || article.tickers || [])
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
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Market News</h1>
      <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {/* news cards */}
      </div>
    </div>
  );
};

export default NewsFeed;