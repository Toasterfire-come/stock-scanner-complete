import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import logger from '../lib/logger';
import { api } from '../api/client';
import { useAuth } from '../context/SecureAuthContext';

/**
 * useFavorites Hook
 *
 * Manages favorite stocks with localStorage persistence
 * Integrates with backend API for syncing across devices
 */

const STORAGE_KEY = 'tradescanpro_favorites';

export function useFavorites() {
  const { isAuthenticated } = useAuth();
  const [favorites, setFavorites] = useState(() => {
    // Load from localStorage on init
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      logger.error('Failed to load favorites:', error);
      return [];
    }
  });

  const [isLoading, setIsLoading] = useState(false);

  // Save to localStorage whenever favorites change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites));
    } catch (error) {
      logger.error('Failed to save favorites:', error);
    }
  }, [favorites]);

  // Sync with backend (if user is logged in)
  const syncWithBackend = useCallback(async () => {
    try {
      setIsLoading(true);

      if (!isAuthenticated) return;
      const { data } = await api.get('/favorites/');
      if (data?.success && Array.isArray(data.favorites)) {
        setFavorites(data.favorites);
      }

      setIsLoading(false);
    } catch (error) {
      logger.error('Failed to sync favorites:', error);
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Initial sync when authenticated
  useEffect(() => {
    if (isAuthenticated) syncWithBackend();
  }, [isAuthenticated, syncWithBackend]);

  const addFavorite = useCallback((ticker) => {
    setFavorites(prev => {
      if (prev.includes(ticker)) {
        return prev;
      }
      const updated = [...prev, ticker];

      if (isAuthenticated) {
        api.post('/favorites/', { ticker }).catch(() => {});
      }

      toast.success(`${ticker} added to favorites`);
      return updated;
    });
  }, [isAuthenticated]);

  const removeFavorite = useCallback((ticker) => {
    setFavorites(prev => {
      const updated = prev.filter(t => t !== ticker);

      if (isAuthenticated) {
        api.delete(`/favorites/${encodeURIComponent(ticker)}/`).catch(() => {});
      }

      toast.success(`${ticker} removed from favorites`);
      return updated;
    });
  }, [isAuthenticated]);

  const toggleFavorite = useCallback((ticker) => {
    setFavorites(prev => {
      const isFavorite = prev.includes(ticker);
      const updated = isFavorite
        ? prev.filter(t => t !== ticker)
        : [...prev, ticker];

      if (isAuthenticated) {
        if (isFavorite) {
          api.delete(`/favorites/${encodeURIComponent(ticker)}/`).catch(() => {});
        } else {
          api.post('/favorites/', { ticker }).catch(() => {});
        }
      }

      toast.success(isFavorite
        ? `${ticker} removed from favorites`
        : `${ticker} added to favorites`
      );

      return updated;
    });
  }, [isAuthenticated]);

  const isFavorite = useCallback((ticker) => {
    return favorites.includes(ticker);
  }, [favorites]);

  const clearFavorites = useCallback(() => {
    setFavorites([]);

    if (isAuthenticated) {
      api.delete('/favorites/all/').catch(() => {});
    }

    toast.success('All favorites cleared');
  }, [isAuthenticated]);

  return {
    favorites,
    isLoading,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
    clearFavorites,
    syncWithBackend,
  };
}
