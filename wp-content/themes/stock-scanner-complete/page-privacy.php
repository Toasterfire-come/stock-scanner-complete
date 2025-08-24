<?php
/**
 * Template Name: Privacy Policy (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('Privacy Policy', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('How we collect, use, and protect your personal information', 'stock-scanner'); ?></p>
    </header>

    <div class="card glass-card">
      <div class="card-body">
        <div class="privacy-content" style="display:grid;gap:var(--space-6);max-width:800px;margin:0 auto">
          <div>
            <h2><?php _e('📋 Information We Collect', 'stock-scanner'); ?></h2>
            <p><?php _e('We collect information you provide directly to us, such as when you create an account, use our services, or contact support.', 'stock-scanner'); ?></p>
          </div>
          <div>
            <h2><?php _e('🛡️ How We Use Your Information', 'stock-scanner'); ?></h2>
            <ul>
              <li><?php _e('Provide and maintain our services', 'stock-scanner'); ?></li>
              <li><?php _e('Personalize your experience and recommendations', 'stock-scanner'); ?></li>
              <li><?php _e('Communicate with you about your account', 'stock-scanner'); ?></li>
              <li><?php _e('Improve and enhance our platform', 'stock-scanner'); ?></li>
              <li><?php _e('Ensure security and prevent fraud', 'stock-scanner'); ?></li>
            </ul>
          </div>
          <div>
            <h2><?php _e('🔐 Data Security', 'stock-scanner'); ?></h2>
            <p><?php _e('We implement security measures to protect your information against unauthorized access and disclosure.', 'stock-scanner'); ?></p>
          </div>
          <div>
            <h2><?php _e('🍪 Cookies and Tracking', 'stock-scanner'); ?></h2>
            <p><?php _e('We use cookies and similar technologies to enhance your experience and analyze usage. Control cookie settings through your browser preferences.', 'stock-scanner'); ?></p>
          </div>
          <div>
            <h2><?php _e('📞 Contact Us', 'stock-scanner'); ?></h2>
            <p><?php _e('If you have questions about this policy, contact us at', 'stock-scanner'); ?> <a href="mailto:privacy@stockscanner.com">privacy@stockscanner.com</a>.</p>
          </div>
          <div style="background:var(--color-bg-lighter);padding:var(--space-4);border-radius:var(--radius-md);border-left:4px solid var(--color-primary)">
            <p style="margin:0;font-size:.875rem;">
              <strong><?php _e('Last updated:', 'stock-scanner'); ?></strong> <?php _e('January 2025', 'stock-scanner'); ?>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>