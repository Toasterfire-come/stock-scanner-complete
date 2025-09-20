import React, { useState } from "react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Plus,
  Search,
  Bell,
  Eye,
  Target,
  TrendingUp,
  Zap,
  BarChart3,
  Star,
  AlertCircle
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/SecureAuthContext";

const QuickActions = ({ className = "", variant = "floating" }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const quickActions = [
    {
      name: "Create Screener",
      description: "Build a custom stock screener",
      icon: <Search className="h-5 w-5" />,
      href: "/app/screeners/new",
      color: "bg-blue-500 hover:bg-blue-600",
      requiresAuth: true
    },
    {
      name: "Add to Watchlist",
      description: "Monitor stocks you're interested in",
      icon: <Eye className="h-5 w-5" />,
      href: "/app/watchlists",
      color: "bg-green-500 hover:bg-green-600",
      requiresAuth: true
    },
    {
      name: "Set Price Alert",
      description: "Get notified when stocks hit target prices",
      icon: <Bell className="h-5 w-5" />,
      href: "/app/alerts",
      color: "bg-orange-500 hover:bg-orange-600",
      requiresAuth: true
    },
    {
      name: "View Portfolio",
      description: "Check your investment performance",
      icon: <Target className="h-5 w-5" />,
      href: "/app/portfolio",
      color: "bg-purple-500 hover:bg-purple-600",
      requiresAuth: true
    },
    {
      name: "Market Overview",
      description: "See what's happening in the markets",
      icon: <TrendingUp className="h-5 w-5" />,
      href: "/app/markets",
      color: "bg-indigo-500 hover:bg-indigo-600",
      requiresAuth: false
    },
    {
      name: "Try Free Plan",
      description: "Start your trading journey today",
      icon: <Star className="h-5 w-5" />,
      href: "/auth/sign-up",
      color: "bg-yellow-500 hover:bg-yellow-600",
      requiresAuth: false,
      hideWhenAuth: true
    }
  ];

  const availableActions = quickActions.filter(action => {
    if (!isAuthenticated && action.requiresAuth) return false;
    if (isAuthenticated && action.hideWhenAuth) return false;
    return true;
  });

  const handleActionClick = (action) => {
    setIsOpen(false);
    navigate(action.href);
  };

  if (variant === "floating") {
    return (
      <div className={`fixed bottom-6 right-6 z-40 ${className}`}>
        <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              size="lg"
              className="h-14 w-14 rounded-full shadow-lg bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 border-0"
            >
              <Plus className="h-6 w-6" />
              <span className="sr-only">Quick Actions</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent 
            align="end" 
            side="top"
            className="w-80 p-2"
            sideOffset={10}
          >
            <DropdownMenuLabel className="flex items-center gap-2 text-base font-semibold">
              <Zap className="h-4 w-4 text-blue-600" />
              Quick Actions
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            
            <div className="grid grid-cols-1 gap-1">
              {availableActions.map((action, index) => (
                <DropdownMenuItem
                  key={index}
                  className="p-3 cursor-pointer focus:bg-gray-50 rounded-lg"
                  onClick={() => handleActionClick(action)}
                >
                  <div className="flex items-center space-x-3 w-full">
                    <div className={`p-2 rounded-lg text-white ${action.color}`}>
                      {action.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {action.name}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </DropdownMenuItem>
              ))}
            </div>

            {!isAuthenticated && (
              <>
                <DropdownMenuSeparator />
                <div className="p-3 bg-blue-50 rounded-lg m-1">
                  <div className="flex items-center gap-2 text-blue-800 text-sm">
                    <AlertCircle className="h-4 w-4" />
                    <span className="font-medium">Sign in for more actions</span>
                  </div>
                </div>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    );
  }

  // Horizontal variant for dashboard/header
  if (variant === "horizontal") {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        {availableActions.slice(0, 4).map((action, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            asChild
            className="h-9 px-3"
          >
            <Link to={action.href} className="flex items-center gap-1.5">
              {action.icon}
              <span className="hidden sm:inline">{action.name}</span>
            </Link>
          </Button>
        ))}
        
        {availableActions.length > 4 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-9 px-3">
                <Plus className="h-4 w-4" />
                <span className="hidden sm:inline ml-1">More</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {availableActions.slice(4).map((action, index) => (
                <DropdownMenuItem key={index} asChild>
                  <Link to={action.href} className="flex items-center gap-2">
                    {action.icon}
                    {action.name}
                  </Link>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    );
  }

  return null;
};

export default QuickActions;