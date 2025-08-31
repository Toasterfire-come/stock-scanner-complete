<?php
/**
 * 404 Error Page - Modern Design
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <section class="error-404 text-center py-16 fade-in">
    <div class="max-w-4xl mx-auto">
      <!-- Error Animation -->
      <div class="error-graphic mb-8">
        <div class="error-number text-9xl font-bold mb-4" style="background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; opacity: 0.8;">
          404
        </div>
        <div class="error-icon mb-6" style="color: var(--muted-foreground);">
          <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="margin: 0 auto;">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M16 16s-1.5-2-4-2-4 2-4 2"></path>
            <line x1="9" y1="9" x2="9.01" y2="9"></line>
            <line x1="15" y1="9" x2="15.01" y2="9"></line>
          </svg>
        </div>
      </div>

      <!-- Error Content -->
      <div class="error-content mb-12">
        <h1 class="text-4xl font-bold mb-6">
          <?php esc_html_e('Oops! Page Not Found', 'retail-trade-scanner'); ?>
        </h1>
        <p class="text-xl text-muted mb-8 max-w-2xl mx-auto">
          <?php esc_html_e('The page you\'re looking for seems to have vanished into the digital void. Don\'t worry, even the best traders sometimes take a wrong turn!', 'retail-trade-scanner'); ?>
        </p>
      </div>

      <!-- Quick Actions -->
      <div class="error-actions mb-12">
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
          <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9,22 9,12 15,12 15,22"></polyline>
            </svg>
            <?php esc_html_e('Go Home', 'retail-trade-scanner'); ?>
          </a>
          
          <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="btn btn-outline">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            <?php esc_html_e('View Dashboard', 'retail-trade-scanner'); ?>
          </a>
          
          <button onclick="history.back()" class="btn" style="background: var(--davys-gray); color: var(--foreground);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15,18 9,12 15,6"></polyline>
            </svg>
            <?php esc_html_e('Go Back', 'retail-trade-scanner'); ?>
          </button>
        </div>

        <!-- Enhanced Search -->
        <div class="error-search max-w-md mx-auto">
          <h3 class="text-lg font-semibold mb-4 flex items-center justify-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="21 21l-4.35-4.35"></path>
            </svg>
            <?php esc_html_e('Search for what you need', 'retail-trade-scanner'); ?>
          </h3>
          <?php get_search_form(); ?>
        </div>
      </div>

      <!-- Helpful Links -->
      <div class="helpful-links card p-8 max-w-4xl mx-auto">
        <h3 class="text-xl font-semibold mb-6 flex items-center justify-center gap-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
          <?php esc_html_e('Try These Popular Pages', 'retail-trade-scanner'); ?>
        </h3>
        
        <div class="grid grid-3 gap-6">
          <!-- Popular Pages -->
          <div class="helpful-link">
            <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="block p-4 rounded-lg transition-all hover:transform hover:scale-105" style="background: var(--surface); border: 1px solid var(--border);">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: var(--primary);">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="21 21l-4.35-4.35"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold"><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></h4>
                  <p class="text-sm text-muted"><?php esc_html_e('Find trading opportunities', 'retail-trade-scanner'); ?></p>
                </div>
              </div>
            </a>
          </div>
          
          <div class="helpful-link">
            <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="block p-4 rounded-lg transition-all hover:transform hover:scale-105" style="background: var(--surface); border: 1px solid var(--border);">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: var(--accent);">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold"><?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?></h4>
                  <p class="text-sm text-muted"><?php esc_html_e('Track your investments', 'retail-trade-scanner'); ?></p>
                </div>
              </div>
            </a>
          </div>
          
          <div class="helpful-link">
            <a href="<?php echo esc_url(home_url('/help/')); ?>" class="block p-4 rounded-lg transition-all hover:transform hover:scale-105" style="background: var(--surface); border: 1px solid var(--border);">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: var(--davys-gray);">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></h4>
                  <p class="text-sm text-muted"><?php esc_html_e('Get support & tutorials', 'retail-trade-scanner'); ?></p>
                </div>
              </div>
            </a>
          </div>
        </div>
      </div>

      <!-- Contact Support -->
      <div class="support-cta mt-8 p-6 rounded-lg" style="background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%); border: 1px solid var(--border);">
        <h3 class="text-lg font-semibold mb-3"><?php esc_html_e('Still can\'t find what you\'re looking for?', 'retail-trade-scanner'); ?></h3>
        <p class="text-muted mb-4"><?php esc_html_e('Our support team is here to help you navigate back to profitable trading.', 'retail-trade-scanner'); ?></p>
        <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="btn btn-primary">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
          <?php esc_html_e('Contact Support', 'retail-trade-scanner'); ?>
        </a>
      </div>
    </div>
  </section>
</main>

<style>
.error-404 {
  min-height: calc(100vh - var(--header-height) - 200px);
  display: flex;
  align-items: center;
}

.error-number {
  line-height: 1;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.error-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.helpful-link:hover {
  transform: translateY(-2px);
}

.error-search input[type="search"] {
  width: 100%;
  padding: 12px 16px;
  background: var(--surface);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  color: var(--foreground);
  font-size: 16px;
  transition: all 0.2s ease;
}

.error-search input[type="search"]:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(55, 74, 103, 0.1);
}

.error-search button {
  margin-top: 12px;
  width: 100%;
}

@media (max-width: 768px) {
  .error-number {
    font-size: 6rem;
  }
  
  .error-icon svg {
    width: 80px;
    height: 80px;
  }
  
  .grid-3 {
    grid-template-columns: 1fr;
  }
  
  .flex-col {
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}

/* Fun Easter Egg - Konami Code */
.konami-active .error-number {
  animation: rainbow 2s linear infinite;
}

@keyframes rainbow {
  0% { color: #ff0000; }
  14% { color: #ff7f00; }
  28% { color: #ffff00; }
  42% { color: #00ff00; }
  57% { color: #0000ff; }
  71% { color: #4b0082; }
  85% { color: #9400d3; }
  100% { color: #ff0000; }
}
</style>

<script>
// Fun Easter Egg - Konami Code
(function() {
  let konamiCode = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65];
  let userInput = [];
  
  document.addEventListener('keydown', function(e) {
    userInput.push(e.keyCode);
    
    if (userInput.length > konamiCode.length) {
      userInput.shift();
    }
    
    if (userInput.join(',') === konamiCode.join(',')) {
      document.querySelector('.error-404').classList.add('konami-active');
      
      // Show secret message
      const secretMsg = document.createElement('div');
      secretMsg.innerHTML = '<p style="margin-top: 2rem; font-size: 1.2rem; color: var(--accent);">🎉 Konami Code activated! You\'re a true trader! 📈</p>';
      document.querySelector('.error-content').appendChild(secretMsg);
      
      // Reset after 5 seconds
      setTimeout(() => {
        document.querySelector('.error-404').classList.remove('konami-active');
        secretMsg.remove();
      }, 5000);
    }
  });
})();

// Analytics tracking for 404 errors
if (typeof gtag !== 'undefined') {
  gtag('event', 'page_view', {
    page_title: '404 Error',
    page_location: window.location.href,
    custom_parameter: 'error_page'
  });
}
</script>

<?php get_footer(); ?>