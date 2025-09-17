import React from 'react';

export const NavigationMenu = ({ children, className = '', ...props }) => (
  <nav className={`flex items-center space-x-4 ${className}`} {...props}>
    {children}
  </nav>
);

export const NavigationMenuList = ({ children, className = '', ...props }) => (
  <ul className={`flex list-none space-x-1 ${className}`} {...props}>
    {children}
  </ul>
);

export const NavigationMenuItem = ({ children, className = '', ...props }) => (
  <li className={className} {...props}>
    {children}
  </li>
);

export const NavigationMenuLink = ({ children, href, className = '', active = false, ...props }) => (
  <a
    href={href}
    className={`
      group inline-flex h-10 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors
      hover:bg-gray-100 hover:text-gray-900 focus:bg-gray-100 focus:text-gray-900 focus:outline-none
      disabled:pointer-events-none disabled:opacity-50
      ${active ? 'bg-gray-100 text-gray-900' : 'text-gray-600'}
      ${className}
    `}
    {...props}
  >
    {children}
  </a>
);

export const NavigationMenuTrigger = ({ children, className = '', ...props }) => (
  <button
    className={`
      group inline-flex h-10 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors
      hover:bg-gray-100 hover:text-gray-900 focus:bg-gray-100 focus:text-gray-900 focus:outline-none
      disabled:pointer-events-none disabled:opacity-50 text-gray-600
      ${className}
    `}
    {...props}
  >
    {children}
  </button>
);

export const NavigationMenuContent = ({ children, className = '', ...props }) => (
  <div
    className={`
      absolute left-0 top-0 w-full data-[motion^=from-]:animate-in data-[motion^=to-]:animate-out
      data-[motion^=from-]:fade-in data-[motion^=to-]:fade-out data-[motion=from-end]:slide-in-from-right-52
      data-[motion=from-start]:slide-in-from-left-52 data-[motion=to-end]:slide-out-to-right-52
      data-[motion=to-start]:slide-out-to-left-52 md:absolute md:w-auto
      ${className}
    `}
    {...props}
  >
    {children}
  </div>
);