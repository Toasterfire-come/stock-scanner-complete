import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { login as apiLogin, getProfile } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => window.localStorage.getItem("rts_token") || "");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      window.localStorage.setItem("rts_token", token);
      // hydrate profile
      getProfile()
        .then((res) => {
          if (res?.success) setUser(res.data);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      window.localStorage.removeItem("rts_token");
      setUser(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const res = await apiLogin(username, password);
      if (res?.token) {
        setToken(res.token);
        setUser(res.data);
        return { ok: true };
      }
      return { ok: false, error: "Invalid login response" };
    } catch (e) {
      return { ok: false, error: e?.response?.data?.detail || "Login failed" };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken("");
    setUser(null);
  };

  const value = useMemo(() => ({ token, user, loading, login, logout }), [token, user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}