class StockScannerAPI {
    constructor() {
        this.baseURL = process.env.REACT_APP_BACKEND_URL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    getAuthHeaders() {
        const token = localStorage.getItem('rts_token');
        return {
            ...this.defaultHeaders,
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getAuthHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Authentication methods
    async register(userData) {
        return this.request('/api/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        return this.request('/api/auth/login/', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    // Stock data methods
    async getStocks(filters = {}) {
        const params = new URLSearchParams();
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined) {
                params.append(key, filters[key]);
            }
        });
        return this.request(`/api/stocks/?${params}`);
    }

    async getStockDetails(ticker) {
        return this.request(`/api/stocks/${ticker.toUpperCase()}/`);
    }

    async getStockQuote(symbol) {
        return this.request(`/api/stocks/${symbol.toUpperCase()}/quote/`);
    }

    async getRealTimeData(ticker) {
        return this.request(`/api/realtime/${ticker.toUpperCase()}/`);
    }

    async searchStocks(query) {
        return this.request(`/api/stocks/search/?q=${encodeURIComponent(query)}`);
    }

    async getNasdaqStocks(limit = 500) {
        return this.request(`/api/stocks/nasdaq/?limit=${limit}`);
    }

    async getMarketStats() {
        return this.request('/api/market/stats/');
    }

    async getTrendingStocks() {
        return this.request('/api/trending/');
    }

    async filterStocks(filters) {
        const params = new URLSearchParams(filters);
        return this.request(`/api/market/filter/?${params}`);
    }

    // Platform methods
    async getPlatformStats() {
        return this.request('/api/platform-stats/');
    }

    async getUsageStats() {
        return this.request('/api/usage/');
    }

    // User methods (authenticated)
    async getUserProfile() {
        return this.request('/api/user/profile/');
    }

    async updateUserProfile(profileData) {
        return this.request('/api/user/profile/', {
            method: 'POST',
            body: JSON.stringify(profileData)
        });
    }

    async changePassword(passwordData) {
        return this.request('/api/user/change-password/', {
            method: 'POST',
            body: JSON.stringify(passwordData)
        });
    }

    // Billing methods (authenticated)
    async getCurrentPlan() {
        return this.request('/api/billing/current-plan/');
    }

    async getBillingHistory() {
        return this.request('/api/billing/history/');
    }

    async getBillingStats() {
        return this.request('/api/billing/stats/');
    }

    // Portfolio & Watchlist methods
    async getPortfolio() {
        return this.request('/api/portfolio/');
    }

    async addToPortfolio(symbol) {
        return this.request('/api/portfolio/add/', {
            method: 'POST',
            body: JSON.stringify({ symbol })
        });
    }

    async getWatchlist() {
        return this.request('/api/watchlist/');
    }

    async addToWatchlist(symbol) {
        return this.request('/api/watchlist/add/', {
            method: 'POST',
            body: JSON.stringify({ symbol })
        });
    }

    // WordPress integration
    async getWordPressStocks() {
        return this.request('/api/wordpress/');
    }

    async getWordPressNews() {
        return this.request('/api/wordpress/news/');
    }

    async getSimpleStocks() {
        return this.request('/api/simple/stocks/');
    }
}

// Export singleton instance
export const stockAPI = new StockScannerAPI();