import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Input } from "../../../components/ui/input";
import { Plus, Search, Filter, TrendingUp, BarChart3, PlayCircle, Edit3, Download, Upload } from "lucide-react";
import { listScreeners, api } from "../../../api/client";

const ScreenerLibrary = () => {
  const [screeners, setScreeners] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [resultCounts, setResultCounts] = useState({});

  useEffect(() => { (async () => {
    setIsLoading(true);
    try {
      const res = await listScreeners();
      const items = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : []);
      setScreeners(items);
    } catch {
      setScreeners([]);
    } finally { setIsLoading(false); }
  })(); }, []);

  const exportJson = (s) => {
    const blob = new Blob([JSON.stringify({ name: s.name, description: s.description, isPublic: s.is_public, criteria: s.criteria || [] }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `${(s.name||'screener').replace(/\s+/g,'-').toLowerCase()}.json`; a.click(); URL.revokeObjectURL(url);
  };

  const importJsonToDraft = async (event) => {
    try {
      const file = event.target.files?.[0]; if (!file) return; const text = await file.text(); const parsed = JSON.parse(text);
      localStorage.setItem('draft_screener_import', JSON.stringify(parsed));
      window.location.hash = '#/app/screeners/new';
    } catch {}
  };

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
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <CardTitle className="text-xl">Quick Filter</CardTitle>
              <Badge variant="secondary">Default</Badge>
            </div>
            <CardDescription>Start with a new filter to scan all stocks.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-xs text-gray-500">Create a screen using the screener builder.</div>
              <div className="flex gap-2">
                <Button size="sm" className="flex-1" asChild>
                  <Link to="/app/screeners/new">
                    <TrendingUp className="h-4 w-4 mr-1" />
                    Open Screener Builder
                  </Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {filteredScreeners.map((s) => (
          <Card key={s.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-xl">{s.name || 'Untitled Screener'}</CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{s.is_public ? 'Public' : 'Private'}</Badge>
                  {resultCounts[s.id] != null && (
                    <Badge variant="secondary">{resultCounts[s.id]} results</Badge>
                  )}
                </div>
              </div>
              <CardDescription>
                {s.description || 'No description'}
                <span className="ml-2 text-xs text-gray-500">{s.last_run ? `Last run: ${new Date(s.last_run).toLocaleString()}` : 'Never run'}</span>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Button size="sm" variant="default" asChild>
                  <Link to={`/app/screeners/${s.id}/results`}>
                    <PlayCircle className="h-4 w-4 mr-1" /> Run
                  </Link>
                </Button>
                <Button size="sm" variant="outline" asChild>
                  <Link to={`/app/screeners/${s.id}/edit`}>
                    <Edit3 className="h-4 w-4 mr-1" /> Edit
                  </Link>
                </Button>
                <Button size="sm" variant="outline" onClick={() => exportJson(s)}>
                  <Download className="h-4 w-4 mr-1" /> Export JSON
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredScreeners.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">No screeners found</div>
          <div className="flex gap-2 justify-center">
            <Button asChild>
              <Link to="/app/screeners/new">Create your first Screener</Link>
            </Button>
            <label className="inline-flex items-center">
              <input type="file" accept="application/json" className="hidden" onChange={(e)=>importJsonToDraft(e)} />
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" /> Import JSON
              </Button>
            </label>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScreenerLibrary;