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
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Templates</h1>
      <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {/* template cards */}
      </div>
    </div>
  );
};

export default Templates;