import React, { useState, createContext, useContext } from 'react';

const SheetContext = createContext();

export const Sheet = ({ children, open, onOpenChange }) => {
  const [isOpen, setIsOpen] = useState(open || false);
  
  const handleOpenChange = (newOpen) => {
    setIsOpen(newOpen);
    onOpenChange && onOpenChange(newOpen);
  };
  
  return (
    <SheetContext.Provider value={{ isOpen, setIsOpen: handleOpenChange }}>
      {children}
    </SheetContext.Provider>
  );
};

export const SheetTrigger = ({ children, asChild = false, ...props }) => {
  const { setIsOpen } = useContext(SheetContext);
  
  const handleClick = () => setIsOpen(true);
  
  if (asChild) {
    return React.cloneElement(children, { onClick: handleClick, ...props });
  }
  
  return (
    <button onClick={handleClick} {...props}>
      {children}
    </button>
  );
};

export const SheetContent = ({ children, className = '', side = 'right', ...props }) => {
  const { isOpen, setIsOpen } = useContext(SheetContext);
  
  if (!isOpen) return null;
  
  const sides = {
    right: 'right-0 top-0 h-full w-3/4 max-w-sm border-l',
    left: 'left-0 top-0 h-full w-3/4 max-w-sm border-r',
    top: 'top-0 left-0 w-full max-h-96 border-b',
    bottom: 'bottom-0 left-0 w-full max-h-96 border-t'
  };
  
  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/50" onClick={() => setIsOpen(false)} />
      <div 
        className={`fixed z-50 bg-white p-6 shadow-lg transition ease-in-out ${sides[side]} ${className}`}
        {...props}
      >
        <button
          onClick={() => setIsOpen(false)}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
        {children}
      </div>
    </>
  );
};

export const SheetHeader = ({ children, className = '', ...props }) => (
  <div className={`mb-4 ${className}`} {...props}>
    {children}
  </div>
);

export const SheetTitle = ({ children, className = '', ...props }) => (
  <h2 className={`text-lg font-semibold ${className}`} {...props}>
    {children}
  </h2>
);

export const SheetDescription = ({ children, className = '', ...props }) => (
  <p className={`text-sm text-gray-600 ${className}`} {...props}>
    {children}
  </p>
);