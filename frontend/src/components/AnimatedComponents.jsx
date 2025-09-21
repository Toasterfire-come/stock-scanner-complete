import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { Loader2, CheckCircle, AlertCircle, TrendingUp, TrendingDown } from "lucide-react";

// Enhanced Button with micro-interactions
export const AnimatedButton = ({ 
  children, 
  onClick, 
  variant = "default", 
  size = "default", 
  className = "",
  loading = false,
  success = false,
  ...props 
}) => {
  const [isPressed, setIsPressed] = useState(false);

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onTapStart={() => setIsPressed(true)}
      onTapCancel={() => setIsPressed(false)}
    >
      <Button
        variant={variant}
        size={size}
        className={`relative overflow-hidden transition-all duration-200 ${className}`}
        onClick={onClick}
        disabled={loading}
        {...props}
      >
        <motion.div
          className="absolute inset-0 bg-white/20 rounded-md"
          initial={{ x: "-100%" }}
          animate={isPressed ? { x: "100%" } : { x: "-100%" }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
        />
        
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center gap-2"
            >
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading...
            </motion.div>
          ) : success ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center gap-2"
            >
              <CheckCircle className="h-4 w-4" />
              Success!
            </motion.div>
          ) : (
            <motion.div
              key="default"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </Button>
    </motion.div>
  );
};

// Enhanced Card with hover effects
export const AnimatedCard = ({ 
  children, 
  className = "", 
  hoverScale = 1.02,
  hoverShadow = true,
  ...props 
}) => {
  return (
    <motion.div
      whileHover={{ 
        scale: hoverScale,
        y: -2
      }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={hoverShadow ? "hover:shadow-lg transition-shadow duration-200" : ""}
    >
      <Card className={`transition-all duration-200 ${className}`} {...props}>
        {children}
      </Card>
    </motion.div>
  );
};

// Animated Number Counter
export const AnimatedCounter = ({ 
  value, 
  duration = 1000, 
  prefix = "", 
  suffix = "",
  className = "",
  decimals = 0
}) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTime;
    let animationFrame;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = easeOutQuart * value;
      
      setDisplayValue(currentValue);
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    
    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [value, duration]);

  return (
    <span className={className}>
      {prefix}{displayValue.toFixed(decimals)}{suffix}
    </span>
  );
};

// Animated Progress Bar
export const AnimatedProgress = ({ 
  value, 
  max = 100, 
  duration = 1000,
  className = "",
  showValue = false
}) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const percentage = (value / max) * 100;

  useEffect(() => {
    const timeout = setTimeout(() => {
      setAnimatedValue(percentage);
    }, 100);

    return () => clearTimeout(timeout);
  }, [percentage]);

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="relative">
        <Progress 
          value={animatedValue} 
          className="transition-all duration-1000 ease-out"
        />
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center text-sm font-medium">
            <AnimatedCounter value={value} suffix={`/${max}`} />
          </div>
        )}
      </div>
    </div>
  );
};

// Staggered List Animation
export const StaggeredList = ({ 
  children, 
  className = "",
  staggerDelay = 0.1,
  initialDelay = 0
}) => {
  return (
    <motion.div 
      className={className}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            delayChildren: initialDelay,
            staggerChildren: staggerDelay
          }
        }
      }}
    >
      {React.Children.map(children, (child, index) => (
        <motion.div
          key={index}
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 }
          }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
};

// Page Transition Wrapper
export const PageTransition = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      {children}
    </motion.div>
  );
};

// Stock Price Animation
export const AnimatedPrice = ({ 
  price, 
  change, 
  changePercent,
  className = ""
}) => {
  const [prevPrice, setPrevPrice] = useState(price);
  const [flashColor, setFlashColor] = useState("");

  useEffect(() => {
    if (prevPrice !== price) {
      const isUp = price > prevPrice;
      setFlashColor(isUp ? "bg-green-200" : "bg-red-200");
      
      const timeout = setTimeout(() => {
        setFlashColor("");
      }, 500);

      setPrevPrice(price);
      return () => clearTimeout(timeout);
    }
  }, [price, prevPrice]);

  const isPositive = change >= 0;

  return (
    <motion.div 
      className={`flex items-center gap-2 p-2 rounded transition-colors duration-500 ${flashColor} ${className}`}
      animate={flashColor ? { scale: 1.05 } : { scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      <div className="font-bold text-lg">
        ${price.toFixed(2)}
      </div>
      <div className={`flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
        <span className="text-sm font-medium">
          {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
        </span>
      </div>
    </motion.div>
  );
};

// Loading Skeleton with shimmer
export const SkeletonLoader = ({ 
  width = "100%", 
  height = "20px", 
  className = "",
  rounded = true 
}) => {
  return (
    <div 
      className={`bg-muted animate-pulse ${rounded ? 'rounded' : ''} ${className}`}
      style={{ width, height }}
    >
      <motion.div
        className="h-full bg-gradient-to-r from-transparent via-white/40 to-transparent"
        animate={{ x: ["-100%", "100%"] }}
        transition={{ 
          repeat: Infinity, 
          duration: 1.5, 
          ease: "linear" 
        }}
        style={{ width: "100%" }}
      />
    </div>
  );
};

// Notification Toast Animation
export const AnimatedToast = ({ 
  message, 
  type = "info", 
  isVisible = false, 
  onClose 
}) => {
  const icons = {
    success: <CheckCircle className="h-5 w-5 text-green-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    info: <AlertCircle className="h-5 w-5 text-blue-500" />
  };

  const backgrounds = {
    success: "bg-green-50 border-green-200",
    error: "bg-red-50 border-red-200",
    info: "bg-blue-50 border-blue-200"
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className={`fixed top-4 right-4 z-50 p-4 rounded-lg border shadow-lg max-w-sm ${backgrounds[type]}`}
        >
          <div className="flex items-center gap-3">
            {icons[type]}
            <p className="text-sm font-medium">{message}</p>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="ml-auto h-6 w-6 p-0"
            >
              ×
            </Button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default {
  AnimatedButton,
  AnimatedCard,
  AnimatedCounter,
  AnimatedProgress,
  StaggeredList,
  PageTransition,
  AnimatedPrice,
  SkeletonLoader,
  AnimatedToast
};