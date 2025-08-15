<?php
/**
 * Template Name: Sign Up
 * 
 * The template for displaying the user registration page
 */

// Redirect if already logged in
if (is_user_logged_in()) {
    wp_redirect(home_url('/dashboard/'));
    exit;
}

get_header(); 
?>

<div class="signup-container">
    <div class="signup-content">
        <div class="signup-card">
            <div class="signup-header">
                <div class="logo-section">
                    <i class="fas fa-chart-line logo-icon"></i>
                    <h1 class="site-title">Stock Scanner Pro</h1>
                </div>
                <h2 class="signup-title">Create Your Account</h2>
                <p class="signup-subtitle">Join thousands of traders making smarter investment decisions</p>
            </div>

            <div class="signup-form-container">
                <form id="signupForm" class="signup-form" method="post">
                    <?php wp_nonce_field('signup_action', 'signup_nonce'); ?>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="firstName">First Name</label>
                            <div class="input-group">
                                <i class="fas fa-user input-icon"></i>
                                <input type="text" 
                                       id="firstName" 
                                       name="first_name" 
                                       class="form-input" 
                                       placeholder="Enter your first name" 
                                       required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="lastName">Last Name</label>
                            <div class="input-group">
                                <i class="fas fa-user input-icon"></i>
                                <input type="text" 
                                       id="lastName" 
                                       name="last_name" 
                                       class="form-input" 
                                       placeholder="Enter your last name" 
                                       required>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="username">Username</label>
                        <div class="input-group">
                            <i class="fas fa-at input-icon"></i>
                            <input type="text" 
                                   id="username" 
                                   name="user_login" 
                                   class="form-input" 
                                   placeholder="Choose a username" 
                                   required>
                        </div>
                        <div class="field-hint">Username must be 3-20 characters, letters and numbers only</div>
                    </div>

                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <div class="input-group">
                            <i class="fas fa-envelope input-icon"></i>
                            <input type="email" 
                                   id="email" 
                                   name="user_email" 
                                   class="form-input" 
                                   placeholder="Enter your email address" 
                                   required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="password">Password</label>
                        <div class="input-group">
                            <i class="fas fa-lock input-icon"></i>
                            <input type="password" 
                                   id="password" 
                                   name="user_password" 
                                   class="form-input" 
                                   placeholder="Create a strong password" 
                                   required>
                            <button type="button" class="password-toggle" id="passwordToggle">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                        <div class="password-strength" id="passwordStrength">
                            <div class="strength-meter">
                                <div class="strength-fill"></div>
                            </div>
                            <span class="strength-text">Password strength</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword">Confirm Password</label>
                        <div class="input-group">
                            <i class="fas fa-lock input-icon"></i>
                            <input type="password" 
                                   id="confirmPassword" 
                                   name="confirm_password" 
                                   class="form-input" 
                                   placeholder="Confirm your password" 
                                   required>
                            <button type="button" class="password-toggle" id="confirmPasswordToggle">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </div>

                    <div class="form-options">
                        <label class="checkbox-label">
                            <input type="checkbox" name="agree_terms" required>
                            <span class="checkbox-custom"></span>
                            I agree to the <a href="/terms-of-service/" target="_blank">Terms of Service</a> and <a href="/privacy-policy/" target="_blank">Privacy Policy</a>
                        </label>
                    </div>

                    <div class="form-options">
                        <label class="checkbox-label">
                            <input type="checkbox" name="newsletter_subscribe" checked>
                            <span class="checkbox-custom"></span>
                            Subscribe to our newsletter for market insights and updates
                        </label>
                    </div>

                    <button type="submit" class="signup-btn" id="signupBtn">
                        <span class="btn-text">Create Account</span>
                        <i class="fas fa-spinner fa-spin btn-loading" style="display: none;"></i>
                    </button>

                    <div class="signup-divider">
                        <span>or</span>
                    </div>

                    <div class="social-signup">
                        <button type="button" class="social-btn google-btn">
                            <i class="fab fa-google"></i>
                            Sign up with Google
                        </button>
                        <button type="button" class="social-btn facebook-btn">
                            <i class="fab fa-facebook-f"></i>
                            Sign up with Facebook
                        </button>
                    </div>
                </form>

                <div class="login-prompt">
                    <p>Already have an account? <a href="/login/">Sign in here</a></p>
                </div>
            </div>
        </div>

        <div class="signup-benefits">
            <h3>Start Your Trading Journey Today</h3>
            <div class="benefits-list">
                <div class="benefit-item">
                    <i class="fas fa-chart-line benefit-icon"></i>
                    <div class="benefit-content">
                        <h4>Real-Time Market Data</h4>
                        <p>Access live stock prices, market indices, and trading volumes</p>
                    </div>
                </div>
                <div class="benefit-item">
                    <i class="fas fa-search-dollar benefit-icon"></i>
                    <div class="benefit-content">
                        <h4>Advanced Stock Screener</h4>
                        <p>Find investment opportunities with powerful filtering tools</p>
                    </div>
                </div>
                <div class="benefit-item">
                    <i class="fas fa-brain benefit-icon"></i>
                    <div class="benefit-content">
                        <h4>AI-Powered Insights</h4>
                        <p>Get intelligent market analysis and personalized recommendations</p>
                    </div>
                </div>
                <div class="benefit-item">
                    <i class="fas fa-shield-alt benefit-icon"></i>
                    <div class="benefit-content">
                        <h4>Secure & Reliable</h4>
                        <p>Your data is protected with bank-level security measures</p>
                    </div>
                </div>
            </div>
            
            <div class="trust-indicators">
                <div class="trust-item">
                    <i class="fas fa-users"></i>
                    <span>50,000+ Active Users</span>
                </div>
                <div class="trust-item">
                    <i class="fas fa-star"></i>
                    <span>4.9/5 User Rating</span>
                </div>
                <div class="trust-item">
                    <i class="fas fa-award"></i>
                    <span>Award-Winning Platform</span>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.signup-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.signup-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    max-width: 1400px;
    width: 100%;
    align-items: center;
}

.signup-card {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
}

.signup-header {
    text-align: center;
    margin-bottom: 3rem;
}

.logo-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.logo-icon {
    font-size: 2.5rem;
    color: #3685fb;
}

.site-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.signup-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
}

.signup-subtitle {
    color: #666;
    font-size: 1.1rem;
    margin: 0;
}

.signup-form-container {
    width: 100%;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #333;
}

.input-group {
    position: relative;
    display: flex;
    align-items: center;
}

.form-input {
    width: 100%;
    padding: 1rem 1rem 1rem 3rem;
    border: 2px solid #e1e5e9;
    border-radius: 12px;
    font-size: 1rem;
    outline: none;
    transition: all 0.3s ease;
    box-sizing: border-box;
}

.form-input:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 4px rgba(54, 133, 251, 0.1);
}

.input-icon {
    position: absolute;
    left: 1rem;
    color: #666;
    z-index: 1;
}

.password-toggle {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: color 0.2s;
}

.password-toggle:hover {
    color: #3685fb;
}

.field-hint {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.25rem;
}

.password-strength {
    margin-top: 0.5rem;
}

.strength-meter {
    height: 4px;
    background: #e1e5e9;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 0.25rem;
}

.strength-fill {
    height: 100%;
    width: 0%;
    background: #ef4444;
    transition: all 0.3s ease;
}

.strength-text {
    font-size: 0.85rem;
    color: #666;
}

.form-options {
    margin-bottom: 1.5rem;
}

.checkbox-label {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    cursor: pointer;
    color: #666;
    font-size: 0.9rem;
    line-height: 1.4;
}

.checkbox-label input[type="checkbox"] {
    display: none;
}

.checkbox-custom {
    width: 18px;
    height: 18px;
    border: 2px solid #e1e5e9;
    border-radius: 4px;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
    margin-top: 2px;
}

.checkbox-label input[type="checkbox"]:checked + .checkbox-custom {
    background: #3685fb;
    border-color: #3685fb;
}

.checkbox-label input[type="checkbox"]:checked + .checkbox-custom::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.checkbox-label a {
    color: #3685fb;
    text-decoration: none;
}

.checkbox-label a:hover {
    text-decoration: underline;
}

.signup-btn {
    width: 100%;
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    position: relative;
}

.signup-btn:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(54, 133, 251, 0.3);
}

.signup-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.btn-loading {
    position: absolute;
}

.signup-divider {
    text-align: center;
    margin: 2rem 0;
    position: relative;
    color: #666;
}

.signup-divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: #e1e5e9;
}

.signup-divider span {
    background: white;
    padding: 0 1rem;
    position: relative;
}

.social-signup {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
}

.social-btn {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e1e5e9;
    border-radius: 12px;
    background: white;
    color: #333;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    transition: all 0.2s;
}

.google-btn:hover {
    border-color: #db4437;
    color: #db4437;
}

.facebook-btn:hover {
    border-color: #4267B2;
    color: #4267B2;
}

.login-prompt {
    text-align: center;
    color: #666;
}

.login-prompt a {
    color: #3685fb;
    text-decoration: none;
    font-weight: 600;
}

.login-prompt a:hover {
    text-decoration: underline;
}

.signup-benefits {
    color: white;
}

.signup-benefits h3 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 2rem 0;
    text-align: center;
}

.benefits-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    margin-bottom: 3rem;
}

.benefit-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.benefit-icon {
    font-size: 2rem;
    color: #ffffff;
    flex-shrink: 0;
    margin-top: 0.25rem;
}

.benefit-content h4 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
}

.benefit-content p {
    margin: 0;
    opacity: 0.9;
    line-height: 1.5;
}

.trust-indicators {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.trust-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 500;
}

.trust-item i {
    color: #fbbf24;
    font-size: 1.25rem;
}

/* Error Messages */
.error-message, .success-message {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    text-align: center;
    font-weight: 500;
}

.error-message {
    background: #fee2e2;
    color: #dc2626;
}

.success-message {
    background: #d1fae5;
    color: #065f46;
}

@media (max-width: 1200px) {
    .signup-content {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .signup-benefits {
        order: -1;
    }
    
    .benefits-list {
        flex-direction: row;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .benefit-item {
        flex: 1;
        min-width: 250px;
    }
}

@media (max-width: 768px) {
    .signup-container {
        padding: 1rem;
    }
    
    .signup-card {
        padding: 2rem;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .benefits-list {
        flex-direction: column;
    }
    
    .benefit-item {
        min-width: auto;
    }
    
    .trust-indicators {
        text-align: center;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeSignupForm();
});

function initializeSignupForm() {
    const form = document.getElementById('signupForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordToggle = document.getElementById('passwordToggle');
    const confirmPasswordToggle = document.getElementById('confirmPasswordToggle');
    
    // Password toggle functionality
    passwordToggle.addEventListener('click', function() {
        togglePasswordVisibility(passwordInput, this);
    });
    
    confirmPasswordToggle.addEventListener('click', function() {
        togglePasswordVisibility(confirmPasswordInput, this);
    });
    
    // Password strength checker
    passwordInput.addEventListener('input', function() {
        checkPasswordStrength(this.value);
    });
    
    // Password confirmation checker
    confirmPasswordInput.addEventListener('input', function() {
        checkPasswordMatch();
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleSignup();
    });
    
    // Social signup buttons
    document.querySelector('.google-btn').addEventListener('click', function() {
        handleSocialSignup('google');
    });
    
    document.querySelector('.facebook-btn').addEventListener('click', function() {
        handleSocialSignup('facebook');
    });
    
    // Username validation
    document.getElementById('username').addEventListener('input', function() {
        validateUsername(this.value);
    });
}

function togglePasswordVisibility(input, button) {
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
    
    const icon = button.querySelector('i');
    icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
}

function checkPasswordStrength(password) {
    const strengthFill = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text');
    
    let strength = 0;
    let strengthLabel = '';
    let color = '#ef4444';
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    switch(strength) {
        case 0:
        case 1:
            strengthLabel = 'Weak';
            color = '#ef4444';
            break;
        case 2:
        case 3:
            strengthLabel = 'Fair';
            color = '#f59e0b';
            break;
        case 4:
            strengthLabel = 'Good';
            color = '#3b82f6';
            break;
        case 5:
            strengthLabel = 'Strong';
            color = '#10b981';
            break;
    }
    
    const width = (strength / 5) * 100;
    strengthFill.style.width = width + '%';
    strengthFill.style.backgroundColor = color;
    strengthText.textContent = strengthLabel;
    strengthText.style.color = color;
}

function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const confirmInput = document.getElementById('confirmPassword');
    
    if (confirmPassword && password !== confirmPassword) {
        confirmInput.style.borderColor = '#ef4444';
        showFieldError(confirmInput, 'Passwords do not match');
    } else {
        confirmInput.style.borderColor = '#e1e5e9';
        hideFieldError(confirmInput);
    }
}

function validateUsername(username) {
    const usernameInput = document.getElementById('username');
    const regex = /^[a-zA-Z0-9]{3,20}$/;
    
    if (username && !regex.test(username)) {
        usernameInput.style.borderColor = '#ef4444';
        showFieldError(usernameInput, 'Username must be 3-20 characters, letters and numbers only');
    } else {
        usernameInput.style.borderColor = '#e1e5e9';
        hideFieldError(usernameInput);
    }
}

function showFieldError(input, message) {
    let errorEl = input.parentElement.parentElement.querySelector('.field-error');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'field-error';
        errorEl.style.color = '#ef4444';
        errorEl.style.fontSize = '0.85rem';
        errorEl.style.marginTop = '0.25rem';
        input.parentElement.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function hideFieldError(input) {
    const errorEl = input.parentElement.parentElement.querySelector('.field-error');
    if (errorEl) {
        errorEl.remove();
    }
}

function handleSignup() {
    const form = document.getElementById('signupForm');
    const signupBtn = document.getElementById('signupBtn');
    const btnText = signupBtn.querySelector('.btn-text');
    const btnLoading = signupBtn.querySelector('.btn-loading');
    
    // Show loading state
    signupBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline-block';
    
    // Remove any existing messages
    const existingMessage = document.querySelector('.error-message, .success-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Get form data
    const formData = new FormData(form);
    const password = formData.get('user_password');
    const confirmPassword = formData.get('confirm_password');
    
    // Validate passwords match
    if (password !== confirmPassword) {
        showError('Passwords do not match.');
        resetSignupButton();
        return;
    }
    
    // Validate terms agreement
    if (!formData.get('agree_terms')) {
        showError('You must agree to the Terms of Service and Privacy Policy.');
        resetSignupButton();
        return;
    }
    
    // Simulate signup process
    setTimeout(() => {
        // In a real app, this would be an AJAX call
        const success = Math.random() > 0.2; // 80% success rate for demo
        
        if (success) {
            showSuccess('Account created successfully! Please check your email to verify your account.');
            setTimeout(() => {
                window.location.href = '/login/?message=account_created';
            }, 2000);
        } else {
            showError('An error occurred during registration. Please try again.');
            resetSignupButton();
        }
    }, 2000);
}

function handleSocialSignup(provider) {
    console.log(`Initiating ${provider} signup...`);
    showInfo(`${provider.charAt(0).toUpperCase() + provider.slice(1)} signup coming soon!`);
}

function resetSignupButton() {
    const signupBtn = document.getElementById('signupBtn');
    const btnText = signupBtn.querySelector('.btn-text');
    const btnLoading = signupBtn.querySelector('.btn-loading');
    
    signupBtn.disabled = false;
    btnText.style.display = 'inline';
    btnLoading.style.display = 'none';
}

function showError(message) {
    showMessage(message, 'error');
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function showInfo(message) {
    showMessage(message, 'info');
}

function showMessage(message, type) {
    const colors = {
        error: { bg: '#fee2e2', color: '#dc2626' },
        success: { bg: '#d1fae5', color: '#065f46' },
        info: { bg: '#dbeafe', color: '#1e40af' }
    };
    
    const messageEl = document.createElement('div');
    messageEl.className = type === 'error' ? 'error-message' : 'success-message';
    messageEl.textContent = message;
    messageEl.style.background = colors[type].bg;
    messageEl.style.color = colors[type].color;
    
    const form = document.getElementById('signupForm');
    form.insertBefore(messageEl, form.firstChild);
    
    // Auto-remove after 5 seconds for info messages
    if (type === 'info') {
        setTimeout(() => {
            if (messageEl.parentElement) {
                messageEl.remove();
            }
        }, 5000);
    }
}
</script>

<?php
// Handle signup form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['signup_nonce']) && wp_verify_nonce($_POST['signup_nonce'], 'signup_action')) {
    $username = sanitize_text_field($_POST['user_login']);
    $email = sanitize_email($_POST['user_email']);
    $password = $_POST['user_password'];
    $first_name = sanitize_text_field($_POST['first_name']);
    $last_name = sanitize_text_field($_POST['last_name']);
    $agree_terms = isset($_POST['agree_terms']);
    $newsletter_subscribe = isset($_POST['newsletter_subscribe']);
    
    // Validate required fields
    if (empty($username) || empty($email) || empty($password) || empty($first_name) || empty($last_name)) {
        echo '<script>document.addEventListener("DOMContentLoaded", function() { showError("Please fill in all required fields."); });</script>';
    } elseif (!$agree_terms) {
        echo '<script>document.addEventListener("DOMContentLoaded", function() { showError("You must agree to the Terms of Service and Privacy Policy."); });</script>';
    } else {
        // Create user
        $user_id = wp_create_user($username, $password, $email);
        
        if (is_wp_error($user_id)) {
            $error_message = $user_id->get_error_message();
            echo '<script>document.addEventListener("DOMContentLoaded", function() { showError("' . esc_js($error_message) . '"); });</script>';
        } else {
            // Update user meta
            wp_update_user(array(
                'ID' => $user_id,
                'first_name' => $first_name,
                'last_name' => $last_name,
                'display_name' => $first_name . ' ' . $last_name
            ));
            
            // Add custom meta
            if ($newsletter_subscribe) {
                update_user_meta($user_id, 'newsletter_subscribed', true);
            }
            
            // Set default subscription status
            update_user_meta($user_id, 'subscription_status', 'free');
            
            // Auto-login the user
            $creds = array(
                'user_login' => $username,
                'user_password' => $password,
                'remember' => true
            );
            
            $user = wp_signon($creds, false);
            
            if (!is_wp_error($user)) {
                wp_redirect(home_url('/dashboard/?welcome=1'));
                exit;
            } else {
                // Registration successful but login failed
                echo '<script>document.addEventListener("DOMContentLoaded", function() { showSuccess("Account created successfully! Please log in."); setTimeout(function() { window.location.href = "/login/"; }, 2000); });</script>';
            }
        }
    }
}

get_footer(); 
?>