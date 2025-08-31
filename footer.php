<?php if (!defined('ABSPATH')) { exit; } ?>

<footer class="site-footer" role="contentinfo">
  <div class="footer-content">
    <!-- Brand Section -->
    <div class="footer-section">
      <h3><?php bloginfo('name'); ?></h3>
      <p><?php bloginfo('description'); ?></p>
      <p>Professional stock trading and market analysis platform designed for retail investors who want to make informed decisions.</p>
      
      <?php if ( isset($_GET['subscribed']) && $_GET['subscribed'] === '1') : ?>
        <div class="notice notice-success" role="status">
          <p><?php esc_html_e('Thanks for subscribing! Welcome to our community.', 'retail-trade-scanner'); ?></p>
        </div>
      <?php endif; ?>
    </div>
    
    <!-- Navigation Links -->
    <div class="footer-section">
      <h3><?php esc_html_e('Platform', 'retail-trade-scanner'); ?></h3>
      <ul class="footer-links">
        <li><a href="<?php echo esc_url(home_url('/dashboard/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          <?php esc_html_e('Dashboard','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/scanner/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="21 21l-4.35-4.35"></path>
          </svg>
          <?php esc_html_e('Stock Scanner','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/portfolio/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
          <?php esc_html_e('Portfolio','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/watchlists/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
          <?php esc_html_e('Watchlists','retail-trade-scanner'); ?>
        </a></li>
      </ul>
    </div>
    
    <!-- Support Links -->
    <div class="footer-section">
      <h3><?php esc_html_e('Support', 'retail-trade-scanner'); ?></h3>
      <ul class="footer-links">
        <li><a href="<?php echo esc_url(home_url('/help/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <?php esc_html_e('Help Center','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/tutorials/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <polygon points="5,3 19,12 5,21"></polygon>
          </svg>
          <?php esc_html_e('Tutorials','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/contact/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
          <?php esc_html_e('Contact Us','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/api-docs/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <polyline points="16,18 22,12 16,6"></polyline>
            <polyline points="8,6 2,12 8,18"></polyline>
          </svg>
          <?php esc_html_e('API Documentation','retail-trade-scanner'); ?>
        </a></li>
      </ul>
    </div>
    
    <!-- Legal Links -->
    <div class="footer-section">
      <h3><?php esc_html_e('Legal', 'retail-trade-scanner'); ?></h3>
      <ul class="footer-links">
        <li><a href="<?php echo esc_url(home_url('/privacy-policy/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <circle cx="12" cy="16" r="1"></circle>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <?php esc_html_e('Privacy Policy','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/terms-of-service/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10,9 9,9 8,9"></polyline>
          </svg>
          <?php esc_html_e('Terms of Service','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/disclaimer/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <?php esc_html_e('Disclaimer','retail-trade-scanner'); ?>
        </a></li>
        <li><a href="<?php echo esc_url(home_url('/careers/')); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; vertical-align: middle;">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
          <?php esc_html_e('Careers','retail-trade-scanner'); ?>
        </a></li>
      </ul>
    </div>
    
    <!-- Newsletter Subscription -->
    <div class="footer-section">
      <h3><?php esc_html_e('Stay Updated', 'retail-trade-scanner'); ?></h3>
      <p><?php esc_html_e('Get the latest market insights and platform updates delivered to your inbox.', 'retail-trade-scanner'); ?></p>
      
      <form class="footer-subscribe" method="post" action="<?php echo esc_url( admin_url('admin-post.php') ); ?>">
        <?php wp_nonce_field('rts_subscribe','rts_subscribe_nonce'); ?>
        <input type="hidden" name="action" value="rts_subscribe" />
        <input 
          type="email" 
          name="email" 
          placeholder="<?php esc_attr_e('Enter your email','retail-trade-scanner'); ?>" 
          required 
          aria-label="<?php esc_attr_e('Email address for newsletter subscription','retail-trade-scanner'); ?>"
        />
        <button type="submit" aria-label="<?php esc_attr_e('Subscribe to newsletter','retail-trade-scanner'); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22,2 15,22 11,13 2,9"></polygon>
          </svg>
          <?php esc_html_e('Subscribe', 'retail-trade-scanner'); ?>
        </button>
      </form>
      
      <div class="social-links">
        <a href="#" aria-label="Follow us on Twitter">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path>
          </svg>
        </a>
        <a href="#" aria-label="Connect on LinkedIn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
            <rect x="2" y="9" width="4" height="12"></rect>
            <circle cx="4" cy="4" r="2"></circle>
          </svg>
        </a>
        <a href="#" aria-label="View our GitHub">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
          </svg>
        </a>
        <a href="#" aria-label="Subscribe to YouTube">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"></path>
            <polygon points="9.75,15.02 15.5,11.75 9.75,8.48"></polygon>
          </svg>
        </a>
      </div>
    </div>
  </div>
  
  <div class="footer-bottom">
    <div class="container">
      <p>&copy; <?php echo esc_html( date('Y') ); ?> <?php bloginfo('name'); ?>. <?php esc_html_e('All rights reserved.', 'retail-trade-scanner'); ?></p>
      <p style="margin-top: 8px; font-size: 11px; opacity: 0.7;">
        <?php esc_html_e('Trading involves risk. Past performance is not indicative of future results. Please trade responsibly.', 'retail-trade-scanner'); ?>
      </p>
    </div>
  </div>
</footer>

<script>
// Enhanced footer interactions
(function() {
  'use strict';
  
  // Newsletter subscription feedback
  const subscribeForm = document.querySelector('.footer-subscribe');
  if (subscribeForm) {
    subscribeForm.addEventListener('submit', function(e) {
      const button = this.querySelector('button');
      const originalText = button.innerHTML;
      
      button.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"></path></svg> Subscribing...';
      button.disabled = true;
      
      // Reset after 3 seconds if form doesn't redirect
      setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
      }, 3000);
    });
  }
  
  // Social links tracking (for analytics)
  const socialLinks = document.querySelectorAll('.social-links a');
  socialLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      // Here you would typically track the social media click
      console.log('Social media link clicked:', this.getAttribute('aria-label'));
      // For now, just log it. In production, you'd integrate with your analytics
    });
  });
  
  // Animate footer elements on scroll
  const footerSections = document.querySelectorAll('.footer-section');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });
  
  footerSections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
  });
  
})();
</script>

<?php wp_footer(); ?>
</body>
</html>