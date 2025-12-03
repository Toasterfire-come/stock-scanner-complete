import React, { useEffect, useRef } from "react";

// Renders the Google One Tap prompt if available. Expects REACT_APP_GOOGLE_CLIENT_ID
const OneTapGoogle = ({ onCredential }) => {
  const initializedRef = useRef(false);
  useEffect(() => {
    if (initializedRef.current) return;
    const backend = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');
    const envClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
    const load = async () => {
      let clientId = envClientId;
      if (!clientId && backend) {
        try {
          const r = await fetch(`${backend}/auth/google/config`, { credentials: 'include' });
          if (r.ok) {
            const j = await r.json().catch(() => ({}));
            clientId = j.client_id || '';
          }
        } catch {}
      }
      if (!clientId) return;
      const scriptId = "google-identity-services";
      if (!document.getElementById(scriptId)) {
        const s = document.createElement('script');
        s.id = scriptId;
        s.src = "https://accounts.google.com/gsi/client";
        s.async = true;
        s.defer = true;
        s.onload = () => {
          try {
            /* global google */
            if (window.google && window.google.accounts && window.google.accounts.id) {
              window.google.accounts.id.initialize({
                client_id: clientId,
                callback: (res) => onCredential && onCredential(res.credential),
                auto_select: false,
                cancel_on_tap_outside: true,
                use_fedcm_for_prompt: true,
              });
              window.google.accounts.id.prompt();
              initializedRef.current = true;
            }
          } catch {}
        };
        document.head.appendChild(s);
      }
    };
    load();
  }, [onCredential]);
  return null;
};

export default OneTapGoogle;

