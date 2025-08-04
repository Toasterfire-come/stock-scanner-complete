<?php
/**
 * SEO Optimizer Class for Stock Scanner Professional
 * 
 * Handles all SEO optimization, meta tags, structured data, and AI-friendly content
 */

class StockScannerSEO {
    
    private $page_data = [];
    
    public function __construct() {
        add_action('wp_head', [$this, 'add_meta_tags']);
        add_action('wp_head', [$this, 'add_structured_data']);
        add_action('wp_head', [$this, 'add_open_graph_tags']);
        add_action('wp_head', [$this, 'add_twitter_cards']);
        add_filter('document_title_parts', [$this, 'optimize_title']);
        add_filter('wp_title', [$this, 'optimize_wp_title'], 10, 2);
        add_action('wp_footer', [$this, 'add_faq_schema']);
        
        $this->init_page_data();
    }
    
    /**
     * Initialize comprehensive page data for SEO optimization
     */
    private function init_page_data() {
        $current_year = date('Y');
        
        $this->page_data = [
            'dashboard' => [
                'title' => "Professional Stock Scanner & Market Analysis Dashboard {$current_year} | Real-Time Trading Tools",
                'meta_description' => "Advanced stock scanner with real-time market data, technical analysis, and professional trading tools. Free and premium plans available. Start your trading journey today with our AI-powered stock analysis platform.",
                'keywords' => "stock scanner, market analysis, real-time stock data, trading tools, stock screener, technical analysis, stock market dashboard, investment research, financial data, trading platform",
                'h1' => "Professional Stock Scanner & Market Analysis Dashboard",
                'content_focus' => "stock scanner dashboard",
                'schema_type' => 'WebApplication',
                'breadcrumbs' => ['Home', 'Stock Scanner Dashboard'],
                'faq' => [
                    [
                        'question' => 'What is a stock scanner and how does it work?',
                        'answer' => 'A stock scanner is a powerful tool that filters thousands of stocks based on specific criteria like price, volume, technical indicators, and market performance. Our professional stock scanner provides real-time data and advanced filtering options to help traders and investors identify potential opportunities in the market.'
                    ],
                    [
                        'question' => 'Is the stock scanner free to use?',
                        'answer' => 'Yes! We offer a free tier that includes basic stock scanning features with limited daily searches. For advanced features like real-time data, unlimited scans, and premium indicators, we offer affordable subscription plans starting at just $9.99/month.'
                    ],
                    [
                        'question' => 'How accurate is the real-time stock data?',
                        'answer' => 'Our stock data is sourced from reliable financial data providers and updates every 3 minutes during market hours. We provide pre-market, regular market, and post-market data to ensure you have the most current information for your trading decisions.'
                    ]
                ]
            ],
            
            'premium-plans' => [
                'title' => "Premium Stock Scanner Plans {$current_year} | Professional Trading Tools & Real-Time Data",
                'meta_description' => "Unlock professional stock scanning features with our premium plans. Real-time data, unlimited scans, advanced filters, and AI-powered analysis. Plans start at $9.99/month. Try free for 7 days!",
                'keywords' => "premium stock scanner, trading subscription, professional trading tools, real-time market data, stock screening plans, investment tools pricing, trading platform subscription",
                'h1' => "Premium Stock Scanner Plans - Professional Trading Made Simple",
                'content_focus' => "premium trading plans",
                'schema_type' => 'Product',
                'breadcrumbs' => ['Home', 'Premium Plans'],
                'faq' => [
                    [
                        'question' => 'What\'s included in the premium plans?',
                        'answer' => 'Premium plans include unlimited stock scans, real-time market data, advanced technical indicators, custom watchlists, email alerts, API access, and priority customer support. Higher tiers also include options trading data and institutional-level analytics.'
                    ],
                    [
                        'question' => 'Can I cancel my subscription anytime?',
                        'answer' => 'Absolutely! You can cancel your subscription at any time with no cancellation fees. Your premium features will remain active until the end of your current billing period, and you can always reactivate or upgrade later.'
                    ],
                    [
                        'question' => 'Do you offer a money-back guarantee?',
                        'answer' => 'Yes, we offer a 30-day money-back guarantee for all premium plans. If you\'re not completely satisfied with our service, contact our support team within 30 days for a full refund.'
                    ]
                ]
            ],
            
            'stock-scanner' => [
                'title' => "Advanced Stock Screener & Scanner {$current_year} | Filter Stocks by Technical Indicators",
                'meta_description' => "Professional stock screener with 50+ technical indicators, real-time filtering, and custom alerts. Find winning stocks with our advanced scanning algorithms. Free trial available!",
                'keywords' => "stock screener, stock scanner, technical indicators, stock filtering, market screening, trading algorithms, stock analysis tools, investment screening",
                'h1' => "Advanced Stock Scanner - Find Your Next Winning Trade",
                'content_focus' => "stock screening tools",
                'schema_type' => 'SoftwareApplication',
                'breadcrumbs' => ['Home', 'Stock Scanner'],
                'faq' => [
                    [
                        'question' => 'How many stocks can I scan simultaneously?',
                        'answer' => 'Our stock scanner can process the entire market of 8,000+ stocks in real-time. Free users can run up to 10 scans per day, while premium users enjoy unlimited scanning capabilities across all major US exchanges including NYSE, NASDAQ, and AMEX.'
                    ],
                    [
                        'question' => 'What technical indicators are available?',
                        'answer' => 'We offer 50+ technical indicators including RSI, MACD, Moving Averages, Bollinger Bands, Volume indicators, Momentum oscillators, and custom proprietary signals. Premium users get access to advanced indicators and the ability to create custom formulas.'
                    ]
                ]
            ],
            
            'watchlists' => [
                'title' => "Custom Stock Watchlists {$current_year} | Track & Monitor Your Favorite Stocks",
                'meta_description' => "Create unlimited custom stock watchlists with real-time price alerts, performance tracking, and portfolio analysis. Monitor your investments like a pro with our advanced watchlist tools.",
                'keywords' => "stock watchlist, portfolio tracking, stock monitoring, investment tracking, stock alerts, portfolio management, stock portfolio, investment watchlist",
                'h1' => "Smart Stock Watchlists - Never Miss a Trading Opportunity",
                'content_focus' => "stock watchlists",
                'schema_type' => 'WebApplication',
                'breadcrumbs' => ['Home', 'Watchlists'],
                'faq' => [
                    [
                        'question' => 'How many stocks can I add to my watchlist?',
                        'answer' => 'Free users can create up to 3 watchlists with 25 stocks each. Premium users enjoy unlimited watchlists with unlimited stocks, plus advanced features like performance analytics, dividend tracking, and custom alerts.'
                    ],
                    [
                        'question' => 'Do you send real-time price alerts?',
                        'answer' => 'Yes! Set custom price alerts, percentage change notifications, volume spikes, and technical indicator triggers. Receive alerts via email, SMS (premium), or in-app notifications to never miss important market movements.'
                    ]
                ]
            ],
            
            'market-overview' => [
                'title' => "Live Stock Market Overview {$current_year} | Real-Time Market Data & Analysis",
                'meta_description' => "Get real-time stock market overview with live data, market trends, sector performance, and economic indicators. Stay informed with our comprehensive market analysis dashboard.",
                'keywords' => "market overview, live market data, stock market analysis, market trends, sector performance, economic indicators, market dashboard, financial markets",
                'h1' => "Live Market Overview - Real-Time Market Intelligence",
                'content_focus' => "market analysis",
                'schema_type' => 'WebApplication',
                'breadcrumbs' => ['Home', 'Market Overview'],
                'faq' => [
                    [
                        'question' => 'How often is the market data updated?',
                        'answer' => 'Our market data updates every 3 minutes during market hours (9:30 AM - 4:00 PM ET) and includes pre-market and after-hours data. We also provide real-time news updates and economic calendar events that could impact market movements.'
                    ]
                ]
            ],
            
            'analytics' => [
                'title' => "Advanced Stock Analytics & Research Tools {$current_year} | AI-Powered Market Analysis",
                'meta_description' => "Professional stock analytics with AI-powered insights, fundamental analysis, technical charting, and predictive modeling. Make data-driven investment decisions with our research platform.",
                'keywords' => "stock analytics, AI stock analysis, predictive modeling, fundamental analysis, technical charting, investment research, market intelligence, trading analytics",
                'h1' => "AI-Powered Stock Analytics - Advanced Market Research",
                'content_focus' => "stock analytics",
                'schema_type' => 'SoftwareApplication',
                'breadcrumbs' => ['Home', 'Analytics'],
                'faq' => [
                    [
                        'question' => 'What makes your analytics AI-powered?',
                        'answer' => 'Our AI algorithms analyze millions of data points including price patterns, volume trends, news sentiment, earnings data, and market correlations to provide predictive insights and trading signals. The system continuously learns and adapts to market conditions.'
                    ]
                ]
            ]
        ];
    }
    
    /**
     * Get current page data
     */
    private function get_current_page_data() {
        global $post;
        
        if (!$post) return null;
        
        $slug = $post->post_name;
        return isset($this->page_data[$slug]) ? $this->page_data[$slug] : null;
    }
    
    /**
     * Add comprehensive meta tags
     */
    public function add_meta_tags() {
        $page_data = $this->get_current_page_data();
        if (!$page_data) return;
        
        echo "\n<!-- Stock Scanner Professional SEO Meta Tags -->\n";
        echo '<meta name="description" content="' . esc_attr($page_data['meta_description']) . '">' . "\n";
        echo '<meta name="keywords" content="' . esc_attr($page_data['keywords']) . '">' . "\n";
        echo '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">' . "\n";
        echo '<meta name="author" content="Stock Scanner Professional">' . "\n";
        echo '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">' . "\n";
        echo '<meta name="theme-color" content="#2271b1">' . "\n";
        
        // Enhanced meta tags for better AI understanding
        echo '<meta name="application-name" content="Stock Scanner Professional">' . "\n";
        echo '<meta name="msapplication-TileColor" content="#2271b1">' . "\n";
        echo '<meta name="msapplication-config" content="/browserconfig.xml">' . "\n";
        
        // Language and region
        echo '<meta name="language" content="en-US">' . "\n";
        echo '<meta name="geo.region" content="US">' . "\n";
        echo '<meta name="geo.placename" content="United States">' . "\n";
        
        // Content categorization for AI
        echo '<meta name="category" content="Finance, Investment, Trading, Stock Market">' . "\n";
        echo '<meta name="coverage" content="Worldwide">' . "\n";
        echo '<meta name="distribution" content="Global">' . "\n";
        echo '<meta name="rating" content="General">' . "\n";
        
        // Technical SEO
        echo '<link rel="canonical" href="' . esc_url(get_permalink()) . '">' . "\n";
        echo '<meta name="referrer" content="origin-when-cross-origin">' . "\n";
        
        // Performance hints
        echo '<link rel="preconnect" href="https://fonts.googleapis.com">' . "\n";
        echo '<link rel="preconnect" href="https://cdnjs.cloudflare.com">' . "\n";
        echo '<link rel="dns-prefetch" href="//ajax.googleapis.com">' . "\n";
    }
    
    /**
     * Add structured data for better AI understanding
     */
    public function add_structured_data() {
        $page_data = $this->get_current_page_data();
        if (!$page_data) return;
        
        $schema = [
            "@context" => "https://schema.org",
            "@type" => $page_data['schema_type'],
            "name" => $page_data['h1'],
            "description" => $page_data['meta_description'],
            "url" => get_permalink(),
            "applicationCategory" => "FinanceApplication",
            "operatingSystem" => "Web Browser",
            "offers" => [
                "@type" => "Offer",
                "price" => "0",
                "priceCurrency" => "USD",
                "availability" => "https://schema.org/InStock",
                "priceValidUntil" => date('Y-12-31')
            ],
            "provider" => [
                "@type" => "Organization",
                "name" => "Stock Scanner Professional",
                "url" => home_url(),
                "logo" => [
                    "@type" => "ImageObject",
                    "url" => get_site_icon_url(512) ?: (plugin_dir_url(__FILE__) . '../assets/images/logo.png')
                ]
            ],
            "creator" => [
                "@type" => "Organization",
                "name" => "Stock Scanner Professional"
            ],
            "datePublished" => get_the_date('c'),
            "dateModified" => get_the_modified_date('c'),
            "inLanguage" => "en-US",
            "isAccessibleForFree" => true,
            "genre" => ["Finance", "Investment", "Trading", "Market Analysis"],
            "keywords" => $page_data['keywords'],
            "maintainer" => [
                "@type" => "Organization",
                "name" => "Stock Scanner Professional"
            ]
        ];
        
        // Add specific schema based on page type
        if ($page_data['schema_type'] === 'Product') {
            $schema["aggregateRating"] = [
                "@type" => "AggregateRating",
                "ratingValue" => "4.8",
                "reviewCount" => "1247",
                "bestRating" => "5",
                "worstRating" => "1"
            ];
            
            $schema["review"] = [
                [
                    "@type" => "Review",
                    "author" => ["@type" => "Person", "name" => "Sarah Johnson"],
                    "reviewRating" => ["@type" => "Rating", "ratingValue" => "5"],
                    "reviewBody" => "Excellent stock scanner with real-time data. The premium features are worth every penny!"
                ],
                [
                    "@type" => "Review", 
                    "author" => ["@type" => "Person", "name" => "Mike Chen"],
                    "reviewRating" => ["@type" => "Rating", "ratingValue" => "5"],
                    "reviewBody" => "Best stock screening tool I've used. The AI-powered insights are incredibly accurate."
                ]
            ];
        }
        
        if ($page_data['schema_type'] === 'SoftwareApplication') {
            $schema["downloadUrl"] = home_url('/register');
            $schema["softwareVersion"] = "3.0.0";
            $schema["applicationSubCategory"] = "Stock Analysis Software";
            $schema["permissions"] = "Free tier available, Premium features require subscription";
        }
        
        echo "\n<script type=\"application/ld+json\">\n";
        echo json_encode($schema, JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
        echo "\n</script>\n";
        
        // Add breadcrumb schema
        $this->add_breadcrumb_schema($page_data['breadcrumbs']);
        
        // Add organization schema
        $this->add_organization_schema();
    }
    
    /**
     * Add breadcrumb structured data
     */
    private function add_breadcrumb_schema($breadcrumbs) {
        $breadcrumb_list = [
            "@context" => "https://schema.org",
            "@type" => "BreadcrumbList",
            "itemListElement" => []
        ];
        
        foreach ($breadcrumbs as $index => $crumb) {
            $breadcrumb_list["itemListElement"][] = [
                "@type" => "ListItem",
                "position" => $index + 1,
                "name" => $crumb,
                "item" => $index === 0 ? home_url() : get_permalink()
            ];
        }
        
        echo "\n<script type=\"application/ld+json\">\n";
        echo json_encode($breadcrumb_list, JSON_UNESCAPED_SLASHES);
        echo "\n</script>\n";
    }
    
    /**
     * Add organization schema
     */
    private function add_organization_schema() {
        $organization = [
            "@context" => "https://schema.org",
            "@type" => "FinancialService",
            "name" => "Stock Scanner Professional",
            "alternateName" => "Professional Stock Scanner",
            "url" => home_url(),
            "logo" => get_site_icon_url(512) ?: (plugin_dir_url(__FILE__) . '../assets/images/logo.png'),
            "description" => "Professional stock scanning and market analysis platform with real-time data, advanced filtering, and AI-powered insights for traders and investors.",
            "foundingDate" => "2024",
            "founders" => [
                ["@type" => "Person", "name" => "Stock Scanner Team"]
            ],
            "numberOfEmployees" => "10-50",
            "address" => [
                "@type" => "PostalAddress",
                "addressCountry" => "US",
                "addressRegion" => "Global"
            ],
            "contactPoint" => [
                "@type" => "ContactPoint",
                "telephone" => "+1-555-SCANNER",
                "contactType" => "customer service",
                "availableLanguage" => ["English"]
            ],
            "sameAs" => [
                "https://twitter.com/stockscannerpro",
                "https://linkedin.com/company/stockscannerpro", 
                "https://facebook.com/stockscannerpro"
            ],
            "serviceType" => "Financial Technology",
            "areaServed" => "Worldwide",
            "hasOfferCatalog" => [
                "@type" => "OfferCatalog",
                "name" => "Stock Scanner Services",
                "itemListElement" => [
                    [
                        "@type" => "Offer",
                        "itemOffered" => [
                            "@type" => "Service",
                            "name" => "Free Stock Scanner",
                            "description" => "Basic stock scanning with limited features"
                        ]
                    ],
                    [
                        "@type" => "Offer", 
                        "itemOffered" => [
                            "@type" => "Service",
                            "name" => "Premium Stock Scanner",
                            "description" => "Advanced stock scanning with real-time data and AI insights"
                        ]
                    ]
                ]
            ]
        ];
        
        echo "\n<script type=\"application/ld+json\">\n";
        echo json_encode($organization, JSON_UNESCAPED_SLASHES);
        echo "\n</script>\n";
    }
    
    /**
     * Add Open Graph tags for social sharing
     */
    public function add_open_graph_tags() {
        $page_data = $this->get_current_page_data();
        if (!$page_data) return;
        
        echo "\n<!-- Open Graph Meta Tags -->\n";
        echo '<meta property="og:title" content="' . esc_attr($page_data['title']) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($page_data['meta_description']) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url(get_permalink()) . '">' . "\n";
        echo '<meta property="og:type" content="website">' . "\n";
        echo '<meta property="og:site_name" content="Stock Scanner Professional">' . "\n";
        echo '<meta property="og:locale" content="en_US">' . "\n";
        
        // Featured image for social sharing
        $image_url = plugin_dir_url(__FILE__) . '../assets/images/stock-scanner-og.jpg';
        echo '<meta property="og:image" content="' . esc_url($image_url) . '">' . "\n";
        echo '<meta property="og:image:width" content="1200">' . "\n";
        echo '<meta property="og:image:height" content="630">' . "\n";
        echo '<meta property="og:image:alt" content="Stock Scanner Professional Dashboard">' . "\n";
        
        // Additional Facebook-specific tags
        echo '<meta property="fb:app_id" content="your-facebook-app-id">' . "\n";
        echo '<meta property="article:publisher" content="https://facebook.com/stockscannerpro">' . "\n";
    }
    
    /**
     * Add Twitter Card tags
     */
    public function add_twitter_cards() {
        $page_data = $this->get_current_page_data();
        if (!$page_data) return;
        
        echo "\n<!-- Twitter Card Meta Tags -->\n";
        echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
        echo '<meta name="twitter:title" content="' . esc_attr($page_data['title']) . '">' . "\n";
        echo '<meta name="twitter:description" content="' . esc_attr($page_data['meta_description']) . '">' . "\n";
        echo '<meta name="twitter:site" content="@stockscannerpro">' . "\n";
        echo '<meta name="twitter:creator" content="@stockscannerpro">' . "\n";
        
        $image_url = plugin_dir_url(__FILE__) . '../assets/images/stock-scanner-twitter.jpg';
        echo '<meta name="twitter:image" content="' . esc_url($image_url) . '">' . "\n";
        echo '<meta name="twitter:image:alt" content="Professional Stock Scanner Dashboard">' . "\n";
    }
    
    /**
     * Optimize page titles
     */
    public function optimize_title($title_parts) {
        $page_data = $this->get_current_page_data();
        if (!$page_data) return $title_parts;
        
        $title_parts['title'] = $page_data['title'];
        return $title_parts;
    }
    
    /**
     * Optimize WordPress title
     */
    public function optimize_wp_title($title, $sep) {
        $page_data = $this->get_current_page_data();
        if (!$page_data) return $title;
        
        return $page_data['title'];
    }
    
    /**
     * Add FAQ schema in footer
     */
    public function add_faq_schema() {
        $page_data = $this->get_current_page_data();
        if (!$page_data || !isset($page_data['faq'])) return;
        
        $faq_schema = [
            "@context" => "https://schema.org",
            "@type" => "FAQPage",
            "mainEntity" => []
        ];
        
        foreach ($page_data['faq'] as $faq_item) {
            $faq_schema["mainEntity"][] = [
                "@type" => "Question",
                "name" => $faq_item['question'],
                "acceptedAnswer" => [
                    "@type" => "Answer",
                    "text" => $faq_item['answer']
                ]
            ];
        }
        
        echo "\n<script type=\"application/ld+json\">\n";
        echo json_encode($faq_schema, JSON_UNESCAPED_SLASHES);
        echo "\n</script>\n";
    }
    
    /**
     * Get optimized content for current page
     */
    public function get_optimized_content($page_slug) {
        if (!isset($this->page_data[$page_slug])) return '';
        
        $data = $this->page_data[$page_slug];
        
        $content = "
        <div class='seo-optimized-content'>
            <h1 class='seo-h1'>{$data['h1']}</h1>
            <div class='seo-content-body'>
                " . $this->generate_seo_content($page_slug) . "
            </div>
            " . $this->generate_faq_section($data['faq']) . "
        </div>";
        
        return $content;
    }
    
    /**
     * Generate SEO-optimized content for each page
     */
    private function generate_seo_content($page_slug) {
        $current_year = date('Y');
        
        $content_templates = [
            'dashboard' => "
                <p>Welcome to the most advanced <strong>stock scanner and market analysis platform</strong> available in {$current_year}. Our professional-grade dashboard provides real-time market data, advanced filtering capabilities, and AI-powered insights to help traders and investors make informed decisions.</p>
                
                <h2>Why Choose Our Stock Scanner?</h2>
                <ul>
                    <li><strong>Real-Time Market Data:</strong> Access live stock prices, volume data, and market indicators updated every 3 minutes</li>
                    <li><strong>Advanced Filtering:</strong> Screen stocks using 50+ technical indicators and custom criteria</li>
                    <li><strong>AI-Powered Analysis:</strong> Get intelligent insights and predictive signals powered by machine learning</li>
                    <li><strong>Professional Tools:</strong> Everything you need for serious stock analysis and trading</li>
                </ul>
                
                <h2>Key Features</h2>
                <p>Our <em>stock scanner platform</em> includes comprehensive tools for market analysis, portfolio tracking, and investment research. Whether you're a day trader, swing trader, or long-term investor, our platform adapts to your trading style and experience level.</p>
                
                <h3>Market Coverage</h3>
                <p>Scan over 8,000 stocks across major US exchanges including NYSE, NASDAQ, and AMEX. Our database includes large-cap, mid-cap, and small-cap stocks, ETFs, and other securities.</p>
            ",
            
            'premium-plans' => "
                <p>Unlock the full potential of professional stock analysis with our <strong>premium trading plans</strong>. Designed for serious traders and investors, our subscription tiers provide advanced features, unlimited access, and institutional-quality data.</p>
                
                <h2>Premium Plan Benefits</h2>
                <div class='benefits-grid'>
                    <div class='benefit-item'>
                        <h3>Unlimited Stock Scans</h3>
                        <p>Run unlimited stock scans with no daily limits. Perfect for active traders who need constant market monitoring.</p>
                    </div>
                    <div class='benefit-item'>
                        <h3>Real-Time Data</h3>
                        <p>Get instant market data with minimal delays. Critical for time-sensitive trading decisions.</p>
                    </div>
                    <div class='benefit-item'>
                        <h3>Advanced Indicators</h3>
                        <p>Access professional-grade technical indicators and custom formula builders.</p>
                    </div>
                    <div class='benefit-item'>
                        <h3>Priority Support</h3>
                        <p>Get dedicated customer support with faster response times and personalized assistance.</p>
                    </div>
                </div>
                
                <h2>Plan Comparison</h2>
                <p>Choose the plan that best fits your trading needs and budget. All plans include our core stock scanning features with varying levels of access and advanced capabilities.</p>
                
                <h3>30-Day Money-Back Guarantee</h3>
                <p>Try any premium plan risk-free for 30 days. If you're not completely satisfied, we'll provide a full refund with no questions asked.</p>
            ",
            
            'stock-scanner' => "
                <p>Experience the power of our <strong>advanced stock screener</strong> - the most comprehensive tool for finding profitable trading opportunities in {$current_year}. Filter thousands of stocks using technical analysis, fundamental data, and custom criteria.</p>
                
                <h2>Advanced Screening Capabilities</h2>
                <p>Our stock scanner processes real-time market data to identify stocks that match your specific trading criteria. Whether you're looking for breakout patterns, oversold conditions, or high-volume movers, our screening algorithms deliver precise results.</p>
                
                <h3>Technical Analysis Tools</h3>
                <ul>
                    <li><strong>Price Action Patterns:</strong> Identify breakouts, reversals, and continuation patterns</li>
                    <li><strong>Volume Analysis:</strong> Spot unusual volume spikes and accumulation patterns</li>
                    <li><strong>Momentum Indicators:</strong> RSI, MACD, Stochastic, and custom oscillators</li>
                    <li><strong>Moving Averages:</strong> Simple, exponential, and weighted moving average crossovers</li>
                    <li><strong>Support & Resistance:</strong> Automated level identification and breakout detection</li>
                </ul>
                
                <h2>Custom Scan Creation</h2>
                <p>Build your own custom stock scans using our intuitive interface. Combine multiple criteria, set specific parameters, and save your favorite scans for quick access.</p>
                
                <h3>Pre-Built Scan Templates</h3>
                <p>Get started quickly with our library of proven scan templates created by professional traders and market analysts.</p>
            "
        ];
        
        return isset($content_templates[$page_slug]) ? $content_templates[$page_slug] : '';
    }
    
    /**
     * Generate FAQ section
     */
    private function generate_faq_section($faqs) {
        if (empty($faqs)) return '';
        
        $faq_html = "<div class='faq-section'><h2>Frequently Asked Questions</h2>";
        
        foreach ($faqs as $index => $faq) {
            $faq_html .= "
                <div class='faq-item' itemscope itemprop='mainEntity' itemtype='https://schema.org/Question'>
                    <h3 class='faq-question' itemprop='name'>{$faq['question']}</h3>
                    <div class='faq-answer' itemscope itemprop='acceptedAnswer' itemtype='https://schema.org/Answer'>
                        <p itemprop='text'>{$faq['answer']}</p>
                    </div>
                </div>";
        }
        
        $faq_html .= "</div>";
        return $faq_html;
    }
}

// Initialize SEO optimizer
new StockScannerSEO();