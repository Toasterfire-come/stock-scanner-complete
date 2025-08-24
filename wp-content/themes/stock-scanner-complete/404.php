<?php
/**
 * 404 Error Page Template (Modernized for v3 styles)
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <div class="card glass-card scroll-reveal" style="text-align:center;padding:2rem;">
      <div class="error-visual" style="margin-bottom:1rem;">
        <div class="section-title" style="font-size:4rem;line-height:1">404</div>
        <div style="font-size:2rem;opacity:.7">📊</div>
      </div>

      <h1 class="section-title text-gradient"><?php _e('Page Not Found', 'stock-scanner'); ?></h1>
      <p class="section-subtitle" style="max-width:680px;margin:0 auto 1rem;">
        <?php _e("Oops! The page you're looking for seems to have moved or doesn't exist.", 'stock-scanner'); ?>
      </p>

      <div class="hero-actions" style="margin:1rem 0 2rem;">
        <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">🏠 <?php _e('Homepage', 'stock-scanner'); ?></a>
        <a href="<?php echo esc_url(home_url('/premium-plans/')); ?>" class="btn btn-outline">⭐ <?php _e('Premium Plans', 'stock-scanner'); ?></a>
        <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="btn btn-outline">📞 <?php _e('Contact', 'stock-scanner'); ?></a>
      </div>

      <form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>" style="max-width:600px;margin:0 auto;display:flex;gap:.5rem">
        <label class="screen-reader-text"><?php _e('Search for:', 'stock-scanner'); ?></label>
        <input type="search" class="form-control" placeholder="<?php echo esc_attr_x('Search for stocks, tools, or help...', 'placeholder', 'stock-scanner'); ?>" name="s" />
        <button type="submit" class="btn btn-primary">🔍 <?php _e('Search', 'stock-scanner'); ?></button>
      </form>

      <div style="margin-top:2rem">
        <h3 class="section-title" style="font-size:1.25rem;margin-bottom:1rem;"><?php _e('Popular Pages:', 'stock-scanner'); ?></h3>
        <div class="features-grid">
          <a href="<?php echo esc_url(home_url('/stock-screener/')); ?>" class="card glass-card" style="text-decoration:none;padding:1rem;">
            <strong>🔍 <?php _e('Stock Screener', 'stock-scanner'); ?></strong>
            <p style="margin:.25rem 0 0;color:var(--color-text-light)"><?php _e('Find stocks', 'stock-scanner'); ?></p>
          </a>
          <a href="<?php echo esc_url(home_url('/market-overview/')); ?>" class="card glass-card" style="text-decoration:none;padding:1rem;">
            <strong>📈 <?php _e('Market Overview', 'stock-scanner'); ?></strong>
            <p style="margin:.25rem 0 0;color:var(--color-text-light)"><?php _e('Market data', 'stock-scanner'); ?></p>
          </a>
          <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="card glass-card" style="text-decoration:none;padding:1rem;">
            <strong>💼 <?php _e('Portfolio', 'stock-scanner'); ?></strong>
            <p style="margin:.25rem 0 0;color:var(--color-text-light)"><?php _e('Track investments', 'stock-scanner'); ?></p>
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<?php get_footer(); ?>