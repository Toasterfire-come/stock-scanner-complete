import React, { useEffect, useState } from 'react';
import { ThemeProvider } from 'next-themes';
import security from '../lib/security';

const SecurityProvider = ({ children }) => {
  const [isSecurityInitialized, setIsSecurityInitialized] = useState(false);
  const [securityError, setSecurityError] = useState(null);

  useEffect(() => {
    const initializeSecurity = async () => {
      try {
        // Initialize security measures
        security.initializeSecurity();
        
        // Avoid meta-delivered security headers which browsers ignore (use server headers instead)
        const robotsMeta = document.createElement('meta');
        robotsMeta.name = 'robots';
        robotsMeta.content = process.env.NODE_ENV === 'production' ? 'index, follow' : 'noindex, nofollow';
        document.head.appendChild(robotsMeta);
        
        // Disable right-click in production (optional security measure)
        if (process.env.NODE_ENV === 'production' && process.env.REACT_APP_DISABLE_RIGHT_CLICK === 'true') {
          document.addEventListener('contextmenu', (e) => e.preventDefault());
        }
        
        // Disable F12 and other dev tools shortcuts in production
        if (process.env.NODE_ENV === 'production' && process.env.REACT_APP_DISABLE_DEVTOOLS === 'true') {
          document.addEventListener('keydown', (e) => {
            // Disable F12, Ctrl+Shift+I, Ctrl+Shift+C, Ctrl+U
            if (
              e.key === 'F12' ||
              (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'C')) ||
              (e.ctrlKey && e.key === 'U')
            ) {
              e.preventDefault();
              e.stopPropagation();
              return false;
            }
          });
        }
        
        // Monitor for security violations
        window.addEventListener('securitypolicyviolation', (e) => {
          console.error('CSP Violation:', e);
          // Log to backend in production
          if (process.env.NODE_ENV === 'production') {
            const apiRoot = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');
            const url = apiRoot ? `${apiRoot}/api/logs/security/` : null;
            if (!url) return;
            fetch(url, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                type: 'csp_violation',
                directive: e.violatedDirective,
                blockedURI: e.blockedURI,
                documentURI: e.documentURI,
                timestamp: new Date().toISOString()
              })
            }).catch(console.error);
          }
        });
        
        setIsSecurityInitialized(true);
      } catch (error) {
        console.error('Security initialization error:', error);
        setSecurityError(error.message);
        
        // Don't block the app even if security init fails
        setIsSecurityInitialized(true);
      }
    };

    initializeSecurity();
  }, []);

  if (securityError) {
    console.error('Security initialization failed:', securityError);
    // Log security init failure but don't block the app
  }

  if (!isSecurityInitialized) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Initializing security...</p>
        </div>
      </div>
    );
  }

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </ThemeProvider>
  );
};

export default SecurityProvider;