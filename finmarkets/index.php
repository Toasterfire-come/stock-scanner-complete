<?php
/**
 * Main Index (blog/home fallback)
 */
get_header();
?>
<main class="site-main">
  <div class="container">
    <?php if (have_posts()): ?>
      <div class="page-header">
        <?php if (is_home() && !is_front_page()): ?>
          <h1 class="page-title"><?php single_post_title(); ?></h1>
        <?php else: ?>
          <h1 class="page-title"><?php echo esc_html(get_bloginfo('name')); ?></h1>
          <p class="page-description"><?php echo esc_html(get_bloginfo('description')); ?></p>
        <?php endif; ?>
      </div>
      <div class="pricing-table" style="grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));">
        <?php while (have_posts()): the_post(); ?>
          <article <?php post_class('card'); ?> >
            <div class="card-header">
              <h2 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
              <div class="card-subtitle"><?php echo esc_html(get_the_date()); ?></div>
            </div>
            <div class="card-body">
              <?php the_excerpt(); ?>
            </div>
            <div class="card-footer">
              <a class="btn btn-primary" href="<?php the_permalink(); ?>"><span>Read More</span></a>
            </div>
          </article>
        <?php endwhile; ?>
      </div>
      <div class="d-flex justify-content-center">
        <?php the_posts_pagination(); ?>
      </div>
    <?php else: ?>
      <div class="page-header">
        <h1 class="page-title">Welcome to Stock Scanner</h1>
        <p class="page-description">Get real-time stock data, charts, and alerts. Track your favorite stocks with our powerful dashboard.</p>
      </div>
      <div class="stock-grid">
        <div class="stock-row">
          <h3>🔥 Popular Stocks</h3>
          <?php echo do_shortcode('[stock_scanner symbol="AAPL" show_chart="true" show_details="true"]'); ?>
          <?php echo do_shortcode('[stock_scanner symbol="TSLA" show_chart="true" show_details="true"]'); ?>
          <?php echo do_shortcode('[stock_scanner symbol="NVDA" show_chart="true" show_details="true"]'); ?>
        </div>
        <div class="stock-row">
          <h3>📊 Market Indices</h3>
          <?php echo do_shortcode('[stock_scanner symbol="SPY" show_chart="true" show_details="true"]'); ?>
          <?php echo do_shortcode('[stock_scanner symbol="QQQ" show_chart="true" show_details="true"]'); ?>
          <?php echo do_shortcode('[stock_scanner symbol="DIA" show_chart="true" show_details="true"]'); ?>
        </div>
      </div>
      <div class="upgrade-notice">
        <h4>🚀 Ready to track more stocks?</h4>
        <p>Upgrade to Premium for 1,000 stocks per month or Professional for unlimited access!</p>
        <a href="/membership-plans/" class="button-premium">View Plans</a>
      </div>
    <?php endif; ?>
  </div>
</main>
<?php get_footer(); ?>