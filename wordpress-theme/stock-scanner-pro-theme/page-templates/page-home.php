<?php
/**
 * Template Name: Home (Marketing)
 * 
 * Marketing homepage for Stock Scanner Pro
 *
 * @package StockScannerPro
 */

get_header(); ?>

<!-- Hero Section -->
<section class="hero-section bg-gradient-to-br from-blue-600 to-blue-800 text-white py-20">
    <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
            <h1 class="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                Professional Stock Market Analysis
            </h1>
            <p class="text-xl md:text-2xl mb-8 text-blue-100">
                Track, analyze, and manage your investments with real-time data and professional-grade tools
            </p>
            <div class="hero-actions space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
                <a href="<?php echo wp_registration_url(); ?>" class="btn-hero btn-primary">
                    Get Started Free
                </a>
                <a href="#features" class="btn-hero btn-secondary">
                    Learn More
                </a>
            </div>
            
            <!-- Trust indicators -->
            <div class="hero-stats mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                <div class="stat-item">
                    <div class="stat-number text-3xl font-bold">50,000+</div>
                    <div class="stat-label text-blue-200">Active Users</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number text-3xl font-bold">$2.5B+</div>
                    <div class="stat-label text-blue-200">Assets Tracked</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number text-3xl font-bold">99.9%</div>
                    <div class="stat-label text-blue-200">Uptime</div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Features Section -->
<section id="features" class="features-section py-20 bg-white">
    <div class="container mx-auto px-4">
        <div class="text-center mb-16">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
                Everything You Need to Succeed
            </h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
                Professional-grade tools and real-time data to help you make informed investment decisions
            </p>
        </div>

        <div class="features-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            
            <!-- Real-time Data -->
            <div class="feature-card bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                <div class="feature-icon bg-blue-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                    <i class="fas fa-chart-line text-2xl text-blue-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Real-time Market Data</h3>
                <p class="text-gray-600 mb-6">
                    Get live stock prices, market movements, and trading data updated every second during market hours.
                </p>
                <ul class="text-sm text-gray-600 space-y-2">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Live price updates
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Volume and volatility data
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        After-hours trading info
                    </li>
                </ul>
            </div>

            <!-- Portfolio Management -->
            <div class="feature-card bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                <div class="feature-icon bg-green-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                    <i class="fas fa-briefcase text-2xl text-green-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Portfolio Management</h3>
                <p class="text-gray-600 mb-6">
                    Track your investments, analyze performance, and optimize your portfolio with advanced analytics.
                </p>
                <ul class="text-sm text-gray-600 space-y-2">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Performance tracking
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Risk analysis
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Dividend tracking
                    </li>
                </ul>
            </div>

            <!-- Advanced Charts -->
            <div class="feature-card bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                <div class="feature-icon bg-purple-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                    <i class="fas fa-chart-bar text-2xl text-purple-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Advanced Charts</h3>
                <p class="text-gray-600 mb-6">
                    Professional-grade charting tools with technical indicators and customizable views.
                </p>
                <ul class="text-sm text-gray-600 space-y-2">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Technical indicators
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Multiple timeframes
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Drawing tools
                    </li>
                </ul>
            </div>

            <!-- Price Alerts -->
            <div class="feature-card bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                <div class="feature-icon bg-orange-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                    <i class="fas fa-bell text-2xl text-orange-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Smart Alerts</h3>
                <p class="text-gray-600 mb-6">
                    Never miss an opportunity with intelligent price alerts and market notifications.
                </p>
                <ul class="text-sm text-gray-600 space-y-2">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Price-based alerts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Volume alerts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        News alerts
                    </li>
                </ul>
            </div>

            <!-- Market News -->
            <div class="feature-card bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                <div class="feature-icon bg-red-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                    <i class="fas fa-newspaper text-2xl text-red-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Market Intelligence</h3>
                <p class="text-gray-600 mb-6">
                    Stay informed with curated market news, earnings reports, and analyst recommendations.
                </p>
                <ul class="text-sm text-gray-600 space-y-2">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Sentiment analysis
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Earnings calendar
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Analyst ratings
                    </li>
                </ul>
            </div>

            <!-- API Access -->
            <div class="feature-card bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                <div class="feature-icon bg-indigo-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                    <i class="fas fa-code text-2xl text-indigo-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Developer API</h3>
                <p class="text-gray-600 mb-6">
                    Build custom applications and integrations with our comprehensive RESTful API.
                </p>
                <ul class="text-sm text-gray-600 space-y-2">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        RESTful endpoints
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        Webhooks support
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-2"></i>
                        SDKs available
                    </li>
                </ul>
            </div>
        </div>
    </div>
</section>

<!-- Pricing Section -->
<section class="pricing-section py-20 bg-gray-50">
    <div class="container mx-auto px-4">
        <div class="text-center mb-16">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
                Choose Your Plan
            </h2>
            <p class="text-xl text-gray-600">
                Start free and upgrade as you grow
            </p>
        </div>

        <div class="pricing-grid grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            
            <!-- Free Plan -->
            <div class="pricing-card bg-white rounded-xl border border-gray-200 p-8">
                <div class="text-center mb-8">
                    <h3 class="text-2xl font-bold text-gray-900 mb-2">Free</h3>
                    <div class="price-display mb-4">
                        <span class="text-4xl font-bold text-gray-900">$0</span>
                        <span class="text-gray-600">/month</span>
                    </div>
                    <p class="text-gray-600">Perfect for getting started</p>
                </div>
                
                <ul class="features-list space-y-3 mb-8">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        10 watchlist items
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        1 portfolio
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        5 price alerts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Basic charts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-times text-gray-400 mr-3"></i>
                        Real-time data
                    </li>
                </ul>
                
                <a href="<?php echo wp_registration_url(); ?>" class="btn w-full btn-outline-primary">
                    Get Started Free
                </a>
            </div>

            <!-- Pro Plan -->
            <div class="pricing-card bg-white rounded-xl border-2 border-blue-500 p-8 relative">
                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span class="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                        Most Popular
                    </span>
                </div>
                
                <div class="text-center mb-8">
                    <h3 class="text-2xl font-bold text-gray-900 mb-2">Pro</h3>
                    <div class="price-display mb-4">
                        <span class="text-4xl font-bold text-gray-900">$29</span>
                        <span class="text-gray-600">/month</span>
                    </div>
                    <p class="text-gray-600">For serious investors</p>
                </div>
                
                <ul class="features-list space-y-3 mb-8">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        200 watchlist items
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        20 portfolios
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        100 price alerts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Real-time data
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Advanced charts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        News sentiment
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        API access
                    </li>
                </ul>
                
                <a href="<?php echo esc_url(get_permalink(get_page_by_path('premium-plans'))); ?>" class="btn w-full btn-primary">
                    Start Pro Trial
                </a>
            </div>

            <!-- Enterprise Plan -->
            <div class="pricing-card bg-white rounded-xl border border-gray-200 p-8">
                <div class="text-center mb-8">
                    <h3 class="text-2xl font-bold text-gray-900 mb-2">Enterprise</h3>
                    <div class="price-display mb-4">
                        <span class="text-4xl font-bold text-gray-900">$99</span>
                        <span class="text-gray-600">/month</span>
                    </div>
                    <p class="text-gray-600">For professional traders</p>
                </div>
                
                <ul class="features-list space-y-3 mb-8">
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Unlimited watchlists
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Unlimited portfolios
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Unlimited alerts
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Priority support
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        Custom integrations
                    </li>
                    <li class="flex items-center">
                        <i class="fas fa-check text-green-500 mr-3"></i>
                        White-label options
                    </li>
                </ul>
                
                <a href="<?php echo esc_url(get_permalink(get_page_by_path('contact'))); ?>" class="btn w-full btn-outline-primary">
                    Contact Sales
                </a>
            </div>
        </div>
    </div>
</section>

<!-- CTA Section -->
<section class="cta-section py-20 bg-gray-900 text-white">
    <div class="container mx-auto px-4 text-center">
        <h2 class="text-4xl font-bold mb-6">
            Ready to Take Control of Your Investments?
        </h2>
        <p class="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of investors who trust Stock Scanner Pro for their market analysis and portfolio management.
        </p>
        <div class="cta-actions space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
            <a href="<?php echo wp_registration_url(); ?>" class="btn-hero btn-primary">
                Start Free Trial
            </a>
            <a href="<?php echo esc_url(get_permalink(get_page_by_path('contact'))); ?>" class="btn-hero btn-secondary">
                Schedule Demo
            </a>
        </div>
    </div>
</section>

<style>
/* Hero Section Styles */
.btn-hero {
    display: inline-block;
    padding: 1rem 2rem;
    font-size: 1.125rem;
    font-weight: 600;
    border-radius: 0.75rem;
    transition: all 0.3s ease;
    text-decoration: none;
}

.btn-hero.btn-primary {
    background: white;
    color: #1e40af;
    border: 2px solid white;
}

.btn-hero.btn-primary:hover {
    background: #f3f4f6;
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.btn-hero.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid rgba(255,255,255,0.3);
}

.btn-hero.btn-secondary:hover {
    background: rgba(255,255,255,0.1);
    border-color: white;
}

/* Feature Cards */
.feature-card:hover {
    transform: translateY(-4px);
}

.features-list li {
    font-size: 0.875rem;
}

/* Pricing Cards */
.pricing-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.pricing-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

/* Responsive adjustments */
@media (max-width: 640px) {
    .hero-section {
        padding: 3rem 0;
    }
    
    .hero-section h1 {
        font-size: 2.5rem;
    }
    
    .hero-section p {
        font-size: 1.125rem;
    }
    
    .btn-hero {
        display: block;
        width: 100%;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .features-grid {
        gap: 1.5rem;
    }
    
    .pricing-grid {
        gap: 1.5rem;
    }
}
</style>

<?php get_footer(); ?>