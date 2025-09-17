import React, { useState, createContext, useContext } from 'react';

const DialogContext = createContext();

export const Dialog = ({ children, open, onOpenChange }) => {
  const [isOpen, setIsOpen] = useState(open || false);
  
  const handleOpenChange = (newOpen) => {
    setIsOpen(newOpen);
    onOpenChange && onOpenChange(newOpen);
  };
  
  return (
    <DialogContext.Provider value={{ isOpen, setIsOpen: handleOpenChange }}>
      {children}
    </DialogContext.Provider>
  );
};

export const DialogTrigger = ({ children, asChild = false, ...props }) => {
  const { setIsOpen } = useContext(DialogContext);
  
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

export const DialogContent = ({ children, className = '', ...props }) => {
  const { isOpen, setIsOpen } = useContext(DialogContext);
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div 
        className={`bg-white rounded-lg shadow-lg max-w-lg w-full max-h-[85vh] overflow-auto ${className}`}
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
    </div>
  );
};

export const DialogHeader = ({ children, className = '', ...props }) => (
  <div className={`p-6 pb-2 ${className}`} {...props}>
    {children}
  </div>
);

export const DialogTitle = ({ children, className = '', ...props }) => (
  <h2 className={`text-lg font-semibold ${className}`} {...props}>
    {children}
  </h2>
);