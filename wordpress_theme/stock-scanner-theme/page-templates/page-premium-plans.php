<?php
/**
 * Template Name: Premium Plans
 * Template for the premium plans and pricing page
 */

get_header(); ?>

<div class="premium-plans-container">
    <div class="plans-header">
        <h1>Choose Your Plan</h1>
        <p class="plans-subtitle">Professional stock analysis tools for every investor</p>
    </div>
    
    <div class="plans-content">
        <?php if (have_posts()): ?>
            <?php while (have_posts()): the_post(); ?>
                <div class="page-content">
                    <?php the_content(); ?>
                </div>
            <?php endwhile; ?>
        <?php endif; ?>
        
        <div class="plan-features-comparison">
            <h2>Feature Comparison</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Free</th>
                        <th>Bronze</th>
                        <th>Silver</th>
                        <th>Gold</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>API Calls per Month</td>
                        <td>15</td>
                        <td>1,500</td>
                        <td>5,000</td>
                        <td>Unlimited</td>
                    </tr>
                    <tr>
                        <td>Real-time Quotes</td>
                        <td>Basic</td>
                        <td>✓</td>
                        <td>✓</td>
                        <td>✓</td>
                    </tr>
                    <tr>
                        <td>Advanced Charts</td>
                        <td>✗</td>
                        <td>✓</td>
                        <td>✓</td>
                        <td>✓</td>
                    </tr>
                    <tr>
                        <td>Technical Indicators</td>
                        <td>✗</td>
                        <td>✓</td>
                        <td>✓</td>
                        <td>✓</td>
                    </tr>
                    <tr>
                        <td>Portfolio Tracking</td>
                        <td>✗</td>
                        <td>✗</td>
                        <td>✓</td>
                        <td>✓</td>
                    </tr>
                    <tr>
                        <td>API Access</td>
                        <td>✗</td>
                        <td>✗</td>
                        <td>✓</td>
                        <td>✓</td>
                    </tr>
                    <tr>
                        <td>Custom Indicators</td>
                        <td>✗</td>
                        <td>✗</td>
                        <td>✗</td>
                        <td>✓</td>
                    </tr>
                    <tr>
                        <td>Support Level</td>
                        <td>Email</td>
                        <td>Priority Email</td>
                        <td>Email + Chat</td>
                        <td>24/7 Phone</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <h3>Can I change plans anytime?</h3>
                    <p>Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
                </div>
                <div class="faq-item">
                    <h3>What payment methods do you accept?</h3>
                    <p>We accept PayPal and all major credit cards through secure payment processing.</p>
                </div>
                <div class="faq-item">
                    <h3>Is there a contract or commitment?</h3>
                    <p>No, all plans are month-to-month. Cancel anytime with no cancellation fees.</p>
                </div>
                <div class="faq-item">
                    <h3>Do you offer refunds?</h3>
                    <p>We offer a 30-day money-back guarantee for all paid plans.</p>
                </div>
            </div>
        </div>
        
        <div class="security-info">
            <h2>Security & Reliability</h2>
            <div class="security-badges">
                <div class="badge-item">
                    <span class="badge-icon">🔒</span>
                    <h4>SSL Encrypted</h4>
                    <p>All data transmission is encrypted with industry-standard SSL</p>
                </div>
                <div class="badge-item">
                    <span class="badge-icon">💳</span>
                    <h4>Secure Payments</h4>
                    <p>PayPal protected payments with fraud detection</p>
                </div>
                <div class="badge-item">
                    <span class="badge-icon">⚡</span>
                    <h4>99.9% Uptime</h4>
                    <p>Reliable service with guaranteed uptime</p>
                </div>
                <div class="badge-item">
                    <span class="badge-icon">🛡️</span>
                    <h4>Data Protection</h4>
                    <p>Your financial data is never stored or shared</p>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.premium-plans-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.plans-header {
    text-align: center;
    margin-bottom: 40px;
    padding: 40px 20px;
    background: linear-gradient(135deg, #2271b1 0%, #135e96 100%);
    color: white;
    border-radius: 12px;
}

.plans-header h1 {
    font-size: 3em;
    margin-bottom: 15px;
    font-weight: 700;
}

.plans-subtitle {
    font-size: 1.3em;
    opacity: 0.9;
    margin: 0;
}

.page-content {
    margin-bottom: 50px;
}

.plan-features-comparison {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 40px;
}

.plan-features-comparison h2 {
    text-align: center;
    color: #2271b1;
    margin-bottom: 30px;
    font-size: 2.2em;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.comparison-table th,
.comparison-table td {
    padding: 15px;
    text-align: center;
    border-bottom: 1px solid #e1e1e1;
}

.comparison-table th {
    background: #f8f9fa;
    font-weight: bold;
    color: #2271b1;
    font-size: 1.1em;
}

.comparison-table td:first-child {
    text-align: left;
    font-weight: 600;
    color: #333;
}

.comparison-table tr:hover {
    background: #f8f9fa;
}

.faq-section {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 40px;
}

.faq-section h2 {
    text-align: center;
    color: #2271b1;
    margin-bottom: 30px;
    font-size: 2.2em;
}

.faq-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
}

.faq-item {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #2271b1;
}

.faq-item h3 {
    color: #2271b1;
    margin-bottom: 10px;
    font-size: 1.2em;
}

.faq-item p {
    color: #666;
    line-height: 1.6;
    margin: 0;
}

.security-info {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.security-info h2 {
    text-align: center;
    color: #2271b1;
    margin-bottom: 30px;
    font-size: 2.2em;
}

.security-badges {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 25px;
}

.badge-item {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    transition: transform 0.3s ease;
}

.badge-item:hover {
    transform: translateY(-5px);
}

.badge-icon {
    font-size: 2.5em;
    display: block;
    margin-bottom: 10px;
}

.badge-item h4 {
    color: #2271b1;
    margin-bottom: 10px;
    font-size: 1.2em;
}

.badge-item p {
    color: #666;
    margin: 0;
    line-height: 1.5;
}

@media (max-width: 768px) {
    .plans-header h1 {
        font-size: 2.2em;
    }
    
    .plans-subtitle {
        font-size: 1.1em;
    }
    
    .comparison-table {
        font-size: 0.9em;
    }
    
    .comparison-table th,
    .comparison-table td {
        padding: 10px 8px;
    }
    
    .faq-grid,
    .security-badges {
        grid-template-columns: 1fr;
    }
}
</style>

<?php get_footer(); ?>