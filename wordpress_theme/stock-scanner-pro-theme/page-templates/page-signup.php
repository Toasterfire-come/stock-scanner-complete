<?php
/**
 * Template Name: User Signup Page
 * Professional signup page with comprehensive legal disclaimers
 */

// Security check
if (!defined('ABSPATH')) {
    exit;
}

// Redirect if user is already logged in
if (is_user_logged_in()) {
    wp_redirect(home_url('/dashboard/'));
    exit;
}

get_header();
?>

<div class="signup-page-container">
    <!-- Prominent Legal Disclaimer Box -->
    <div class="legal-disclaimer-banner">
        <div class="disclaimer-icon">⚠️</div>
        <div class="disclaimer-content">
            <h2 class="disclaimer-title">IMPORTANT LEGAL NOTICE</h2>
            <p class="disclaimer-text">
                <strong>NO INVESTMENT ADVICE PROVIDED:</strong> This platform provides stock screening tools and market data for informational purposes only. 
                We do not provide investment advice, recommendations, or guidance. All investment decisions are entirely your own responsibility.
            </p>
            <div class="risk-warning">
                <span class="risk-icon">🚨</span>
                <strong class="risk-text">INVEST AT YOUR OWN RISK</strong>
                <span class="risk-icon">🚨</span>
            </div>
        </div>
    </div>

    <div class="signup-content-wrapper">
        <div class="signup-form-section">
            <div class="signup-header">
                <h1>Join Stock Scanner Pro</h1>
                <p class="signup-subtitle">Get access to advanced stock screening and portfolio management tools</p>
            </div>

            <!-- Signup Form -->
            <form id="user-signup-form" class="signup-form" method="post">
                <?php wp_nonce_field('user_signup_nonce', 'signup_nonce'); ?>
                
                <div class="form-step active" id="step-1">
                    <h3>Account Information</h3>
                    
                    <div class="form-group">
                        <label for="signup-email">Email Address *</label>
                        <input type="email" id="signup-email" name="user_email" required class="form-control">
                        <div class="field-error" id="email-error"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="signup-username">Username *</label>
                        <input type="text" id="signup-username" name="user_login" required class="form-control">
                        <div class="field-error" id="username-error"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="signup-password">Password *</label>
                        <input type="password" id="signup-password" name="user_pass" required class="form-control">
                        <div class="password-strength" id="password-strength"></div>
                        <div class="field-error" id="password-error"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="signup-password-confirm">Confirm Password *</label>
                        <input type="password" id="signup-password-confirm" name="user_pass_confirm" required class="form-control">
                        <div class="field-error" id="password-confirm-error"></div>
                    </div>
                    
                    <button type="button" class="btn btn-primary btn-next" onclick="nextStep()">Continue</button>
                </div>
                
                <div class="form-step" id="step-2">
                    <h3>Profile Information</h3>
                    
                    <div class="form-group">
                        <label for="signup-first-name">First Name *</label>
                        <input type="text" id="signup-first-name" name="first_name" required class="form-control">
                    </div>
                    
                    <div class="form-group">
                        <label for="signup-last-name">Last Name *</label>
                        <input type="text" id="signup-last-name" name="last_name" required class="form-control">
                    </div>
                    
                    <div class="form-group">
                        <label for="signup-experience">Investment Experience</label>
                        <select id="signup-experience" name="investment_experience" class="form-control">
                            <option value="">Select your experience level</option>
                            <option value="beginner">Beginner (Less than 1 year)</option>
                            <option value="intermediate">Intermediate (1-5 years)</option>
                            <option value="advanced">Advanced (5+ years)</option>
                            <option value="professional">Professional Trader/Advisor</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="signup-interests">Primary Investment Interests</label>
                        <div class="checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" name="interests[]" value="stocks"> Individual Stocks
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" name="interests[]" value="etfs"> ETFs
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" name="interests[]" value="options"> Options Trading
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" name="interests[]" value="crypto"> Cryptocurrency
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" name="interests[]" value="bonds"> Bonds
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" name="interests[]" value="forex"> Forex
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-navigation">
                        <button type="button" class="btn btn-secondary btn-prev" onclick="prevStep()">Back</button>
                        <button type="button" class="btn btn-primary btn-next" onclick="nextStep()">Continue</button>
                    </div>
                </div>
                
                <div class="form-step" id="step-3">
                    <h3>Legal Agreement & Terms</h3>
                    
                    <!-- Comprehensive Risk Disclosure -->
                    <div class="risk-disclosure-section">
                        <h4 class="risk-title">⚠️ INVESTMENT RISK DISCLOSURE ⚠️</h4>
                        
                        <div class="risk-warning-box">
                            <div class="risk-header">
                                <span class="risk-emoji">🚨</span>
                                <strong>INVEST AT YOUR OWN RISK</strong>
                                <span class="risk-emoji">🚨</span>
                            </div>
                            
                            <div class="risk-content">
                                <p><strong>By using this platform, you acknowledge and understand that:</strong></p>
                                
                                <ul class="risk-list">
                                    <li><strong>No Investment Advice:</strong> We do not provide investment advice, recommendations, or suggestions. All tools and data are for informational purposes only.</li>
                                    <li><strong>Past Performance:</strong> Past performance does not guarantee future results. All investments carry risk of loss.</li>
                                    <li><strong>Market Volatility:</strong> Stock prices can fluctuate dramatically and you may lose some or all of your investment.</li>
                                    <li><strong>Your Responsibility:</strong> You are solely responsible for your investment decisions and their consequences.</li>
                                    <li><strong>Professional Advice:</strong> Consult with a qualified financial advisor before making investment decisions.</li>
                                    <li><strong>Data Accuracy:</strong> While we strive for accuracy, market data may be delayed or contain errors.</li>
                                    <li><strong>No Guarantees:</strong> We make no warranties or guarantees about investment outcomes or platform performance.</li>
                                </ul>
                                
                                <div class="additional-warnings">
                                    <div class="warning-item">
                                        <span class="warning-icon">💰</span>
                                        <strong>Only invest money you can afford to lose</strong>
                                    </div>
                                    <div class="warning-item">
                                        <span class="warning-icon">📚</span>
                                        <strong>Educate yourself before investing</strong>
                                    </div>
                                    <div class="warning-item">
                                        <span class="warning-icon">🎯</span>
                                        <strong>Diversify your investments</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Legal Agreements -->
                    <div class="legal-agreements">
                        <div class="agreement-item">
                            <label class="checkbox-label required-checkbox">
                                <input type="checkbox" name="agree_terms" required id="agree-terms">
                                <span class="checkmark"></span>
                                I have read and agree to the <a href="/terms-of-service/" target="_blank">Terms of Service</a> *
                            </label>
                        </div>
                        
                        <div class="agreement-item">
                            <label class="checkbox-label required-checkbox">
                                <input type="checkbox" name="agree_privacy" required id="agree-privacy">
                                <span class="checkmark"></span>
                                I have read and agree to the <a href="/privacy-policy/" target="_blank">Privacy Policy</a> *
                            </label>
                        </div>
                        
                        <div class="agreement-item">
                            <label class="checkbox-label required-checkbox">
                                <input type="checkbox" name="acknowledge_risk" required id="acknowledge-risk">
                                <span class="checkmark"></span>
                                I acknowledge that I have read and understand the investment risk disclosure above *
                            </label>
                        </div>
                        
                        <div class="agreement-item">
                            <label class="checkbox-label required-checkbox">
                                <input type="checkbox" name="no_advice_acknowledgment" required id="no-advice">
                                <span class="checkmark"></span>
                                I understand that this platform does not provide investment advice and I am responsible for my own investment decisions *
                            </label>
                        </div>
                        
                        <div class="agreement-item">
                            <label class="checkbox-label">
                                <input type="checkbox" name="marketing_emails" id="marketing-emails">
                                <span class="checkmark"></span>
                                I would like to receive market updates and educational content via email (optional)
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-navigation">
                        <button type="button" class="btn btn-secondary btn-prev" onclick="prevStep()">Back</button>
                        <button type="submit" class="btn btn-success btn-signup" id="final-signup-btn">
                            <span class="btn-text">Create Account</span>
                            <span class="btn-loader" style="display: none;">Creating...</span>
                        </button>
                    </div>
                </div>
            </form>
            
            <!-- Login Link -->
            <div class="login-link">
                <p>Already have an account? <a href="/login/">Sign in here</a></p>
            </div>
        </div>
        
        <!-- Features Sidebar -->
        <div class="features-sidebar">
            <h3>What You'll Get</h3>
            
            <div class="feature-item">
                <div class="feature-icon">📊</div>
                <div class="feature-content">
                    <h4>Advanced Stock Screener</h4>
                    <p>Filter stocks by 50+ criteria including financials, technicals, and fundamentals</p>
                </div>
            </div>
            
            <div class="feature-item">
                <div class="feature-icon">📈</div>
                <div class="feature-content">
                    <h4>Portfolio Tracking</h4>
                    <p>Monitor your investments with real-time performance analytics and ROI tracking</p>
                </div>
            </div>
            
            <div class="feature-item">
                <div class="feature-icon">🔔</div>
                <div class="feature-content">
                    <h4>Price Alerts</h4>
                    <p>Get notified when stocks hit your target prices or meet specific conditions</p>
                </div>
            </div>
            
            <div class="feature-item">
                <div class="feature-icon">📰</div>
                <div class="feature-content">
                    <h4>Personalized News</h4>
                    <p>Curated news feed based on your portfolio and watchlist holdings</p>
                </div>
            </div>
            
            <div class="feature-item">
                <div class="feature-icon">📱</div>
                <div class="feature-content">
                    <h4>Mobile Responsive</h4>
                    <p>Access all features on any device with our responsive design</p>
                </div>
            </div>
            
            <!-- Membership Levels -->
            <div class="membership-preview">
                <h4>Membership Levels</h4>
                <div class="tier-preview">
                    <div class="tier-item">
                        <strong>Free</strong> - Basic screening & 1 portfolio
                    </div>
                    <div class="tier-item">
                        <strong>Bronze ($9.99/mo)</strong> - 5 portfolios & advanced filters
                    </div>
                    <div class="tier-item">
                        <strong>Silver ($19.99/mo)</strong> - Unlimited portfolios & alerts
                    </div>
                    <div class="tier-item">
                        <strong>Gold ($39.99/mo)</strong> - All features & priority support
                    </div>
                </div>
                <p class="upgrade-note">Start with a free account and upgrade anytime!</p>
            </div>
        </div>
    </div>
</div>

<style>
/* Signup Page Styles */
.signup-page-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Legal Disclaimer Banner */
.legal-disclaimer-banner {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
    color: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
    animation: pulse-warning 2s infinite;
}

@keyframes pulse-warning {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.disclaimer-icon {
    font-size: 3rem;
    margin-right: 20px;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

.disclaimer-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0 0 10px 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.disclaimer-text {
    margin: 0 0 15px 0;
    line-height: 1.6;
    font-size: 1.1rem;
}

.risk-warning {
    background: rgba(255,255,255,0.2);
    padding: 10px 20px;
    border-radius: 8px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.risk-icon {
    font-size: 1.2rem;
    animation: flash 1s infinite;
}

@keyframes flash {
    0%, 50% { opacity: 1; }
    25%, 75% { opacity: 0.5; }
}

.risk-text {
    font-size: 1.2rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

/* Main Content Layout */
.signup-content-wrapper {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 40px;
    margin-top: 20px;
}

/* Signup Form Section */
.signup-form-section {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.signup-header {
    text-align: center;
    margin-bottom: 30px;
}

.signup-header h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin: 0 0 10px 0;
    font-weight: 600;
}

.signup-subtitle {
    color: #7f8c8d;
    font-size: 1.1rem;
    margin: 0;
}

/* Multi-step Form */
.form-step {
    display: none;
}

.form-step.active {
    display: block;
    animation: fadeInSlide 0.5s ease-in-out;
}

@keyframes fadeInSlide {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.form-step h3 {
    color: #2c3e50;
    margin: 0 0 25px 0;
    font-size: 1.4rem;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2c3e50;
}

.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: #fafbfc;
}

.form-control:focus {
    outline: none;
    border-color: #3498db;
    background: white;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.field-error {
    color: #e74c3c;
    font-size: 0.9rem;
    margin-top: 5px;
    display: none;
}

.field-error.show {
    display: block;
}

/* Password Strength Indicator */
.password-strength {
    margin-top: 8px;
    font-size: 0.9rem;
    font-weight: 600;
}

.password-strength.weak { color: #e74c3c; }
.password-strength.medium { color: #f39c12; }
.password-strength.strong { color: #27ae60; }

/* Checkbox Group */
.checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.checkbox-label {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    transition: background 0.3s ease;
}

.checkbox-label:hover {
    background: #f8f9fa;
}

.checkbox-label input[type="checkbox"] {
    margin-right: 8px;
    transform: scale(1.2);
}

/* Risk Disclosure Section */
.risk-disclosure-section {
    background: #fff5f5;
    border: 3px solid #ff6b6b;
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 25px;
}

.risk-title {
    text-align: center;
    color: #c0392b;
    font-size: 1.3rem;
    margin: 0 0 20px 0;
    font-weight: bold;
}

.risk-warning-box {
    background: white;
    border: 2px solid #e74c3c;
    border-radius: 8px;
    padding: 20px;
}

.risk-header {
    text-align: center;
    background: #e74c3c;
    color: white;
    padding: 15px;
    margin: -20px -20px 20px -20px;
    border-radius: 6px 6px 0 0;
    font-size: 1.2rem;
    font-weight: bold;
}

.risk-emoji {
    font-size: 1.3rem;
    margin: 0 10px;
}

.risk-content p {
    font-weight: 600;
    margin-bottom: 15px;
    color: #2c3e50;
}

.risk-list {
    list-style: none;
    padding: 0;
    margin: 15px 0;
}

.risk-list li {
    background: #fef9e7;
    border-left: 4px solid #f39c12;
    padding: 12px 15px;
    margin-bottom: 10px;
    border-radius: 0 6px 6px 0;
}

.risk-list li strong {
    color: #d35400;
}

.additional-warnings {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.warning-item {
    background: #e8f6f3;
    border: 1px solid #1abc9c;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.warning-icon {
    font-size: 1.5rem;
}

/* Legal Agreements */
.legal-agreements {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
}

.agreement-item {
    margin-bottom: 15px;
    display: flex;
    align-items: flex-start;
}

.required-checkbox {
    font-weight: 600;
}

.required-checkbox input[type="checkbox"] {
    margin-right: 10px;
    transform: scale(1.3);
}

.checkmark {
    margin-left: 5px;
}

/* Buttons */
.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #2980b9, #21618c);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
    background: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background: #7f8c8d;
}

.btn-success {
    background: linear-gradient(135deg, #27ae60, #229954);
    color: white;
    font-size: 1.1rem;
    padding: 15px 30px;
}

.btn-success:hover {
    background: linear-gradient(135deg, #229954, #1e8449);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(39, 174, 96, 0.4);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
}

.form-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 30px;
}

.btn-loader {
    display: none;
}

/* Features Sidebar */
.features-sidebar {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    height: fit-content;
    position: sticky;
    top: 20px;
}

.features-sidebar h3 {
    color: #2c3e50;
    margin: 0 0 25px 0;
    font-size: 1.5rem;
    text-align: center;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

.feature-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    transition: transform 0.3s ease;
}

.feature-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.feature-icon {
    font-size: 1.8rem;
    margin-right: 15px;
    flex-shrink: 0;
}

.feature-content h4 {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 1.1rem;
}

.feature-content p {
    margin: 0;
    color: #7f8c8d;
    font-size: 0.9rem;
    line-height: 1.4;
}

/* Membership Preview */
.membership-preview {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    margin-top: 30px;
}

.membership-preview h4 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    text-align: center;
}

.tier-preview {
    margin-bottom: 15px;
}

.tier-item {
    background: white;
    padding: 10px 15px;
    border-radius: 6px;
    margin-bottom: 8px;
    border-left: 4px solid #3498db;
    font-size: 0.9rem;
}

.upgrade-note {
    text-align: center;
    font-style: italic;
    color: #7f8c8d;
    margin: 0;
    font-size: 0.9rem;
}

/* Login Link */
.login-link {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e1e5e9;
}

.login-link a {
    color: #3498db;
    text-decoration: none;
    font-weight: 600;
}

.login-link a:hover {
    text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
    .signup-content-wrapper {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .signup-form-section {
        padding: 25px;
    }
    
    .legal-disclaimer-banner {
        flex-direction: column;
        text-align: center;
    }
    
    .disclaimer-icon {
        margin-right: 0;
        margin-bottom: 15px;
    }
    
    .checkbox-group {
        grid-template-columns: 1fr;
    }
    
    .additional-warnings {
        grid-template-columns: 1fr;
    }
    
    .form-navigation {
        flex-direction: column;
        gap: 15px;
    }
    
    .form-navigation .btn {
        width: 100%;
    }
    
    .features-sidebar {
        position: static;
        margin-top: 0;
    }
}

@media (max-width: 480px) {
    .signup-page-container {
        padding: 10px;
    }
    
    .signup-form-section {
        padding: 20px;
    }
    
    .signup-header h1 {
        font-size: 2rem;
    }
    
    .legal-disclaimer-banner {
        padding: 20px;
    }
}

/* Print Styles */
@media print {
    .features-sidebar,
    .btn,
    .form-navigation {
        display: none;
    }
    
    .legal-disclaimer-banner,
    .risk-disclosure-section {
        border: 2px solid #000;
        background: #f0f0f0 !important;
        color: #000 !important;
    }
}

/* Accessibility Enhancements */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
    .legal-disclaimer-banner {
        background: #000;
        color: #fff;
        border: 3px solid #fff;
    }
    
    .risk-warning-box {
        border: 3px solid #000;
    }
    
    .btn {
        border: 2px solid #000;
    }
}
</style>

<script>
// Multi-step form functionality
let currentStep = 1;
const totalSteps = 3;

function nextStep() {
    if (validateCurrentStep()) {
        if (currentStep < totalSteps) {
            document.getElementById(`step-${currentStep}`).classList.remove('active');
            currentStep++;
            document.getElementById(`step-${currentStep}`).classList.add('active');
            
            // Scroll to top of form
            document.querySelector('.signup-form-section').scrollIntoView({ behavior: 'smooth' });
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.getElementById(`step-${currentStep}`).classList.remove('active');
        currentStep--;
        document.getElementById(`step-${currentStep}`).classList.add('active');
        
        // Scroll to top of form
        document.querySelector('.signup-form-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function validateCurrentStep() {
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    const requiredFields = currentStepElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        clearFieldError(field);
        
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            // Additional validation based on field type
            if (field.type === 'email' && !isValidEmail(field.value)) {
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            } else if (field.name === 'user_pass_confirm') {
                const password = document.getElementById('signup-password').value;
                if (field.value !== password) {
                    showFieldError(field, 'Passwords do not match');
                    isValid = false;
                }
            }
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    const errorElement = document.getElementById(field.name.replace('_', '-') + '-error') || 
                        field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
    field.style.borderColor = '#e74c3c';
}

function clearFieldError(field) {
    const errorElement = document.getElementById(field.name.replace('_', '-') + '-error') || 
                        field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.classList.remove('show');
    }
    field.style.borderColor = '';
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Password strength checker
document.getElementById('signup-password').addEventListener('input', function() {
    const password = this.value;
    const strengthElement = document.getElementById('password-strength');
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    strengthElement.className = 'password-strength';
    
    if (strength < 3) {
        strengthElement.textContent = 'Weak password';
        strengthElement.classList.add('weak');
    } else if (strength < 4) {
        strengthElement.textContent = 'Medium strength';
        strengthElement.classList.add('medium');
    } else {
        strengthElement.textContent = 'Strong password';
        strengthElement.classList.add('strong');
    }
});

// Form submission
document.getElementById('user-signup-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Validate all required checkboxes in step 3
    const requiredCheckboxes = ['agree-terms', 'agree-privacy', 'acknowledge-risk', 'no-advice'];
    let allChecked = true;
    
    requiredCheckboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (!checkbox.checked) {
            allChecked = false;
            checkbox.parentNode.style.color = '#e74c3c';
        } else {
            checkbox.parentNode.style.color = '';
        }
    });
    
    if (!allChecked) {
        alert('Please check all required agreements before creating your account.');
        return;
    }
    
    // Show loading state
    const submitBtn = document.getElementById('final-signup-btn');
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').style.display = 'none';
    submitBtn.querySelector('.btn-loader').style.display = 'inline';
    
    fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(document.getElementById('user-signup-form'))).toString() + '&action=stock_scanner_register_user'
    }).then(r => r.json()).then(res => {
        if (res.success && res.data && res.data.redirect) {
            window.location.href = res.data.redirect;
        } else {
            alert(res.data || 'Failed to create account.');
        }
    }).catch(() => {
        alert('Network error. Please try again.');
    }).finally(() => {
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').style.display = 'inline';
        submitBtn.querySelector('.btn-loader').style.display = 'none';
    });
});

// Enhanced form interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add focus effects to form controls
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentNode.classList.remove('focused');
        });
    });
    
    // Auto-clear errors when user starts typing
    formControls.forEach(control => {
        control.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
});
</script>

<?php get_footer(); ?>