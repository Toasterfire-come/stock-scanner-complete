import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import logger from '../lib/logger';

/**
 * useFavorites Hook
 *
 * Manages favorite stocks with localStorage persistence
 * Integrates with backend API for syncing across devices
 */

const STORAGE_KEY = 'tradescanpro_favorites';

export function useFavorites() {
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

      // TODO: Integrate with your backend API
      // const response = await api.get('/api/favorites/');
      // if (response.data.favorites) {
      //   setFavorites(response.data.favorites);
      // }

      setIsLoading(false);
    } catch (error) {
      logger.error('Failed to sync favorites:', error);
      setIsLoading(false);
    }
  }, []);

  const addFavorite = useCallback((ticker) => {
    setFavorites(prev => {
      if (prev.includes(ticker)) {
        return prev;
      }
      const updated = [...prev, ticker];

      // TODO: Sync with backend
      // api.post('/api/favorites/', { ticker });

      toast.success(`${ticker} added to favorites`);
      return updated;
    });
  }, []);

  const removeFavorite = useCallback((ticker) => {
    setFavorites(prev => {
      const updated = prev.filter(t => t !== ticker);

      // TODO: Sync with backend
      // api.delete(`/api/favorites/${ticker}/`);

      toast.success(`${ticker} removed from favorites`);
      return updated;
    });
  }, []);

  const toggleFavorite = useCallback((ticker) => {
    setFavorites(prev => {
      const isFavorite = prev.includes(ticker);
      const updated = isFavorite
        ? prev.filter(t => t !== ticker)
        : [...prev, ticker];

      // TODO: Sync with backend
      // if (isFavorite) {
      //   api.delete(`/api/favorites/${ticker}/`);
      // } else {
      //   api.post('/api/favorites/', { ticker });
      // }

      toast.success(isFavorite
        ? `${ticker} removed from favorites`
        : `${ticker} added to favorites`
      );

      return updated;
    });
  }, []);

  const isFavorite = useCallback((ticker) => {
    return favorites.includes(ticker);
  }, [favorites]);

  const clearFavorites = useCallback(() => {
    setFavorites([]);

    // TODO: Sync with backend
    // api.delete('/api/favorites/all/');

    toast.success('All favorites cleared');
  }, []);

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
