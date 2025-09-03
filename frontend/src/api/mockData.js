// Mock data for static deployment without backend
export const mockData = {
  health: {
    status: "demo",
    local_db: "mock",
    external_api: "demo_mode",
    mode: "static_deployment",
    timestamp: new Date().toISOString()
  },
  
  platformStats: {
    nyse_stocks: 3200,
    total_indicators: 14,
    scanner_combinations: 1540
  },
  
  stocks: [
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      price: 189.46,
      change: 2.15,
      changePercent: 1.15,
      volume: 54289100,
      marketCap: 2950000000000,
      peRatio: 31.2,
      weekHigh52: 199.62,
      weekLow52: 164.08
    },
    {
      symbol: "MSFT",
      name: "Microsoft Corporation",
      price: 378.91,
      change: -1.23,
      changePercent: -0.32,
      volume: 23456789,
      marketCap: 2810000000000,
      peRatio: 35.8,
      weekHigh52: 384.52,
      weekLow52: 275.37
    },
    {
      symbol: "GOOGL",
      name: "Alphabet Inc.",
      price: 141.80,
      change: 0.95,
      changePercent: 0.67,
      volume: 29876543,
      marketCap: 1760000000000,
      peRatio: 26.5,
      weekHigh52: 155.20,
      weekLow52: 101.88
    },
    {
      symbol: "AMZN",
      name: "Amazon.com Inc.",
      price: 155.33,
      change: 3.21,
      changePercent: 2.11,
      volume: 65432100,
      marketCap: 1610000000000,
      peRatio: 52.3,
      weekHigh52: 161.73,
      weekLow52: 88.12
    },
    {
      symbol: "NVDA",
      name: "NVIDIA Corporation",
      price: 495.22,
      change: 12.45,
      changePercent: 2.58,
      volume: 45678900,
      marketCap: 1220000000000,
      peRatio: 118.9,
      weekHigh52: 502.66,
      weekLow52: 204.21
    },
    {
      symbol: "TSLA",
      name: "Tesla Inc.",
      price: 251.92,
      change: -5.38,
      changePercent: -2.09,
      volume: 98765432,
      marketCap: 800000000000,
      peRatio: 79.2,
      weekHigh52: 299.29,
      weekLow52: 152.37
    },
    {
      symbol: "META",
      name: "Meta Platforms Inc.",
      price: 313.86,
      change: 4.52,
      changePercent: 1.46,
      volume: 23456789,
      marketCap: 815000000000,
      peRatio: 24.7,
      weekHigh52: 354.83,
      weekLow52: 196.68
    },
    {
      symbol: "BRK.B",
      name: "Berkshire Hathaway Inc.",
      price: 367.71,
      change: -0.84,
      changePercent: -0.23,
      volume: 3456789,
      marketCap: 785000000000,
      peRatio: 9.1,
      weekHigh52: 375.40,
      weekLow52: 302.37
    },
    {
      symbol: "JPM",
      name: "JPMorgan Chase & Co.",
      price: 158.10,
      change: 1.20,
      changePercent: 0.76,
      volume: 12345678,
      marketCap: 465000000000,
      peRatio: 11.2,
      weekHigh52: 172.96,
      weekLow52: 134.78
    },
    {
      symbol: "V",
      name: "Visa Inc.",
      price: 247.49,
      change: 0.38,
      changePercent: 0.15,
      volume: 6789012,
      marketCap: 510000000000,
      peRatio: 30.1,
      weekHigh52: 261.75,
      weekLow52: 216.66
    }
  ],

  scannerResults: {
    gainers: [
      { symbol: "NVDA", name: "NVIDIA Corporation", change: 2.58 },
      { symbol: "AMZN", name: "Amazon.com Inc.", change: 2.11 },
      { symbol: "META", name: "Meta Platforms Inc.", change: 1.46 }
    ],
    losers: [
      { symbol: "TSLA", name: "Tesla Inc.", change: -2.09 },
      { symbol: "MSFT", name: "Microsoft Corporation", change: -0.32 },
      { symbol: "BRK.B", name: "Berkshire Hathaway Inc.", change: -0.23 }
    ],
    mostActive: [
      { symbol: "TSLA", name: "Tesla Inc.", volume: 98765432 },
      { symbol: "AMZN", name: "Amazon.com Inc.", volume: 65432100 },
      { symbol: "AAPL", name: "Apple Inc.", volume: 54289100 }
    ]
  },

  userProfile: {
    id: "demo-user",
    email: "demo@stockscanner.com",
    name: "Demo User",
    plan: "free",
    created: "2024-01-01T00:00:00Z"
  }
};

// Mock API delay to simulate network requests
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms));

export const mockApi = {
  async get(endpoint) {
    await delay();
    
    if (endpoint.includes('/health')) {
      return { data: mockData.health };
    }
    if (endpoint.includes('/platform-stats')) {
      return { data: mockData.platformStats };
    }
    if (endpoint.includes('/stocks')) {
      return { data: mockData.stocks };
    }
    if (endpoint.includes('/scanner')) {
      return { data: mockData.scannerResults };
    }
    if (endpoint.includes('/user') || endpoint.includes('/profile')) {
      return { data: mockData.userProfile };
    }
    
    // Default response
    return { data: { message: "Demo mode - no backend connected" } };
  },
  
  async post(endpoint, data) {
    await delay();
    
    if (endpoint.includes('/auth/login')) {
      return {
        data: {
          token: "demo-token-" + Date.now(),
          user: mockData.userProfile,
          message: "Demo login successful"
        }
      };
    }
    
    if (endpoint.includes('/auth/register')) {
      return {
        data: {
          message: "Demo registration successful",
          user: { ...mockData.userProfile, email: data.email || "new@demo.com" }
        }
      };
    }
    
    return { data: { success: true, message: "Demo mode - action simulated" } };
  }
};