import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Input } from "../../components/ui/input";
import { Search, TrendingUp, DollarSign, Target, Zap, Star } from "lucide-react";
import { toast } from "sonner";
import { getScreenerTemplates, createScreener } from "../../api/client";

const Templates = () => {
  const [templates, setTemplates] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const templateCategories = [
    { id: "growth", name: "Growth", icon: TrendingUp, color: "text-green-600" },
    { id: "value", name: "Value", icon: DollarSign, color: "text-blue-600" },
    { id: "dividend", name: "Dividend", icon: Target, color: "text-purple-600" },
    { id: "momentum", name: "Momentum", icon: Zap, color: "text-orange-600" }
  ];

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    setIsLoading(true);
    try {
      const res = await getScreenerTemplates();
      const items = Array.isArray(res?.data) ? res.data : Array.isArray(res) ? res : [];
      setTemplates(items);
    } catch (error) {
      toast.error("Failed to fetch templates");
      setTemplates([]);
    } finally { setIsLoading(false); }
  };

  const useTemplate = async (templateId) => {
    try {
      const template = templates.find(t => t.id === templateId);
      if (!template) throw new Error('Template not found');
      const payload = { name: template.name, description: template.description, criteria: template.criteria, isPublic: false };
      await createScreener(payload);
      toast.success("Template applied! Redirecting to screener...");
    } catch (error) {
      toast.error("Failed to apply template");
    }
  };

  const filteredTemplates = templates.filter(template =>
    template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getCategoryIcon = (category) => {
    const cat = templateCategories.find(c => c.id === category);
    if (!cat) return TrendingUp;
    return cat.icon;
  };

  const getCategoryColor = (category) => {
    const cat = templateCategories.find(c => c.id === category);
    return cat?.color || "text-gray-600";
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Screener Templates</h1>
          <p className="text-gray-600 mt-2">Pre-built screening strategies from market experts</p>
        </div>
        <Button asChild>
          <Link to="/app/screeners/new">Create Custom Screener</Link>
        </Button>
      </div>

      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="mb-8">
        <div className="flex flex-wrap gap-4">
          {templateCategories.map((category) => {
            const Icon = category.icon;
            const count = templates.filter(t => t.category === category.id).length;
            return (
              <Badge key={category.id} variant="outline" className="px-4 py-2">
                <Icon className={`h-4 w-4 mr-2 ${category.color}`} />
                {category.name} ({count})
              </Badge>
            );
          })}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredTemplates.map((template) => {
          const Icon = getCategoryIcon(template.category);
          return (
            <Card key={template.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-5 w-5 ${getCategoryColor(template.category)}`} />
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                  </div>
                  {template.isPopular && (
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                      <Star className="h-3 w-3 mr-1" />
                      Popular
                    </Badge>
                  )}
                </div>
                <CardDescription>{template.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Expected Matches</div>
                      <div className="font-semibold text-blue-600">{template.expectedMatches}</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Popularity</div>
                      <div className="font-semibold">{template.popularity}%</div>
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-gray-500 mb-2">Key Criteria:</div>
                    <div className="space-y-1">
          {(template.criteria || []).slice(0, 2).map((criterion, index) => (
                        <div key={index} className="text-xs bg-gray-100 rounded px-2 py-1">
                          {criterion}
                        </div>
                      ))}
                      {template.criteria.length > 2 && (
                        <div className="text-xs text-gray-500">
                          +{template.criteria.length - 2} more criteria
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button 
                      size="sm" 
                      className="flex-1"
                      onClick={() => useTemplate(template.id)}
                    >
                      Use Template
                    </Button>
                    <Button size="sm" variant="outline" asChild>
                      <Link to={`/app/screeners/new?template=${template.id}`}>
                        Customize
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">No templates found matching your search</div>
          <Button onClick={() => setSearchTerm("")}>Clear Search</Button>
        </div>
      )}
    </div>
  );
};

export default Templates;