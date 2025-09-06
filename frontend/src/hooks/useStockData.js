import { useState, useEffect, useCallback } from 'react';
import { stockAPI } from '../services/stockAPI';

export const useStockData = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchStocks = useCallback(async (filters = {}) => {
        setLoading(true);
        setError(null);

        try {
            const response = await stockAPI.getStocks(filters);
            if (response.success) {
                setStocks(response.data);
            } else {
                setError(response.error);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const getStockQuote = useCallback(async (symbol) => {
        try {
            const response = await stockAPI.getStockQuote(symbol);
            if (response.success) {
                return response;
            } else {
                throw new Error(response.error);
            }
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, []);

    const searchStocks = useCallback(async (query) => {
        try {
            const response = await stockAPI.searchStocks(query);
            return response.success ? response.data : [];
        } catch (err) {
            setError(err.message);
            return [];
        }
    }, []);

    return {
        stocks,
        loading,
        error,
        fetchStocks,
        getStockQuote,
        searchStocks
    };
};

export const usePlatformStats = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchStats = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await stockAPI.getPlatformStats();
            if (response.success) {
                setStats(response);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchStats();
    }, [fetchStats]);

    return { stats, loading, error, refetch: fetchStats };
};

export const useUsageStats = () => {
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchUsage = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await stockAPI.getUsageStats();
            if (response.success) {
                setUsage(response);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUsage();
    }, [fetchUsage]);

    return { usage, loading, error, refetch: fetchUsage };
};

export const useTrendingStocks = () => {
    const [trending, setTrending] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchTrending = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await stockAPI.getTrendingStocks();
            if (response.success) {
                setTrending(response);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTrending();
    }, [fetchTrending]);

    return { trending, loading, error, refetch: fetchTrending };
};