import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { 
  ChevronRight, 
  Home, 
  TrendingUp, 
  BarChart3, 
  Search,
  Bell,
  User,
  Settings,
  Activity
} from 'lucide-react';

const Breadcrumb = ({ items = [], className, ...props }) => {
  return (
    <nav className={cn('flex items-center space-x-2 text-sm', className)} {...props}>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <ChevronRight className="h-4 w-4 text-gray-400" />
          )}
          {item.href && !item.current ? (
            <Link
              to={item.href}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className={cn(
              item.current ? 'text-gray-900 font-medium' : 'text-gray-500'
            )}>
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

const NavigationMenu = ({ 
  items = [], 
  orientation = 'horizontal',
  variant = 'default',
  className,
  ...props 
}) => {
  const location = useLocation();
  
  const isActiveRoute = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  const orientationClasses = {
    horizontal: 'flex items-center space-x-1',
    vertical: 'flex flex-col space-y-1'
  };

  const variantClasses = {
    default: '',
    pills: 'bg-gray-100 rounded-xl p-1',
    underline: 'border-b border-gray-200'
  };

  return (
    <nav 
      className={cn(
        orientationClasses[orientation],
        variantClasses[variant],
        className
      )} 
      {...props}
    >
      {items.map((item, index) => {
        const Icon = item.icon;
        const isActive = isActiveRoute(item.href);
        
        return (
          <Link
            key={index}
            to={item.href}
            className={cn(
              'flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200',
              'hover:bg-white hover:shadow-sm',
              isActive
                ? 'bg-white text-primary shadow-sm border border-primary/20'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            {Icon && <Icon className="w-4 h-4" />}
            <span>{item.label}</span>
            {item.badge && (
              <span className="ml-auto bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                {item.badge}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
};

const TabNavigation = ({ 
  tabs = [], 
  activeTab, 
  onTabChange,
  variant = 'default',
  size = 'md',
  className,
  ...props 
}) => {
  const variants = {
    default: 'border-b border-gray-200',
    pills: 'bg-gray-100 rounded-xl p-1',
    cards: 'space-x-2'
  };

  const sizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={cn(variants[variant], className)} {...props}>
      <div className="flex items-center space-x-1">
        {tabs.map((tab, index) => {
          const isActive = activeTab === tab.value;
          
          return (
            <button
              key={index}
              onClick={() => onTabChange(tab.value)}
              className={cn(
                'flex items-center space-x-2 px-4 py-2 font-medium transition-all duration-200',
                sizes[size],
                variant === 'default' && [
                  'border-b-2 -mb-px',
                  isActive 
                    ? 'border-primary text-primary' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ],
                variant === 'pills' && [
                  'rounded-lg',
                  isActive 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                ],
                variant === 'cards' && [
                  'rounded-xl border',
                  isActive 
                    ? 'bg-white border-primary text-primary shadow-sm' 
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-white hover:border-gray-300'
                ]
              )}
              disabled={tab.disabled}
            >
              {tab.icon && <tab.icon className="w-4 h-4" />}
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={cn(
                  'text-xs px-2 py-1 rounded-full',
                  isActive ? 'bg-primary/10 text-primary' : 'bg-gray-200 text-gray-600'
                )}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

const SidebarNavigation = ({ 
  sections = [], 
  collapsed = false,
  className,
  ...props 
}) => {
  const location = useLocation();
  
  const isActiveRoute = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  return (
    <nav className={cn('space-y-6', className)} {...props}>
      {sections.map((section, sectionIndex) => (
        <div key={sectionIndex}>
          {section.title && !collapsed && (
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              {section.title}
            </h3>
          )}
          <div className="space-y-1">
            {section.items.map((item, itemIndex) => {
              const Icon = item.icon;
              const isActive = isActiveRoute(item.href);
              
              return (
                <Link
                  key={itemIndex}
                  to={item.href}
                  className={cn(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-xl transition-all duration-200',
                    collapsed ? 'justify-center' : 'space-x-3',
                    isActive
                      ? 'bg-primary/10 text-primary border-r-2 border-primary'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  )}
                  title={collapsed ? item.label : undefined}
                >
                  {Icon && (
                    <Icon className={cn(
                      'flex-shrink-0',
                      collapsed ? 'w-6 h-6' : 'w-5 h-5'
                    )} />
                  )}
                  {!collapsed && (
                    <>
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );
};

const MobileNavigation = ({ 
  isOpen, 
  onClose, 
  items = [],
  className,
  ...props 
}) => {
  const location = useLocation();
  
  const isActiveRoute = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      {/* Mobile Menu */}
      <div className={cn(
        'fixed top-0 right-0 bottom-0 w-80 bg-white shadow-2xl z-50 overflow-y-auto',
        'transform transition-transform duration-300 ease-in-out',
        className
      )} {...props}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-xl font-bold text-gray-900">Menu</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <nav className="space-y-2">
            {items.map((item, index) => {
              const Icon = item.icon;
              const isActive = isActiveRoute(item.href);
              
              return (
                <Link
                  key={index}
                  to={item.href}
                  onClick={onClose}
                  className={cn(
                    'flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-base font-medium transition-all duration-200',
                    isActive
                      ? 'bg-primary/10 text-primary border border-primary/20'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  )}
                >
                  {Icon && <Icon className="w-5 h-5" />}
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="ml-auto bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </>
  );
};

// Export components
export {
  Breadcrumb,
  NavigationMenu,
  TabNavigation,
  SidebarNavigation,
  MobileNavigation
};