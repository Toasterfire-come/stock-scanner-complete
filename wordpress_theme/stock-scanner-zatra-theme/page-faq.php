<?php
/**
 * Template Name: FAQ
 * 
 * The template for displaying frequently asked questions
 */

get_header(); 
?>

<div class="faq-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-question-circle"></i>
                Frequently Asked Questions
            </h1>
            <p class="page-subtitle">Find answers to common questions about Stock Scanner Pro</p>
        </div>
    </div>

    <div class="faq-content">
        <div class="container">
            <!-- FAQ Search -->
            <div class="faq-search">
                <div class="search-box">
                    <input type="text" id="faqSearch" placeholder="Search for answers..." class="search-input">
                    <button class="search-btn">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
                <p class="search-hint">Type your question or keywords to find relevant answers</p>
            </div>

            <!-- FAQ Categories -->
            <div class="faq-categories">
                <h2>Browse by Category</h2>
                <div class="category-tabs">
                    <button class="category-tab active" data-category="all">All Questions</button>
                    <button class="category-tab" data-category="getting-started">Getting Started</button>
                    <button class="category-tab" data-category="account">Account & Billing</button>
                    <button class="category-tab" data-category="features">Features</button>
                    <button class="category-tab" data-category="technical">Technical</button>
                    <button class="category-tab" data-category="trading">Trading</button>
                </div>
            </div>

            <!-- FAQ Items -->
            <div class="faq-sections">
                <!-- Getting Started -->
                <div class="faq-section" data-category="getting-started">
                    <h3 class="section-title">Getting Started</h3>
                    
                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>How do I create an account?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Creating an account is simple and free:</p>
                            <ol>
                                <li>Click the "Sign Up" button in the top right corner</li>
                                <li>Fill in your basic information (name, email, password)</li>
                                <li>Verify your email address by clicking the link we send you</li>
                                <li>Complete your profile setup</li>
                                <li>Start exploring our free features immediately!</li>
                            </ol>
                            <p>No credit card required for the free plan.</p>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>What's included in the free plan?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Our free plan includes:</p>
                            <ul>
                                <li>Real-time stock quotes (15-minute delay)</li>
                                <li>Basic stock screener with 5 criteria</li>
                                <li>Watchlist for up to 10 stocks</li>
                                <li>Market news and analysis</li>
                                <li>Basic portfolio tracking</li>
                                <li>Email alerts for price movements</li>
                            </ul>
                            <p>Perfect for getting started with stock analysis!</p>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>How do I add stocks to my watchlist?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Adding stocks to your watchlist is easy:</p>
                            <ol>
                                <li>Use the search bar to find any stock by symbol or company name</li>
                                <li>Click on the stock you want to add</li>
                                <li>Click the "Add to Watchlist" button (star icon)</li>
                                <li>The stock will appear in your watchlist with real-time updates</li>
                            </ol>
                            <p>You can also add stocks directly from the screener results or news articles.</p>
                        </div>
                    </div>
                </div>

                <!-- Account & Billing -->
                <div class="faq-section" data-category="account">
                    <h3 class="section-title">Account & Billing</h3>
                    
                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>How much does Stock Scanner Pro cost?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>We offer three plans to fit your needs:</p>
                            <div class="pricing-summary">
                                <div class="plan-item">
                                    <strong>Free Plan:</strong> $0/month - Basic features
                                </div>
                                <div class="plan-item">
                                    <strong>Pro Plan:</strong> $29/month - Advanced features & real-time data
                                </div>
                                <div class="plan-item">
                                    <strong>Enterprise:</strong> $99/month - Professional tools & API access
                                </div>
                            </div>
                            <p>All paid plans come with a 30-day money-back guarantee.</p>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Can I cancel my subscription anytime?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Yes! You can cancel your subscription at any time:</p>
                            <ul>
                                <li>Go to Account Settings → Billing</li>
                                <li>Click "Cancel Subscription"</li>
                                <li>Your plan will remain active until the end of your billing cycle</li>
                                <li>You'll automatically be moved to our free plan</li>
                                <li>No cancellation fees or penalties</li>
                            </ul>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Do you offer refunds?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>We offer a 30-day money-back guarantee on all paid plans. If you're not satisfied for any reason, contact our support team within 30 days of your purchase for a full refund.</p>
                        </div>
                    </div>
                </div>

                <!-- Features -->
                <div class="faq-section" data-category="features">
                    <h3 class="section-title">Features</h3>
                    
                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>What's the difference between real-time and delayed data?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p><strong>Real-time data:</strong> Stock prices update instantly as trades happen on the exchange. This is crucial for active trading and timing your trades.</p>
                            <p><strong>Delayed data:</strong> Stock prices are delayed by 15-20 minutes. This is fine for research and long-term investing but not suitable for day trading.</p>
                            <p>Our Pro and Enterprise plans include real-time data for all major exchanges.</p>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>How does the stock screener work?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Our stock screener helps you find stocks that match your criteria:</p>
                            <ul>
                                <li>Set filters like price range, market cap, P/E ratio, etc.</li>
                                <li>Choose from 50+ technical and fundamental criteria</li>
                                <li>Save your favorite screening strategies</li>
                                <li>Get real-time results from over 8,000 stocks</li>
                                <li>Export results or add them to your watchlist</li>
                            </ul>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Can I set up price alerts?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Yes! Set up unlimited price alerts on our Pro and Enterprise plans:</p>
                            <ul>
                                <li>Price target alerts (when stock reaches a specific price)</li>
                                <li>Percentage change alerts (when stock moves by X%)</li>
                                <li>Volume spike alerts</li>
                                <li>Technical indicator alerts</li>
                                <li>News and earnings alerts</li>
                            </ul>
                            <p>Receive alerts via email, SMS, or push notifications.</p>
                        </div>
                    </div>
                </div>

                <!-- Technical -->
                <div class="faq-section" data-category="technical">
                    <h3 class="section-title">Technical Support</h3>
                    
                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Which devices and browsers are supported?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p><strong>Browsers:</strong> Chrome, Firefox, Safari, Edge (latest versions)</p>
                            <p><strong>Mobile:</strong> iOS 12+ and Android 8+ via web browser</p>
                            <p><strong>Tablets:</strong> iPad and Android tablets fully supported</p>
                            <p>Our platform is fully responsive and works great on all screen sizes.</p>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Do you have a mobile app?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Currently, we offer a fully responsive web application that works excellently on mobile devices. Native iOS and Android apps are in development and will be available in Q2 2024.</p>
                            <p>You can add our web app to your home screen for a native app-like experience!</p>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Is my data secure?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Absolutely! We take security seriously:</p>
                            <ul>
                                <li>256-bit SSL encryption for all data transmission</li>
                                <li>SOC 2 Type II compliant infrastructure</li>
                                <li>Regular security audits and penetration testing</li>
                                <li>We never store your brokerage login credentials</li>
                                <li>Two-factor authentication available</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Trading -->
                <div class="faq-section" data-category="trading">
                    <h3 class="section-title">Trading & Investing</h3>
                    
                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>Can I execute trades through Stock Scanner Pro?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>Stock Scanner Pro is an analysis and research platform. We don't execute trades directly, but we integrate with major brokers:</p>
                            <ul>
                                <li>One-click trade buttons that open your broker's platform</li>
                                <li>Portfolio sync with supported brokers</li>
                                <li>Paper trading for practice and strategy testing</li>
                                <li>Export trade ideas to your preferred broker</li>
                            </ul>
                        </div>
                    </div>

                    <div class="faq-item">
                        <div class="faq-question">
                            <h4>What markets do you cover?</h4>
                            <span class="toggle-icon">+</span>
                        </div>
                        <div class="faq-answer">
                            <p>We provide comprehensive coverage:</p>
                            <ul>
                                <li><strong>US Markets:</strong> NYSE, NASDAQ, AMEX</li>
                                <li><strong>International:</strong> Major exchanges in UK, Canada, Germany, Japan</li>
                                <li><strong>Asset Classes:</strong> Stocks, ETFs, Mutual Funds, Options</li>
                                <li><strong>Indices:</strong> S&P 500, NASDAQ, Dow Jones, Russell 2000</li>
                                <li><strong>Cryptocurrencies:</strong> Bitcoin, Ethereum, and 100+ altcoins</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Still Have Questions -->
            <div class="contact-section">
                <div class="contact-card">
                    <h3>Still Have Questions?</h3>
                    <p>Can't find what you're looking for? Our support team is here to help!</p>
                    <div class="contact-options">
                        <a href="/contact/" class="btn btn-primary">
                            <i class="fas fa-envelope"></i>
                            Contact Support
                        </a>
                        <a href="/help-center/" class="btn btn-secondary">
                            <i class="fas fa-book"></i>
                            Help Center
                        </a>
                    </div>
                    <div class="response-time">
                        <i class="fas fa-clock"></i>
                        Average response time: 2 hours
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.faq-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 1rem 0 0 0;
}

.faq-content {
    padding: 3rem 0;
}

.faq-search {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    text-align: center;
}

.search-box {
    position: relative;
    max-width: 600px;
    margin: 0 auto 1rem;
}

.search-input {
    width: 100%;
    padding: 1rem 4rem 1rem 1.5rem;
    border: 2px solid #e1e5e9;
    border-radius: 50px;
    font-size: 1.1rem;
    outline: none;
    transition: border-color 0.2s;
    box-sizing: border-box;
}

.search-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.search-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: #3685fb;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    transition: background 0.2s;
}

.search-btn:hover {
    background: #2563eb;
}

.search-hint {
    color: #666;
    font-size: 0.95rem;
    margin: 0;
}

.faq-categories {
    margin-bottom: 3rem;
}

.faq-categories h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 1.5rem 0;
    color: #1a1a1a;
}

.category-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.category-tab {
    padding: 0.75rem 1.5rem;
    border: 2px solid #e1e5e9;
    border-radius: 25px;
    background: white;
    color: #666;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}

.category-tab:hover,
.category-tab.active {
    background: #3685fb;
    color: white;
    border-color: #3685fb;
}

.faq-sections {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.faq-section {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section-title {
    background: #f8f9fa;
    color: #1a1a1a;
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
    padding: 1.5rem;
    border-bottom: 1px solid #e1e5e9;
}

.faq-item {
    border-bottom: 1px solid #f0f0f0;
}

.faq-item:last-child {
    border-bottom: none;
}

.faq-question {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    cursor: pointer;
    transition: background 0.2s;
}

.faq-question:hover {
    background: #f8f9fa;
}

.faq-question h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
    flex: 1;
    padding-right: 1rem;
}

.toggle-icon {
    font-size: 1.5rem;
    font-weight: 300;
    color: #3685fb;
    transition: transform 0.2s;
}

.faq-item.active .toggle-icon {
    transform: rotate(45deg);
}

.faq-answer {
    max-height: 0;
    overflow: hidden;
    transition: all 0.3s ease;
    background: #fff;
}

.faq-item.active .faq-answer {
    max-height: 1000px;
    padding: 0 1.5rem 1.5rem;
}

.faq-answer p {
    color: #666;
    line-height: 1.6;
    margin: 0 0 1rem 0;
}

.faq-answer p:last-child {
    margin-bottom: 0;
}

.faq-answer ul,
.faq-answer ol {
    color: #666;
    line-height: 1.6;
    margin: 0 0 1rem 0;
    padding-left: 1.5rem;
}

.faq-answer li {
    margin-bottom: 0.5rem;
}

.pricing-summary {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.plan-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid #e1e5e9;
}

.plan-item:last-child {
    border-bottom: none;
}

.contact-section {
    margin-top: 3rem;
}

.contact-card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.contact-card h3 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
}

.contact-card p {
    color: #666;
    font-size: 1.1rem;
    margin: 0 0 2rem 0;
}

.contact-options {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary {
    background: #3685fb;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(54, 133, 251, 0.3);
}

.btn-secondary {
    background: #f8f9fa;
    color: #666;
    border: 1px solid #e1e5e9;
}

.btn-secondary:hover {
    background: #e1e5e9;
    color: #333;
}

.response-time {
    color: #10b981;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .category-tabs {
        justify-content: center;
    }
    
    .category-tab {
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
    }
    
    .faq-question {
        padding: 1rem;
    }
    
    .faq-question h4 {
        font-size: 1rem;
    }
    
    .faq-item.active .faq-answer {
        padding: 0 1rem 1rem;
    }
    
    .contact-options {
        flex-direction: column;
        align-items: center;
    }
    
    .btn {
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
    }
}

.faq-section.hidden {
    display: none;
}

.faq-item.hidden {
    display: none;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeFAQ();
});

function initializeFAQ() {
    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            filterByCategory(this.dataset.category);
        });
    });
    
    // FAQ accordion
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', function() {
            const faqItem = this.parentElement;
            const isActive = faqItem.classList.contains('active');
            
            // Close all other items
            document.querySelectorAll('.faq-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Toggle current item
            if (!isActive) {
                faqItem.classList.add('active');
            }
        });
    });
    
    // Search functionality
    document.getElementById('faqSearch').addEventListener('input', handleSearch);
}

function filterByCategory(category) {
    const sections = document.querySelectorAll('.faq-section');
    
    sections.forEach(section => {
        if (category === 'all') {
            section.classList.remove('hidden');
        } else {
            if (section.dataset.category === category) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        }
    });
    
    // Close all open items when switching categories
    document.querySelectorAll('.faq-item.active').forEach(item => {
        item.classList.remove('active');
    });
}

function handleSearch() {
    const searchTerm = document.getElementById('faqSearch').value.toLowerCase();
    const faqItems = document.querySelectorAll('.faq-item');
    const sections = document.querySelectorAll('.faq-section');
    
    if (searchTerm === '') {
        // Show all items and sections
        faqItems.forEach(item => item.classList.remove('hidden'));
        sections.forEach(section => section.classList.remove('hidden'));
        return;
    }
    
    // Hide all sections first
    sections.forEach(section => section.classList.add('hidden'));
    
    let hasVisibleItems = false;
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question h4').textContent.toLowerCase();
        const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
        
        if (question.includes(searchTerm) || answer.includes(searchTerm)) {
            item.classList.remove('hidden');
            item.parentElement.classList.remove('hidden');
            hasVisibleItems = true;
        } else {
            item.classList.add('hidden');
        }
    });
    
    // If no results found, show a message (you could add this functionality)
    if (!hasVisibleItems) {
        console.log('No results found for:', searchTerm);
    }
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
</script>

<?php get_footer(); ?>