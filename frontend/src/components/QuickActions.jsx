import React, { useState } from "react";
import { Button } from "./ui/button";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Plus, Menu, Zap, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/SecureAuthContext";

const QuickActions = ({ className = "", variant = "floating" }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const actions = [
    { name: "Create Screener", href: "/app/screeners/new", requiresAuth: true },
    { name: "Add to Watchlist", href: "/app/watchlists", requiresAuth: true },
    { name: "Set Price Alert", href: "/app/alerts", requiresAuth: true },
    { name: "View Portfolio", href: "/app/portfolio", requiresAuth: true },
    { name: "Market Overview", href: "/app/markets", requiresAuth: false },
  ];

  const available = actions.filter(a => (isAuthenticated || !a.requiresAuth));
  const handleGo = (href) => { setIsOpen(false); navigate(href); };

  // Single hamburger menu for all variants
  return (
    <div className={`z-40 ${variant === 'floating' ? 'fixed bottom-6 right-6' : ''} ${className}`}>
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            size={variant === 'floating' ? 'lg' : 'sm'}
            className={`${variant === 'floating' ? 'h-14 w-14 rounded-full shadow-lg' : 'h-9 px-3'} bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 border-0`}
          >
            {variant === 'floating' ? <Plus className="h-6 w-6" /> : <Menu className="h-4 w-4" />}
            <span className="sr-only">Quick Actions</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" side={variant === 'floating' ? 'top' : 'bottom'} className="w-72 p-2 max-h-80 overflow-y-auto" sideOffset={10}>
          <DropdownMenuLabel className="flex items-center gap-2 text-base font-semibold">
            <Zap className="h-4 w-4 text-blue-600" /> Quick Actions
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          {available.map((a) => (
            <DropdownMenuItem key={a.name} className="p-3 cursor-pointer rounded-lg" onClick={() => handleGo(a.href)}>
              {a.name}
            </DropdownMenuItem>
          ))}
          {!isAuthenticated && (
            <>
              <DropdownMenuSeparator />
              <div className="p-3 bg-blue-50 rounded-lg m-1 text-sm text-blue-800 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" /> Sign in for more actions
              </div>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default QuickActions;