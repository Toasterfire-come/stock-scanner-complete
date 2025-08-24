<?php
/**
 * Template Name: Contact Us
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
      <p class="section-subtitle"><?php _e('Get in touch with our support team or send us your feedback', 'stock-scanner'); ?></p>
    </header>

    <div class="features-grid">
      <div class="card glass-card">
        <div class="card-body">
          <h2 class="section-title" style="font-size:1.25rem"><?php _e('Send us a Message', 'stock-scanner'); ?></h2>
          <form class="contact-form" style="display:grid;gap:var(--space-4)">
            <div class="form-group">
              <label for="contact-name" class="form-label"><?php _e('Your Name *', 'stock-scanner'); ?></label>
              <input type="text" id="contact-name" class="form-control" required>
            </div>
            <div class="form-group">
              <label for="contact-email" class="form-label"><?php _e('Email Address *', 'stock-scanner'); ?></label>
              <input type="email" id="contact-email" class="form-control" required>
            </div>
            <div class="form-group">
              <label for="contact-subject" class="form-label"><?php _e('Subject *', 'stock-scanner'); ?></label>
              <select id="contact-subject" class="form-control" required>
                <option value=""><?php _e('Select a topic', 'stock-scanner'); ?></option>
                <option value="support"><?php _e('Technical Support', 'stock-scanner'); ?></option>
                <option value="billing"><?php _e('Billing & Account', 'stock-scanner'); ?></option>
                <option value="feature"><?php _e('Feature Request', 'stock-scanner'); ?></option>
                <option value="bug"><?php _e('Bug Report', 'stock-scanner'); ?></option>
                <option value="general"><?php _e('General Inquiry', 'stock-scanner'); ?></option>
              </select>
            </div>
            <div class="form-group">
              <label for="contact-message" class="form-label"><?php _e('Message *', 'stock-scanner'); ?></label>
              <textarea id="contact-message" class="form-control" rows="5" required placeholder="<?php esc_attr_e('Please describe your question or issue in detail...', 'stock-scanner'); ?>"></textarea>
            </div>
            <button type="submit" class="btn btn-primary"><?php _e('Send Message', 'stock-scanner'); ?></button>
          </form>
        </div>
      </div>

      <div class="card glass-card">
        <div class="card-body">
          <h3 class="section-title" style="font-size:1.25rem"><?php _e('Quick Support', 'stock-scanner'); ?></h3>
          <div style="display:grid;gap:var(--space-3)">
            <div style="display:flex;align-items:center;gap:var(--space-3)">
              <span style="font-size:1.5rem">📧</span>
              <div>
                <strong><?php _e('Email Support', 'stock-scanner'); ?></strong>
                <p class="section-subtitle" style="margin:0">support@stockscanner.com</p>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:var(--space-3)">
              <span style="font-size:1.5rem">⏰</span>
              <div>
                <strong><?php _e('Response Time', 'stock-scanner'); ?></strong>
                <p class="section-subtitle" style="margin:0"><?php _e('Within 24 hours', 'stock-scanner'); ?></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<?php get_footer(); ?>