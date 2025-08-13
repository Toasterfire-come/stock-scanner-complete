<?php
/**
 * Template Name: Stock Scanner Pro - Login
 * 
 * Professional login page with Zatra theme styling
 */

// Redirect if already logged in
if (is_user_logged_in()) {
    wp_redirect('/dashboard/');
    exit;
}

get_header(); ?>

<main id="main" class="wp-block-group alignfull is-layout-constrained wp-block-group-is-layout-constrained" style="margin-top:0">
    
    <div class="wp-block-group__inner-container">
        <div class="container">
            <div class="login-form-container">
                
                <!-- Login Form -->
                <div class="login-card">
                    <div class="login-header">
                        <h1 class="wp-block-heading has-large-font-size">Welcome Back</h1>
                        <p>Sign in to your Stock Scanner Pro account</p>
                    </div>

                    <?php if (isset($_GET['message'])): ?>
                        <div class="login-message <?php echo $_GET['type'] === 'error' ? 'login-error' : 'signup-success'; ?>">
                            <i class="fas fa-<?php echo $_GET['type'] === 'error' ? 'exclamation-circle' : 'check-circle'; ?>"></i>
                            <?php echo esc_html(urldecode($_GET['message'])); ?>
                        </div>
                    <?php endif; ?>

                    <form id="login-form" class="ajax-form" method="post" action="<?php echo wp_login_url(); ?>">
                        <div class="form-group">
                            <label for="username">Email or Username</label>
                            <input type="text" id="username" name="log" required 
                                   placeholder="Enter your email or username"
                                   value="<?php echo isset($_GET['username']) ? esc_attr($_GET['username']) : ''; ?>">
                        </div>

                        <div class="form-group">
                            <label for="password">Password</label>
                            <div class="password-input">
                                <input type="password" id="password" name="pwd" required 
                                       placeholder="Enter your password">
                                <button type="button" class="password-toggle">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                        </div>

                        <div class="form-options">
                            <label class="checkbox-label">
                                <input type="checkbox" name="rememberme" value="forever">
                                <span>Remember me</span>
                            </label>
                            <a href="<?php echo wp_lostpassword_url(); ?>" class="forgot-password">Forgot password?</a>
                        </div>

                        <button type="submit" class="btn btn-primary btn-full btn-large">
                            <i class="fas fa-sign-in-alt"></i> Sign In
                        </button>

                        <?php wp_nonce_field('ajax-login-nonce', 'security'); ?>
                        <input type="hidden" name="redirect_to" value="/dashboard/">
                    </form>

                    <div class="form-divider">
                        <span>or</span>
                    </div>

                    <button class="btn btn-social btn-full">
                        <i class="fab fa-google"></i> Continue with Google
                    </button>

                    <div class="login-footer">
                        <p>Don't have an account? <a href="/signup/">Sign up for free</a></p>
                    </div>
                </div>

                <!-- Login Benefits -->
                <div class="login-benefits">
                    <h2 class="wp-block-heading has-medium-font-size">Why Stock Scanner Pro?</h2>
                    <ul class="benefits-list">
                        <li>
                            <i class="fas fa-chart-line"></i>
                            <span>Real-time stock data and advanced charts</span>
                        </li>
                        <li>
                            <i class="fas fa-search"></i>
                            <span>Powerful stock screening tools</span>
                        </li>
                        <li>
                            <i class="fas fa-star"></i>
                            <span>Personal watchlist and portfolio tracking</span>
                        </li>
                        <li>
                            <i class="fas fa-newspaper"></i>
                            <span>Personalized market news and alerts</span>
                        </li>
                        <li>
                            <i class="fas fa-mobile-alt"></i>
                            <span>Access anywhere, anytime</span>
                        </li>
                        <li>
                            <i class="fas fa-shield-alt"></i>
                            <span>Bank-level security and encryption</span>
                        </li>
                    </ul>

                    <div class="testimonial-preview">
                        <blockquote>
                            <p>"Stock Scanner Pro has transformed how I analyze the market. The real-time data and intuitive interface make it indispensable for my trading strategy."</p>
                            <cite>
                                <strong>Sarah Johnson</strong>
                                <span>Professional Trader</span>
                            </cite>
                        </blockquote>
                    </div>

                    <div class="stats-preview">
                        <div class="stat-item">
                            <span class="stat-number">10,000+</span>
                            <span class="stat-label">Active Users</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">99.9%</span>
                            <span class="stat-label">Uptime</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">24/7</span>
                            <span class="stat-label">Support</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

</main>

<style>
/* Login page specific styles */
.testimonial-preview {
    margin: 32px 0;
    padding: 24px;
    background: white;
    border-radius: var(--border-radius);
    border-left: 4px solid var(--primary-color);
}

.testimonial-preview blockquote {
    margin: 0;
}

.testimonial-preview p {
    font-style: italic;
    color: var(--text-color);
    margin-bottom: 16px;
    line-height: 1.5;
}

.testimonial-preview cite {
    display: block;
    font-style: normal;
}

.testimonial-preview cite strong {
    display: block;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 4px;
}

.testimonial-preview cite span {
    font-size: 14px;
    color: var(--light-text);
}

.stats-preview {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 32px;
}

.stats-preview .stat-item {
    text-align: center;
    padding: 16px;
    background: white;
    border-radius: var(--border-radius);
}

.stats-preview .stat-number {
    display: block;
    font-size: 24px;
    font-weight: 700;
    font-family: var(--font-primary);
    color: var(--primary-color);
    margin-bottom: 4px;
}

.stats-preview .stat-label {
    font-size: 12px;
    color: var(--light-text);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.is-invalid {
    border-color: #ff6b6b !important;
    box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1) !important;
}

.is-valid {
    border-color: var(--success-color) !important;
    box-shadow: 0 0 0 3px rgba(187, 215, 0, 0.1) !important;
}

.field-error {
    color: #ff6b6b;
    font-size: 14px;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.field-error::before {
    content: "⚠";
    font-size: 12px;
}

.form-error,
.form-success {
    padding: 12px 16px;
    border-radius: var(--border-radius);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
}

.form-error {
    background: #fff5f5;
    color: #c53030;
    border: 1px solid #fed7d7;
}

.form-success {
    background: #f0fff4;
    color: #22543d;
    border: 1px solid #9ae6b4;
}

@media (max-width: 768px) {
    .stats-preview {
        grid-template-columns: 1fr;
        gap: 16px;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    // Handle form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Clear previous messages
        const existingError = this.querySelector('.form-error');
        if (existingError) existingError.remove();
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
        
        // Simulate login process (replace with actual AJAX call)
        setTimeout(() => {
            // For demo purposes, check credentials
            const username = formData.get('log');
            const password = formData.get('pwd');
            
            if (username && password) {
                // Success - redirect to dashboard
                window.location.href = '/dashboard/';
            } else {
                // Show error
                const errorDiv = document.createElement('div');
                errorDiv.className = 'form-error';
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please fill in all fields.';
                this.insertBefore(errorDiv, this.firstChild);
                
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }, 1500);
    });
    
    // Handle Google login (placeholder)
    document.querySelector('.btn-social').addEventListener('click', function(e) {
        e.preventDefault();
        alert('Google login integration would be implemented here.');
    });
    
    // Auto-focus username field
    document.getElementById('username').focus();
    
    // Add smooth animations
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.login-card, .login-benefits').forEach(el => {
        observer.observe(el);
    });
});
</script>

<?php get_footer(); ?>