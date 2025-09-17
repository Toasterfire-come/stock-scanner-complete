import React, { useState, createContext, useContext } from 'react';

const DropdownContext = createContext();

export const DropdownMenu = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <DropdownContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative inline-block text-left">
        {children}
      </div>
    </DropdownContext.Provider>
  );
};

export const DropdownMenuTrigger = ({ children, asChild = false, ...props }) => {
  const { isOpen, setIsOpen } = useContext(DropdownContext);
  
  const handleClick = () => setIsOpen(!isOpen);
  
  if (asChild) {
    return React.cloneElement(children, { onClick: handleClick, ...props });
  }
  
  return (
    <button onClick={handleClick} {...props}>
      {children}
    </button>
  );
};

export const DropdownMenuContent = ({ children, className = '', align = 'right', ...props }) => {
  const { isOpen, setIsOpen } = useContext(DropdownContext);
  
  if (!isOpen) return null;
  
  const alignmentClasses = {
    left: 'left-0',
    right: 'right-0',
    center: 'left-1/2 transform -translate-x-1/2'
  };
  
  return (
    <>
      <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
      <div 
        className={`absolute z-20 mt-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 ${alignmentClasses[align]} ${className}`}
        {...props}
      >
        <div className="py-1" role="menu">
          {children}
        </div>
      </div>
    </>
  );
};

export const DropdownMenuItem = ({ children, onClick, className = '', ...props }) => {
  const { setIsOpen } = useContext(DropdownContext);
  
  const handleClick = (e) => {
    onClick && onClick(e);
    setIsOpen(false);
  };
  
  return (
    <button
      className={`block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 ${className}`}
      onClick={handleClick}
      role="menuitem"
      {...props}
    >
      {children}
    </button>
  );
};

export const DropdownMenuSeparator = ({ className = '' }) => (
  <div className={`border-t border-gray-100 my-1 ${className}`} />
);