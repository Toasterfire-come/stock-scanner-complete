import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  Grid,
  Settings,
  Plus,
  Eye,
  EyeOff,
  Move,
  Trash2,
  BarChart3,
  TrendingUp,
  DollarSign,
  Target,
  Bell,
  Clock,
  Users,
  Zap,
  AlertCircle,
  Save,
  RotateCcw
} from "lucide-react";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

const DashboardCustomizer = ({ onLayoutChange, currentLayout, className = "" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [widgets, setWidgets] = useState(currentLayout || []);
  const [availableWidgets] = useState([
    {
      id: 'market-overview',
      title: 'Market Overview',
      description: 'Real-time market statistics and indices',
      icon: <TrendingUp className="h-5 w-5" />,
      category: 'Market Data',
      size: 'medium'
    },
    {
      id: 'portfolio-summary',
      title: 'Portfolio Summary',
      description: 'Your investment performance overview',
      icon: <Target className="h-5 w-5" />,
      category: 'Portfolio',
      size: 'large'
    },
    {
      id: 'watchlist-preview',
      title: 'Watchlist Preview',
      description: 'Quick view of your watched stocks',
      icon: <Eye className="h-5 w-5" />,
      category: 'Stocks',
      size: 'medium'
    },
    {
      id: 'recent-alerts',
      title: 'Recent Alerts',
      description: 'Latest price and volume alerts',
      icon: <Bell className="h-5 w-5" />,
      category: 'Alerts',
      size: 'small'
    },
    {
      id: 'top-movers',
      title: 'Top Movers',
      description: 'Biggest gainers and losers',
      icon: <BarChart3 className="h-5 w-5" />,
      category: 'Market Data',
      size: 'medium'
    },
    {
      id: 'quick-actions',
      title: 'Quick Actions',
      description: 'Fast access to common tasks',
      icon: <Zap className="h-5 w-5" />,
      category: 'Tools',
      size: 'small'
    },
    {
      id: 'market-news',
      title: 'Market News',
      description: 'Latest financial news headlines',
      icon: <AlertCircle className="h-5 w-5" />,
      category: 'News',
      size: 'large'
    },
    {
      id: 'performance-chart',
      title: 'Performance Chart',
      description: 'Portfolio performance visualization',
      icon: <BarChart3 className="h-5 w-5" />,
      category: 'Portfolio',
      size: 'large'
    }
  ]);

  const [layouts] = useState([
    {
      id: 'default',
      name: 'Default',
      description: 'Balanced layout for all users',
      widgets: ['market-overview', 'portfolio-summary', 'watchlist-preview', 'recent-alerts']
    },
    {
      id: 'trader',
      name: 'Active Trader',
      description: 'Focus on market data and alerts',
      widgets: ['market-overview', 'top-movers', 'recent-alerts', 'quick-actions', 'watchlist-preview']
    },
    {
      id: 'investor',
      name: 'Long-term Investor',
      description: 'Portfolio-focused layout',
      widgets: ['portfolio-summary', 'performance-chart', 'market-news', 'watchlist-preview']
    },
    {
      id: 'minimal',
      name: 'Minimal',
      description: 'Clean, distraction-free layout',
      widgets: ['market-overview', 'portfolio-summary', 'quick-actions']
    }
  ]);

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(widgets);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setWidgets(items);
  };

  const toggleWidget = (widgetId) => {
    const widgetExists = widgets.some(w => w.id === widgetId || w === widgetId);
    
    if (widgetExists) {
      setWidgets(widgets.filter(w => (w.id || w) !== widgetId));
    } else {
      const widgetData = availableWidgets.find(w => w.id === widgetId);
      setWidgets([...widgets, widgetData]);
    }
  };

  const applyLayout = (layoutId) => {
    const layout = layouts.find(l => l.id === layoutId);
    if (layout) {
      const layoutWidgets = layout.widgets.map(widgetId => 
        availableWidgets.find(w => w.id === widgetId)
      ).filter(Boolean);
      setWidgets(layoutWidgets);
    }
  };

  const saveLayout = () => {
    onLayoutChange(widgets);
    setIsOpen(false);
    // Here you would typically save to localStorage or send to API
    localStorage.setItem('dashboard-layout', JSON.stringify(widgets));
  };

  const resetToDefault = () => {
    applyLayout('default');
  };

  const getWidgetById = (id) => {
    return availableWidgets.find(w => w.id === id);
  };

  const isWidgetActive = (widgetId) => {
    return widgets.some(w => (w.id || w) === widgetId);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className={className}>
          <Grid className="h-4 w-4 mr-2" />
          Customize Dashboard
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Customize Your Dashboard
          </DialogTitle>
          <DialogDescription>
            Drag widgets to reorder them, toggle visibility, or apply preset layouts.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Quick Layout Templates */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Layout Templates</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {layouts.map((layout) => (
                <Card 
                  key={layout.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => applyLayout(layout.id)}
                >
                  <CardContent className="p-4 text-center">
                    <div className="font-medium text-sm">{layout.name}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {layout.description}
                    </div>
                    <Badge variant="outline" className="mt-2 text-xs">
                      {layout.widgets.length} widgets
                    </Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Current Layout */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">Current Layout</h3>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={resetToDefault}>
                  <RotateCcw className="h-4 w-4 mr-1" />
                  Reset
                </Button>
              </div>
            </div>
            
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId="dashboard-widgets">
                {(provided) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className="space-y-2 min-h-[100px] p-3 border-2 border-dashed border-gray-200 rounded-lg"
                  >
                    {widgets.length === 0 ? (
                      <div className="text-center text-muted-foreground py-8">
                        <Grid className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>No widgets selected. Add widgets from the available options below.</p>
                      </div>
                    ) : (
                      widgets.map((widget, index) => {
                        const widgetData = getWidgetById(widget.id || widget);
                        if (!widgetData) return null;
                        
                        return (
                          <Draggable key={widgetData.id} draggableId={widgetData.id} index={index}>
                            {(provided, snapshot) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                className={`flex items-center justify-between p-3 bg-white border rounded-lg transition-shadow ${
                                  snapshot.isDragging ? 'shadow-lg' : 'shadow-sm'
                                }`}
                              >
                                <div className="flex items-center gap-3">
                                  <div {...provided.dragHandleProps} className="cursor-move">
                                    <Move className="h-4 w-4 text-gray-400" />
                                  </div>
                                  {widgetData.icon}
                                  <div>
                                    <div className="font-medium">{widgetData.title}</div>
                                    <div className="text-sm text-muted-foreground">
                                      {widgetData.description}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge variant="secondary" className="text-xs">
                                    {widgetData.category}
                                  </Badge>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => toggleWidget(widgetData.id)}
                                  >
                                    <EyeOff className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            )}
                          </Draggable>
                        );
                      })
                    )}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          </div>

          {/* Available Widgets */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Available Widgets</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {availableWidgets.map((widget) => {
                const isActive = isWidgetActive(widget.id);
                return (
                  <Card 
                    key={widget.id}
                    className={`cursor-pointer transition-all ${
                      isActive 
                        ? 'opacity-50 bg-gray-50' 
                        : 'hover:shadow-md hover:scale-[1.02]'
                    }`}
                    onClick={() => !isActive && toggleWidget(widget.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {widget.icon}
                          <div>
                            <div className="font-medium">{widget.title}</div>
                            <div className="text-sm text-muted-foreground">
                              {widget.description}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {widget.category}
                          </Badge>
                          {isActive ? (
                            <Eye className="h-4 w-4 text-green-500" />
                          ) : (
                            <Plus className="h-4 w-4 text-gray-400" />
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={saveLayout}>
              <Save className="h-4 w-4 mr-2" />
              Save Layout
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DashboardCustomizer;