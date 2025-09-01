import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Input } from "../../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Skeleton } from "../../../components/ui/skeleton";
import { toast } from "sonner";
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical, 
  Play,
  Edit,
  Copy,
  Trash2,
  Star,
  TrendingUp,
  BarChart3,
  Target,
  Calendar,
  Users
} from "lucide-react";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "../../../components/ui/dropdown-menu";

const ScreenerLibrary = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [screeners, setScreeners] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortBy, setSortBy] = useState("recent");

  useEffect(() => {
    const fetchScreeners = async () => {
      try {
        // Mock screener data since this endpoint isn't in the Django API spec
        setScreeners([
          {
            id: "1",
            name: "High Growth Tech Stocks",
            description: "Technology companies with revenue growth > 25% and P/E < 30",
            category: "Growth",
            criteria_count: 8,
            results_count: 47,
            last_run: "2024-03-15T10:30:00Z",
            created_at: "2024-03-01T09:00:00Z",
            is_favorite: true,
            is_public: false,
            tags: ["tech", "growth", "high-volume"]
          },
          {
            id: "2", 
            name: "Value Dividend Stocks",
            description: "Undervalued stocks with dividend yield > 3% and P/B < 1.5",
            category: "Value",
            criteria_count: 6,
            results_count: 89,
            last_run: "2024-03-14T15:45:00Z",
            created_at: "2024-02-28T14:20:00Z",
            is_favorite: false,
            is_public: true,
            tags: ["dividend", "value", "income"]
          },
          {
            id: "3",
            name: "Small Cap Momentum",
            description: "Small cap stocks with strong price momentum and increasing volume",
            category: "Momentum",
            criteria_count: 10,
            results_count: 23,
            last_run: "2024-03-15T09:15:00Z",
            created_at: "2024-03-10T11:30:00Z",
            is_favorite: true,
            is_public: false,
            tags: ["small-cap", "momentum", "breakout"]
          },
          {
            id: "4",
            name: "Low Volatility Blue Chips",
            description: "Large cap stocks with low beta, stable earnings, and strong balance sheets",
            category: "Quality",
            criteria_count: 12,
            results_count: 156,
            last_run: "2024-03-13T16:00:00Z",
            created_at: "2024-02-15T10:45:00Z",
            is_favorite: false,
            is_public: true,
            tags: ["blue-chip", "low-volatility", "defensive"]
          }
        ]);
      } catch (error) {
        toast.error("Failed to load screeners");
      } finally {
        setIsLoading(false);
      }
    };

    fetchScreeners();
  }, []);

  const handleRunScreener = (screenerId) => {
    toast.success("Running screener...");
    // In real app, would trigger screener execution
  };

  const handleDeleteScreener = (screenerId) => {
    setScreeners(prev => prev.filter(s => s.id !== screenerId));
    toast.success("Screener deleted");
  };

  const handleToggleFavorite = (screenerId) => {
    setScreeners(prev => prev.map(s => 
      s.id === screenerId ? { ...s, is_favorite: !s.is_favorite } : s
    ));
  };

  const filteredScreeners = screeners.filter(screener => {
    const matchesSearch = screener.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         screener.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         screener.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = categoryFilter === "all" || screener.category.toLowerCase() === categoryFilter.toLowerCase();
    
    return matchesSearch && matchesCategory;
  });

  const sortedScreeners = [...filteredScreeners].sort((a, b) => {
    switch (sortBy) {
      case "name":
        return a.name.localeCompare(b.name);
      case "results":
        return b.results_count - a.results_count;
      case "recent":
        return new Date(b.last_run) - new Date(a.last_run);
      case "created":
        return new Date(b.created_at) - new Date(a.created_at);
      default:
        return 0;
    }
  });

  const getCategoryIcon = (category) => {
    switch (category.toLowerCase()) {
      case 'growth':
        return <TrendingUp className="h-4 w-4" />;
      case 'value':
        return <Target className="h-4 w-4" />;
      case 'momentum':
        return <BarChart3 className="h-4 w-4" />;
      default:
        return <Filter className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-10 w-32" />
          </div>
          
          <div className="grid gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-2">
                      <Skeleton className="h-6 w-64" />
                      <Skeleton className="h-4 w-96" />
                      <div className="flex space-x-2">
                        <Skeleton className="h-5 w-16" />
                        <Skeleton className="h-5 w-20" />
                        <Skeleton className="h-5 w-18" />
                      </div>
                    </div>
                    <Skeleton className="h-10 w-24" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Stock Screeners</h1>
            <p className="text-gray-600 mt-2">
              Create and manage custom stock screening strategies
            </p>
          </div>
          
          <Button asChild>
            <Link to="/app/screeners/new">
              <Plus className="h-4 w-4 mr-2" />
              New Screener
            </Link>
          </Button>
        </div>

        {/* Filters and Search */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search screeners, descriptions, or tags..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="growth">Growth</SelectItem>
                  <SelectItem value="value">Value</SelectItem>
                  <SelectItem value="momentum">Momentum</SelectItem>
                  <SelectItem value="quality">Quality</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="recent">Recently Run</SelectItem>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="results">Result Count</SelectItem>
                  <SelectItem value="created">Date Created</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Screeners List */}
        <div className="space-y-4">
          {sortedScreeners.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Filter className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {searchTerm || categoryFilter !== "all" ? "No screeners found" : "No screeners yet"}
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || categoryFilter !== "all" 
                    ? "Try adjusting your search or filters"
                    : "Create your first stock screener to get started"
                  }
                </p>
                <Button asChild>
                  <Link to="/app/screeners/new">
                    <Plus className="h-4 w-4 mr-2" />
                    Create Screener
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            sortedScreeners.map((screener) => (
              <Card key={screener.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <button
                          onClick={() => handleToggleFavorite(screener.id)}
                          className={`transition-colors ${
                            screener.is_favorite ? 'text-yellow-500' : 'text-gray-300 hover:text-yellow-500'
                          }`}
                        >
                          <Star className={`h-5 w-5 ${screener.is_favorite ? 'fill-current' : ''}`} />
                        </button>
                        
                        <Link 
                          to={`/app/screeners/${screener.id}/results`}
                          className="text-xl font-semibold text-gray-900 hover:text-blue-600"
                        >
                          {screener.name}
                        </Link>
                        
                        <Badge variant="secondary" className="flex items-center">
                          {getCategoryIcon(screener.category)}
                          <span className="ml-1">{screener.category}</span>
                        </Badge>
                        
                        {screener.is_public && (
                          <Badge variant="outline" className="flex items-center">
                            <Users className="h-3 w-3 mr-1" />
                            Public
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-gray-600 mb-3">{screener.description}</p>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{screener.criteria_count} criteria</span>
                        <span>•</span>
                        <span className="text-blue-600 font-medium">{screener.results_count} matches</span>
                        <span>•</span>
                        <span className="flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          Last run {new Date(screener.last_run).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2 mt-3">
                        {screener.tags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <Button
                        onClick={() => handleRunScreener(screener.id)}
                        className="flex items-center"
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Run
                      </Button>
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link to={`/app/screeners/${screener.id}/results`}>
                              <BarChart3 className="h-4 w-4 mr-2" />
                              View Results
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <Link to={`/app/screeners/${screener.id}/edit`}>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => toast.info("Copy feature coming soon")}>
                            <Copy className="h-4 w-4 mr-2" />
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={() => handleDeleteScreener(screener.id)}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{screeners.length}</div>
              <div className="text-sm text-gray-600">Total Screeners</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {screeners.filter(s => s.is_favorite).length}
              </div>
              <div className="text-sm text-gray-600">Favorites</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {screeners.reduce((sum, s) => sum + s.results_count, 0)}
              </div>
              <div className="text-sm text-gray-600">Total Matches</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {screeners.filter(s => s.is_public).length}
              </div>
              <div className="text-sm text-gray-600">Public</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ScreenerLibrary;