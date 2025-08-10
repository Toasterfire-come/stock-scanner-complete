<?php
/*
Template Name: Financial Glossary
Description: Searchable financial terms and definitions
*/

get_header(); ?>

<div class="container mx-auto p-6">
    <div class="page-header text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Financial Glossary</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">Comprehensive dictionary of financial terms, investment concepts, and trading terminology to help you navigate the markets with confidence.</p>
    </div>

    <!-- Search and Filter Section -->
    <div class="card p-6 mb-8">
        <div class="flex flex-col md:flex-row gap-4 items-center">
            <div class="flex-1">
                <div class="relative">
                    <input 
                        type="text" 
                        id="search-input" 
                        placeholder="Search for financial terms..." 
                        class="w-full p-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                    <svg class="absolute right-3 top-3 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>
            </div>
            <div class="flex gap-2">
                <select id="category-filter" class="form-select rounded-lg border-gray-300">
                    <option value="">All Categories</option>
                    <option value="stocks">Stocks</option>
                    <option value="bonds">Bonds</option>
                    <option value="options">Options</option>
                    <option value="forex">Forex</option>
                    <option value="crypto">Cryptocurrency</option>
                    <option value="technical">Technical Analysis</option>
                    <option value="fundamental">Fundamental Analysis</option>
                    <option value="general">General Finance</option>
                </select>
                <button id="clear-search" class="btn btn-secondary">Clear</button>
            </div>
        </div>
    </div>

    <!-- Alphabet Navigation -->
    <div class="card p-6 mb-6">
        <div class="flex flex-wrap justify-center gap-2" id="alphabet-nav">
            <button class="alphabet-btn active" data-letter="all">All</button>
            <button class="alphabet-btn" data-letter="A">A</button>
            <button class="alphabet-btn" data-letter="B">B</button>
            <button class="alphabet-btn" data-letter="C">C</button>
            <button class="alphabet-btn" data-letter="D">D</button>
            <button class="alphabet-btn" data-letter="E">E</button>
            <button class="alphabet-btn" data-letter="F">F</button>
            <button class="alphabet-btn" data-letter="G">G</button>
            <button class="alphabet-btn" data-letter="H">H</button>
            <button class="alphabet-btn" data-letter="I">I</button>
            <button class="alphabet-btn" data-letter="J">J</button>
            <button class="alphabet-btn" data-letter="K">K</button>
            <button class="alphabet-btn" data-letter="L">L</button>
            <button class="alphabet-btn" data-letter="M">M</button>
            <button class="alphabet-btn" data-letter="N">N</button>
            <button class="alphabet-btn" data-letter="O">O</button>
            <button class="alphabet-btn" data-letter="P">P</button>
            <button class="alphabet-btn" data-letter="Q">Q</button>
            <button class="alphabet-btn" data-letter="R">R</button>
            <button class="alphabet-btn" data-letter="S">S</button>
            <button class="alphabet-btn" data-letter="T">T</button>
            <button class="alphabet-btn" data-letter="U">U</button>
            <button class="alphabet-btn" data-letter="V">V</button>
            <button class="alphabet-btn" data-letter="W">W</button>
            <button class="alphabet-btn" data-letter="X">X</button>
            <button class="alphabet-btn" data-letter="Y">Y</button>
            <button class="alphabet-btn" data-letter="Z">Z</button>
        </div>
    </div>

    <!-- Results Summary -->
    <div class="mb-4">
        <p id="results-summary" class="text-gray-600">Showing <span id="results-count">0</span> terms</p>
    </div>

    <!-- Glossary Terms -->
    <div class="space-y-4" id="glossary-container">
        <!-- Terms will be dynamically populated here -->
    </div>

    <!-- No Results Message -->
    <div id="no-results" class="card p-8 text-center" style="display: none;">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No terms found</h3>
        <p class="text-gray-600">Try adjusting your search criteria or browse by category.</p>
    </div>
</div>

<style>
/* Glossary Specific Styles */
.glossary-term {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    transition: all 0.2s ease;
}

.glossary-term:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.term-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: var(--space-2);
}

.term-category {
    display: inline-block;
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    margin-bottom: var(--space-3);
}

.term-definition {
    color: var(--color-text);
    line-height: 1.6;
    margin-bottom: var(--space-3);
}

.term-example {
    background: var(--color-bg);
    border-left: 4px solid var(--color-info);
    padding: var(--space-3);
    margin-top: var(--space-3);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.term-example-label {
    font-weight: 600;
    color: var(--color-info);
    margin-bottom: var(--space-1);
}

.alphabet-btn {
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    color: var(--color-text);
    border-radius: var(--radius-md);
    font-weight: 500;
    transition: all 0.2s ease;
    cursor: pointer;
}

.alphabet-btn:hover {
    background: var(--color-border);
}

.alphabet-btn.active {
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    border-color: var(--color-primary);
}

.btn {
    display: inline-flex;
    align-items: center;
    padding: var(--space-2) var(--space-4);
    font-weight: 500;
    border-radius: var(--radius-md);
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;
    text-decoration: none;
}

.btn-secondary {
    background: var(--color-surface);
    color: var(--color-text);
    border: 1px solid var(--color-border);
}

.btn-secondary:hover {
    background: var(--color-border);
}

.form-select {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    color: var(--color-text);
    padding: var(--space-2) var(--space-3);
}

.card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

@media (max-width: 768px) {
    .alphabet-btn {
        padding: var(--space-1) var(--space-2);
        font-size: 0.875rem;
    }
    
    .glossary-term {
        padding: var(--space-4);
    }
    
    .term-title {
        font-size: 1.125rem;
    }
}
</style>

<script>
// Financial Glossary Data
const glossaryTerms = [
    {
        term: "Bull Market",
        category: "stocks",
        definition: "A financial market condition characterized by rising prices and investor optimism. In a bull market, stock prices generally trend upward over an extended period, typically 20% or more from recent lows.",
        example: "The U.S. stock market experienced a significant bull market from 2009 to 2020, with the S&P 500 gaining over 400% during this period."
    },
    {
        term: "Bear Market",
        category: "stocks",
        definition: "A market condition where securities prices fall 20% or more from recent highs, accompanied by widespread pessimism and negative investor sentiment.",
        example: "The 2008 financial crisis led to a bear market where the S&P 500 declined approximately 57% from its peak."
    },
    {
        term: "Dividend",
        category: "stocks",
        definition: "A payment made by a corporation to its shareholders, usually as a distribution of profits. Dividends are typically paid quarterly and can be in cash or additional shares.",
        example: "Apple Inc. pays a quarterly dividend of approximately $0.24 per share, providing investors with regular income."
    },
    {
        term: "P/E Ratio",
        category: "fundamental",
        definition: "Price-to-Earnings ratio is a valuation metric calculated by dividing a company's current share price by its earnings per share (EPS). It indicates how much investors are willing to pay per dollar of earnings.",
        example: "If a stock trades at $100 and has an EPS of $5, its P/E ratio is 20, meaning investors pay $20 for every $1 of earnings."
    },
    {
        term: "Market Capitalization",
        category: "stocks",
        definition: "The total dollar market value of a company's outstanding shares of stock. It's calculated by multiplying the current stock price by the total number of outstanding shares.",
        example: "A company with 1 million shares outstanding trading at $50 per share has a market cap of $50 million."
    },
    {
        term: "Beta",
        category: "technical",
        definition: "A measure of a stock's volatility in relation to the overall market. A beta of 1 indicates the stock moves with the market, while beta greater than 1 indicates higher volatility.",
        example: "A stock with a beta of 1.5 is expected to move 50% more than the market in either direction."
    },
    {
        term: "Call Option",
        category: "options",
        definition: "A financial contract that gives the holder the right, but not the obligation, to buy an underlying asset at a specified price within a certain time period.",
        example: "Buying a call option on AAPL with a $150 strike price gives you the right to purchase AAPL shares at $150 until expiration."
    },
    {
        term: "Put Option",
        category: "options",
        definition: "A financial contract that gives the holder the right, but not the obligation, to sell an underlying asset at a specified price within a certain time period.",
        example: "A put option on SPY with a $400 strike allows you to sell SPY shares at $400, useful if you expect the price to fall."
    },
    {
        term: "Volatility",
        category: "technical",
        definition: "A statistical measure of the dispersion of returns for a given security or market index. Higher volatility indicates larger price swings.",
        example: "During market crises, volatility typically spikes as investors react to uncertainty with rapid buying and selling."
    },
    {
        term: "Yield",
        category: "bonds",
        definition: "The income return on an investment, usually expressed as an annual percentage rate. For bonds, it's the annual coupon payments divided by the current market price.",
        example: "A bond paying $50 annually and trading at $1,000 has a current yield of 5%."
    },
    {
        term: "Asset Allocation",
        category: "general",
        definition: "An investment strategy that balances risk and reward by apportioning a portfolio's assets according to an individual's goals, risk tolerance, and investment horizon.",
        example: "A typical balanced portfolio might allocate 60% to stocks, 30% to bonds, and 10% to alternative investments."
    },
    {
        term: "Cryptocurrency",
        category: "crypto",
        definition: "A digital or virtual currency secured by cryptography, making it nearly impossible to counterfeit. Most cryptocurrencies are decentralized networks based on blockchain technology.",
        example: "Bitcoin was the first cryptocurrency, created in 2009, and remains the largest by market capitalization."
    },
    {
        term: "Forex",
        category: "forex",
        definition: "The foreign exchange market where currencies are traded. It's the largest and most liquid financial market in the world, operating 24 hours a day.",
        example: "EUR/USD is the most traded currency pair, representing the exchange rate between the Euro and US Dollar."
    },
    {
        term: "Moving Average",
        category: "technical",
        definition: "A technical analysis indicator that smooths price data by creating a constantly updated average price over a specific time period.",
        example: "A 50-day moving average takes the average closing price of the last 50 trading days and updates daily."
    },
    {
        term: "Support Level",
        category: "technical",
        definition: "A price level where a declining stock tends to find support as buying interest overcomes selling pressure, preventing further decline.",
        example: "If a stock repeatedly bounces off $50, that price level is considered a support level."
    },
    {
        term: "Resistance Level",
        category: "technical",
        definition: "A price level where a rising stock tends to encounter selling pressure that prevents it from moving higher.",
        example: "If a stock struggles to break above $100 multiple times, $100 becomes a resistance level."
    },
    {
        term: "Dollar Cost Averaging",
        category: "general",
        definition: "An investment strategy where an investor divides up the total amount to be invested across periodic purchases to reduce the impact of volatility.",
        example: "Investing $500 monthly in an index fund regardless of market conditions is dollar cost averaging."
    },
    {
        term: "IPO",
        category: "stocks",
        definition: "Initial Public Offering - the first sale of stock by a private company to the public. It's how private companies become publicly traded.",
        example: "Facebook went public through an IPO in 2012, raising $16 billion from investors."
    },
    {
        term: "Short Selling",
        category: "stocks",
        definition: "A trading strategy where an investor borrows shares and sells them, hoping to repurchase them later at a lower price for profit.",
        example: "An investor might short a stock at $100, hoping to buy it back at $80 for a $20 profit per share."
    },
    {
        term: "Stop Loss",
        category: "general",
        definition: "An order placed with a broker to sell a security when it reaches a certain price, designed to limit an investor's loss on a position.",
        example: "Setting a stop loss at $90 on a stock bought at $100 limits the maximum loss to $10 per share."
    }
];

// Glossary Manager Class
class GlossaryManager {
    constructor() {
        this.allTerms = glossaryTerms;
        this.filteredTerms = [...this.allTerms];
        this.currentLetter = 'all';
        this.currentCategory = '';
        this.searchTerm = '';
        
        this.initializeEventListeners();
        this.renderTerms();
        this.updateResultsCount();
    }
    
    initializeEventListeners() {
        // Search input
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterTerms();
        });
        
        // Category filter
        document.getElementById('category-filter').addEventListener('change', (e) => {
            this.currentCategory = e.target.value;
            this.filterTerms();
        });
        
        // Clear search
        document.getElementById('clear-search').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Alphabet navigation
        document.querySelectorAll('.alphabet-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentLetter = e.target.dataset.letter;
                this.updateAlphabetButtons();
                this.filterTerms();
            });
        });
    }
    
    filterTerms() {
        this.filteredTerms = this.allTerms.filter(term => {
            const matchesSearch = !this.searchTerm || 
                term.term.toLowerCase().includes(this.searchTerm) ||
                term.definition.toLowerCase().includes(this.searchTerm);
            
            const matchesCategory = !this.currentCategory || 
                term.category === this.currentCategory;
            
            const matchesLetter = this.currentLetter === 'all' || 
                term.term.charAt(0).toUpperCase() === this.currentLetter;
            
            return matchesSearch && matchesCategory && matchesLetter;
        });
        
        this.renderTerms();
        this.updateResultsCount();
    }
    
    renderTerms() {
        const container = document.getElementById('glossary-container');
        const noResults = document.getElementById('no-results');
        
        if (this.filteredTerms.length === 0) {
            container.style.display = 'none';
            noResults.style.display = 'block';
            return;
        }
        
        container.style.display = 'block';
        noResults.style.display = 'none';
        
        // Sort terms alphabetically
        const sortedTerms = [...this.filteredTerms].sort((a, b) => a.term.localeCompare(b.term));
        
        container.innerHTML = sortedTerms.map(term => this.createTermHTML(term)).join('');
    }
    
    createTermHTML(term) {
        const categoryColors = {
            stocks: 'var(--color-primary)',
            bonds: 'var(--color-success)',
            options: 'var(--color-warning)',
            forex: 'var(--color-info)',
            crypto: 'var(--color-danger)',
            technical: '#8b5cf6',
            fundamental: '#06b6d4',
            general: '#64748b'
        };
        
        return `
            <div class="glossary-term">
                <div class="term-category" style="background: ${categoryColors[term.category] || 'var(--color-primary)'}">
                    ${term.category.charAt(0).toUpperCase() + term.category.slice(1)}
                </div>
                <h3 class="term-title">${term.term}</h3>
                <p class="term-definition">${term.definition}</p>
                ${term.example ? `
                    <div class="term-example">
                        <div class="term-example-label">Example:</div>
                        <div>${term.example}</div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    updateAlphabetButtons() {
        document.querySelectorAll('.alphabet-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.letter === this.currentLetter) {
                btn.classList.add('active');
            }
        });
    }
    
    updateResultsCount() {
        const count = this.filteredTerms.length;
        document.getElementById('results-count').textContent = count;
        
        let summary = `Showing ${count} term${count !== 1 ? 's' : ''}`;
        
        if (this.searchTerm) {
            summary += ` matching "${this.searchTerm}"`;
        }
        
        if (this.currentCategory) {
            const categoryName = this.currentCategory.charAt(0).toUpperCase() + this.currentCategory.slice(1);
            summary += ` in ${categoryName}`;
        }
        
        if (this.currentLetter !== 'all') {
            summary += ` starting with "${this.currentLetter}"`;
        }
        
        document.getElementById('results-summary').innerHTML = summary;
    }
    
    clearFilters() {
        this.searchTerm = '';
        this.currentCategory = '';
        this.currentLetter = 'all';
        
        document.getElementById('search-input').value = '';
        document.getElementById('category-filter').value = '';
        
        this.updateAlphabetButtons();
        this.filterTerms();
    }
}

// Initialize glossary when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new GlossaryManager();
});
</script>

<?php get_footer(); ?>