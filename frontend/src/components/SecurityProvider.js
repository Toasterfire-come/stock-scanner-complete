import React, { useEffect, useState } from 'react';
import security from '../lib/security';

const SecurityProvider = ({ children }) => {
  const [isSecurityInitialized, setIsSecurityInitialized] = useState(false);
  const [securityError, setSecurityError] = useState(null);

  useEffect(() => {
    const initializeSecurity = async () => {
      try {
        // Initialize security measures
        security.initializeSecurity();
        
        // Add Content Security Policy meta tag
        const cspMeta = document.createElement('meta');
        cspMeta.httpEquiv = 'Content-Security-Policy';
        cspMeta.content = security.generateCSPMeta();
        document.head.appendChild(cspMeta);
        
        // Add additional security meta tags
        const securityMetas = [
          { httpEquiv: 'X-Frame-Options', content: 'DENY' },
          { httpEquiv: 'X-Content-Type-Options', content: 'nosniff' },
          { httpEquiv: 'X-XSS-Protection', content: '1; mode=block' },
          { httpEquiv: 'Referrer-Policy', content: 'strict-origin-when-cross-origin' },
          { name: 'robots', content: process.env.NODE_ENV === 'production' ? 'index, follow' : 'noindex, nofollow' }
        ];
        
        securityMetas.forEach(({ httpEquiv, name, content }) => {
          const meta = document.createElement('meta');
          if (httpEquiv) meta.httpEquiv = httpEquiv;
          if (name) meta.name = name;
          meta.content = content;
          document.head.appendChild(meta);
        });
        
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
            fetch('/api/logs/security/', {
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

  return <>{children}</>;
};

export default SecurityProvider;