import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTradingMode } from '../context/TradingModeContext';
import { cn } from '../lib/utils';
import {
  LayoutDashboard,
  Search,
  CandlestickChart,
  Bell,
  Eye,
  TrendingUp,
  FileSearch,
  Calculator,
  Briefcase,
  PieChart,
} from 'lucide-react';

const iconMap = {
  LayoutDashboard,
  Search,
  CandlestickChart,
  Bell,
  Eye,
  TrendingUp,
  FileSearch,
  Calculator,
  Briefcase,
  PieChart,
};

export default function ModeAwareNavigation({ collapsed = false, className }) {
  const { config, isDayTrade } = useTradingMode();
  const location = useLocation();

  return (
    <nav className={cn("space-y-1", className)} data-testid="mode-aware-navigation">
      {config.navigation.map((item) => {
        const Icon = iconMap[item.icon] || LayoutDashboard;
        const isActive = location.pathname === item.href || 
          (item.href !== '/app/dashboard' && location.pathname.startsWith(item.href));

        return (
          <Link
            key={item.href}
            to={item.href}
            data-testid={`nav-link-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all",
              isActive
                ? isDayTrade
                  ? "bg-amber-100 text-amber-900"
                  : "bg-blue-100 text-blue-900"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            )}
          >
            <Icon className={cn(
              "h-5 w-5 flex-shrink-0",
              isActive
                ? isDayTrade ? "text-amber-600" : "text-blue-600"
                : "text-gray-400"
            )} />
            {!collapsed && <span>{item.name}</span>}
          </Link>
        );
      })}
    </nav>
  );
}
