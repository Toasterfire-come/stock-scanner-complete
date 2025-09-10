<?php
/**
 * Template Name: Frequently Asked Questions
 */
get_header(); ?>

<div class="faq-page">
    <div class="container">
        <div class="page-header">
            <h1>❓ Frequently Asked Questions</h1>
            <p class="page-description">Find quick answers to common questions about our platform and services</p>
        </div>

        <div class="faq-content">
            <!-- Search FAQ -->
            <div class="card p-6 mb-6">
                <div class="faq-search" style="max-width: 500px; margin: 0 auto;">
                    <label for="faq-search" style="display: block; margin-bottom: var(--space-2); color: var(--color-text); font-weight: 600;">Search FAQ</label>
                    <input type="text" id="faq-search" placeholder="Search for answers..." style="width: 100%;">
                </div>
            </div>

            <!-- FAQ Categories -->
            <div class="faq-categories" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-5);">
                
                <!-- Getting Started -->
                <div class="faq-category card p-6">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-5); display: flex; align-items: center; gap: var(--space-2);">
                         Getting Started
                    </h2>
                    <div class="faq-items" style="display: grid; gap: var(--space-4);">
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                How do I create a free account?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                Click the "Sign Up" button in the top navigation, enter your email and create a password. You'll get immediate access to free features.
                            </div>
                        </div>
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                What's included in the free plan?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                The free plan includes basic stock screening, watchlist management, and limited market data access with a monthly usage limit.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Features & Tools -->
                <div class="faq-category card p-6">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-5); display: flex; align-items: center; gap: var(--space-2);">
                        🔧 Features & Tools
                    </h2>
                    <div class="faq-items" style="display: grid; gap: var(--space-4);">
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                How accurate is the stock data?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                We use professional-grade data feeds with real-time updates during market hours and minimal delay for historical data.
                            </div>
                        </div>
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                Can I export my screening results?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                Yes, premium subscribers can export screening results to CSV format for further analysis in spreadsheet applications.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Billing & Accounts -->
                <div class="faq-category card p-6">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-5); display: flex; align-items: center; gap: var(--space-2);">
                        💳 Billing & Accounts
                    </h2>
                    <div class="faq-items" style="display: grid; gap: var(--space-4);">
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                Can I cancel my subscription anytime?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                Yes, you can cancel your subscription at any time from your account settings. You'll retain access until the end of your billing period.
                            </div>
                        </div>
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                Do you offer refunds?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                We offer a 30-day money-back guarantee for new premium subscriptions. Contact support for refund requests.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Technical Support -->
                <div class="faq-category card p-6">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-5); display: flex; align-items: center; gap: var(--space-2);">
                        🛠️ Technical Support
                    </h2>
                    <div class="faq-items" style="display: grid; gap: var(--space-4);">
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                What browsers are supported?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                We support all modern browsers including Chrome, Firefox, Safari, and Edge. Mobile browsers are also fully supported.
                            </div>
                        </div>
                        <div class="faq-item">
                            <h3 class="faq-question" style="color: var(--color-primary); cursor: pointer; margin-bottom: var(--space-2);">
                                How do I reset my password?
                            </h3>
                            <div class="faq-answer" style="color: var(--color-text-muted); line-height: 1.6;">
                                Click "Forgot Password" on the login page and enter your email. You'll receive a password reset link within minutes.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Still Have Questions -->
            <div class="card p-6 mt-6" style="text-align: center;">
                <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">Still Have Questions?</h2>
                <p style="color: var(--color-text-muted); margin-bottom: var(--space-5);">
                    Can't find the answer you're looking for? Our support team is here to help.
                </p>
                <div style="display: flex; gap: var(--space-3); justify-content: center; flex-wrap: wrap;">
                    <a href="/contact/" class="btn btn-primary">Contact Support</a>
                    <a href="/help-center/" class="btn btn-outline">Help Center</a>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.faq-page {
    padding: var(--space-10) 0;
    background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
    min-height: 100vh;
}

.faq-question {
    font-size: 1rem;
    font-weight: 600;
    transition: color 0.2s ease;
}

.faq-question:hover {
    color: var(--color-primary) !important;
}

.faq-item {
    padding-bottom: var(--space-3);
    border-bottom: 1px solid var(--color-border);
}

.faq-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

@media (max-width: 768px) {
    .faq-categories {
        grid-template-columns: 1fr !important;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // FAQ Search functionality
    const searchInput = document.getElementById('faq-search');
    const faqItems = document.querySelectorAll('.faq-item');

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question').textContent.toLowerCase();
            const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
            
            if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = searchTerm === '' ? 'block' : 'none';
            }
        });
    });

    // FAQ Toggle functionality
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const isVisible = answer.style.display === 'block';
            
            // Hide all answers
            document.querySelectorAll('.faq-answer').forEach(a => {
                a.style.display = 'none';
            });
            
            // Show clicked answer if it wasn't visible
            if (!isVisible) {
                answer.style.display = 'block';
            }
        });
    });

    // Initially hide all answers
    document.querySelectorAll('.faq-answer').forEach(answer => {
        answer.style.display = 'none';
    });
});
</script>

<?php get_footer(); ?>