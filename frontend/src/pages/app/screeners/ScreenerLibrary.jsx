import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Input } from "../../../components/ui/input";
import { Plus, Search, Filter, TrendingUp, BarChart3 } from "lucide-react";
import { listScreeners } from "../../../api/client";

const ScreenerLibrary = () => {
  const [screeners, setScreeners] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => { (async () => {
    setIsLoading(true);
    try {
      const res = await listScreeners();
      const items = Array.isArray(res?.data) ? res.data : Array.isArray(res) ? res : [];
      setScreeners(items);
    } catch {
      setScreeners([]);
    } finally { setIsLoading(false); }
  })(); }, []);

  const filteredScreeners = screeners.filter(screener =>
    screener.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    screener.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock Screeners</h1>
          <p className="text-gray-600 mt-2">Find stocks that match your criteria</p>
        </div>
        <Button asChild>
          <Link to="/app/screeners/new">
            <Plus className="h-4 w-4 mr-2" />
            Create Screener
          </Link>
        </Button>
      </div>

      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search screeners..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredScreeners.map((screener) => (
          <Card key={screener.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-xl">{screener.name}</CardTitle>
                {screener.is_public && <Badge variant="secondary">Public</Badge>}
              </div>
              <CardDescription>{screener.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Criteria</div>
                    <div className="font-semibold">{screener.criteria_count ?? 0}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Matches</div>
                    <div className="font-semibold text-blue-600">{screener.matches ?? 0}</div>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  Last run: {screener.last_run ? new Date(screener.last_run).toLocaleDateString() : 'Never'}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" className="flex-1" asChild>
                    <Link to={`/app/screeners/${screener.id}/results`}>
                      <TrendingUp className="h-4 w-4 mr-1" />
                      View Results
                    </Link>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <Link to={`/app/screeners/${screener.id}/edit`}>
                      <BarChart3 className="h-4 w-4 mr-1" />
                      Edit
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredScreeners.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">No screeners found</div>
          <Button asChild>
            <Link to="/app/screeners/new">Create your first screener</Link>
          </Button>
        </div>
      )}
    </div>
  );
};

export default ScreenerLibrary;