<?php
/**
 * Template Name: Login
 * 
 * The template for displaying the login page
 */

// Redirect if already logged in
if (is_user_logged_in()) {
    wp_redirect(home_url('/dashboard/'));
    exit;
}

get_header(); 
?>

<div class="login-container">
    <div class="login-content">
        <div class="login-card">
            <div class="login-header">
                <div class="logo-section">
                    <i class="fas fa-chart-line logo-icon"></i>
                    <h1 class="site-title">Stock Scanner Pro</h1>
                </div>
                <h2 class="login-title">Welcome Back</h2>
                <p class="login-subtitle">Sign in to access your portfolio and trading tools</p>
            </div>

            <div class="login-form-container">
                <form id="loginForm" class="login-form" method="post">
                    <?php wp_nonce_field('login_action', 'login_nonce'); ?>
                    
                    <div class="form-group">
                        <label for="username">Username or Email</label>
                        <div class="input-group">
                            <i class="fas fa-user input-icon"></i>
                            <input type="text" 
                                   id="username" 
                                   name="log" 
                                   class="form-input" 
                                   placeholder="Enter your username or email" 
                                   required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="password">Password</label>
                        <div class="input-group">
                            <i class="fas fa-lock input-icon"></i>
                            <input type="password" 
                                   id="password" 
                                   name="pwd" 
                                   class="form-input" 
                                   placeholder="Enter your password" 
                                   required>
                            <button type="button" class="password-toggle" id="passwordToggle">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </div>

                    <div class="form-options">
                        <label class="checkbox-label">
                            <input type="checkbox" name="rememberme" value="forever">
                            <span class="checkbox-custom"></span>
                            Remember me
                        </label>
                        <a href="<?php echo wp_lostpassword_url(); ?>" class="forgot-password">
                            Forgot password?
                        </a>
                    </div>

                    <button type="submit" class="login-btn" id="loginBtn">
                        <span class="btn-text">Sign In</span>
                        <i class="fas fa-spinner fa-spin btn-loading" style="display: none;"></i>
                    </button>

                    <div class="login-divider">
                        <span>or</span>
                    </div>

                    <div class="social-login">
                        <button type="button" class="social-btn google-btn">
                            <i class="fab fa-google"></i>
                            Continue with Google
                        </button>
                        <button type="button" class="social-btn facebook-btn">
                            <i class="fab fa-facebook-f"></i>
                            Continue with Facebook
                        </button>
                    </div>
                </form>

                <div class="signup-prompt">
                    <p>Don't have an account? <a href="/signup/">Create one here</a></p>
                </div>
            </div>
        </div>

        <div class="login-features">
            <h3>Why Choose Stock Scanner Pro?</h3>
            <div class="features-list">
                <div class="feature-item">
                    <i class="fas fa-chart-line feature-icon"></i>
                    <div class="feature-content">
                        <h4>Real-Time Data</h4>
                        <p>Access live market data and instant price updates</p>
                    </div>
                </div>
                <div class="feature-item">
                    <i class="fas fa-search-dollar feature-icon"></i>
                    <div class="feature-content">
                        <h4>Advanced Screening</h4>
                        <p>Find investment opportunities with powerful filters</p>
                    </div>
                </div>
                <div class="feature-item">
                    <i class="fas fa-brain feature-icon"></i>
                    <div class="feature-content">
                        <h4>AI-Powered Insights</h4>
                        <p>Get intelligent market analysis and recommendations</p>
                    </div>
                </div>
                <div class="feature-item">
                    <i class="fas fa-shield-alt feature-icon"></i>
                    <div class="feature-content">
                        <h4>Secure & Reliable</h4>
                        <p>Your data is protected with enterprise-grade security</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.login-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.login-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    max-width: 1200px;
    width: 100%;
    align-items: center;
}

.login-card {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
}

.login-header {
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

.login-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
}

.login-subtitle {
    color: #666;
    font-size: 1.1rem;
    margin: 0;
}

.login-form-container {
    width: 100%;
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

.form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    color: #666;
    font-size: 0.9rem;
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

.forgot-password {
    color: #3685fb;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
}

.forgot-password:hover {
    text-decoration: underline;
}

.login-btn {
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

.login-btn:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(54, 133, 251, 0.3);
}

.login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.btn-loading {
    position: absolute;
}

.login-divider {
    text-align: center;
    margin: 2rem 0;
    position: relative;
    color: #666;
}

.login-divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: #e1e5e9;
}

.login-divider span {
    background: white;
    padding: 0 1rem;
    position: relative;
}

.social-login {
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

.signup-prompt {
    text-align: center;
    color: #666;
}

.signup-prompt a {
    color: #3685fb;
    text-decoration: none;
    font-weight: 600;
}

.signup-prompt a:hover {
    text-decoration: underline;
}

.login-features {
    color: white;
}

.login-features h3 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 2rem 0;
    text-align: center;
}

.features-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.feature-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.feature-icon {
    font-size: 2rem;
    color: #ffffff;
    flex-shrink: 0;
    margin-top: 0.25rem;
}

.feature-content h4 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
}

.feature-content p {
    margin: 0;
    opacity: 0.9;
    line-height: 1.5;
}

/* Error Messages */
.error-message {
    background: #fee2e2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    text-align: center;
    font-weight: 500;
}

@media (max-width: 968px) {
    .login-content {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .login-features {
        order: -1;
    }
    
    .login-features h3 {
        font-size: 1.5rem;
    }
    
    .features-list {
        flex-direction: row;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .feature-item {
        flex: 1;
        min-width: 250px;
    }
}

@media (max-width: 768px) {
    .login-container {
        padding: 1rem;
    }
    
    .login-card {
        padding: 2rem;
    }
    
    .features-list {
        flex-direction: column;
    }
    
    .feature-item {
        min-width: auto;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeLoginForm();
});

function initializeLoginForm() {
    const form = document.getElementById('loginForm');
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    
    // Password toggle functionality
    passwordToggle.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = this.querySelector('i');
        icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleLogin();
    });
    
    // Social login buttons
    document.querySelector('.google-btn').addEventListener('click', function() {
        handleSocialLogin('google');
    });
    
    document.querySelector('.facebook-btn').addEventListener('click', function() {
        handleSocialLogin('facebook');
    });
}

function handleLogin() {
    const form = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoading = loginBtn.querySelector('.btn-loading');
    
    // Show loading state
    loginBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline-block';
    
    // Remove any existing error messages
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Simulate login process
    setTimeout(() => {
        const formData = new FormData(form);
        const username = formData.get('log');
        const password = formData.get('pwd');
        
        // Basic validation
        if (!username || !password) {
            showError('Please fill in all fields.');
            resetLoginButton();
            return;
        }
        
        // Simulate successful login (in real app, this would be an AJAX call)
        if (username === 'demo' && password === 'demo') {
            // Successful login
            showSuccess('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = '/dashboard/';
            }, 1500);
        } else {
            // Failed login
            showError('Invalid username or password. Please try again.');
            resetLoginButton();
        }
    }, 1500);
}

function handleSocialLogin(provider) {
    console.log(`Initiating ${provider} login...`);
    // In a real app, this would redirect to the OAuth provider
    showInfo(`${provider.charAt(0).toUpperCase() + provider.slice(1)} login coming soon!`);
}

function resetLoginButton() {
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoading = loginBtn.querySelector('.btn-loading');
    
    loginBtn.disabled = false;
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
    messageEl.className = 'error-message';
    messageEl.textContent = message;
    messageEl.style.background = colors[type].bg;
    messageEl.style.color = colors[type].color;
    
    const form = document.getElementById('loginForm');
    form.insertBefore(messageEl, form.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageEl.parentElement) {
            messageEl.remove();
        }
    }, 5000);
}
</script>

<?php
// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login_nonce']) && wp_verify_nonce($_POST['login_nonce'], 'login_action')) {
    $username = sanitize_text_field($_POST['log']);
    $password = $_POST['pwd'];
    $remember = isset($_POST['rememberme']);
    
    $creds = array(
        'user_login'    => $username,
        'user_password' => $password,
        'remember'      => $remember
    );
    
    $user = wp_signon($creds, false);
    
    if (is_wp_error($user)) {
        $error_message = $user->get_error_message();
        echo '<script>document.addEventListener("DOMContentLoaded", function() { showError("' . esc_js($error_message) . '"); });</script>';
    } else {
        // Successful login - redirect will be handled by WordPress
        $redirect_url = home_url('/dashboard/');
        wp_redirect($redirect_url);
        exit;
    }
}

get_footer(); 
?>