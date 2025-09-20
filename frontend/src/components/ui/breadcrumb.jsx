import React from "react";
import { ChevronRight, Home } from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "../../lib/utils";

const Breadcrumb = React.forwardRef(({ className, ...props }, ref) => (
  <nav ref={ref} aria-label="breadcrumb" className={cn("", className)} {...props} />
));
Breadcrumb.displayName = "Breadcrumb";

const BreadcrumbList = React.forwardRef(({ className, ...props }, ref) => (
  <ol
    ref={ref}
    className={cn(
      "flex flex-wrap items-center gap-1.5 break-words text-sm text-muted-foreground sm:gap-2.5",
      className
    )}
    {...props}
  />
));
BreadcrumbList.displayName = "BreadcrumbList";

const BreadcrumbItem = React.forwardRef(({ className, ...props }, ref) => (
  <li
    ref={ref}
    className={cn("inline-flex items-center gap-1.5", className)}
    {...props}
  />
));
BreadcrumbItem.displayName = "BreadcrumbItem";

const BreadcrumbLink = React.forwardRef(({ asChild, className, ...props }, ref) => {
  return (
    <Link
      ref={ref}
      className={cn("transition-colors hover:text-foreground", className)}
      {...props}
    />
  );
});
BreadcrumbLink.displayName = "BreadcrumbLink";

const BreadcrumbPage = React.forwardRef(({ className, ...props }, ref) => (
  <span
    ref={ref}
    role="link"
    aria-disabled="true"
    aria-current="page"
    className={cn("font-normal text-foreground", className)}
    {...props}
  />
));
BreadcrumbPage.displayName = "BreadcrumbPage";

const BreadcrumbSeparator = ({ children, className, ...props }) => (
  <li
    role="presentation"
    aria-hidden="true"
    className={cn("[&>svg]:size-3.5", className)}
    {...props}
  >
    {children ?? <ChevronRight />}
  </li>
);
BreadcrumbSeparator.displayName = "BreadcrumbSeparator";

const BreadcrumbEllipsis = ({ className, ...props }) => (
  <span
    role="presentation"
    aria-hidden="true"
    className={cn("flex h-9 w-9 items-center justify-center", className)}
    {...props}
  >
    <span className="sr-only">More</span>
    <span>...</span>
  </span>
);
BreadcrumbEllipsis.displayName = "BreadcrumbElipsis";

// Smart breadcrumb component that generates breadcrumbs from current path
const SmartBreadcrumb = ({ className }) => {
  const currentPath = window.location.pathname;
  const pathSegments = currentPath.split('/').filter(segment => segment !== '');
  
  // Define route mappings for better display names
  const routeNames = {
    'app': 'Dashboard',
    'dashboard': 'Overview',
    'markets': 'Markets',
    'stocks': 'Stocks',
    'portfolio': 'Portfolio',
    'watchlists': 'Watchlists', 
    'screeners': 'Screeners',
    'alerts': 'Alerts',
    'account': 'Account',
    'profile': 'Profile',
    'plan': 'Plan & Billing',
    'docs': 'Documentation',
    'getting-started': 'Getting Started',
    'create-account': 'Create Account',
    'first-screener': 'First Screener',
    'features': 'Features',
    'pricing': 'Pricing',
    'about': 'About',
    'contact': 'Contact',
    'help': 'Help'
  };

  // Don't show breadcrumbs on home page or single-level pages
  if (pathSegments.length <= 1 && currentPath !== '/') {
    return null;
  }

  const breadcrumbItems = [];
  
  // Always add home
  breadcrumbItems.push({
    name: 'Home',
    path: '/',
    icon: <Home className="h-4 w-4" />
  });

  // Build breadcrumb items from path segments
  let currentBreadcrumbPath = '';
  pathSegments.forEach((segment, index) => {
    currentBreadcrumbPath += `/${segment}`;
    const displayName = routeNames[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
    
    breadcrumbItems.push({
      name: displayName,
      path: currentBreadcrumbPath,
      isLast: index === pathSegments.length - 1
    });
  });

  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        {breadcrumbItems.map((item, index) => (
          <React.Fragment key={item.path}>
            <BreadcrumbItem>
              {item.isLast ? (
                <BreadcrumbPage className="flex items-center gap-1">
                  {item.icon}
                  {item.name}
                </BreadcrumbPage>
              ) : (
                <BreadcrumbLink to={item.path} className="flex items-center gap-1">
                  {item.icon}
                  {item.name}
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
            {index < breadcrumbItems.length - 1 && <BreadcrumbSeparator />}
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

export {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
  SmartBreadcrumb,
};