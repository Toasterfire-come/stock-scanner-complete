<?php if (!defined('ABSPATH')) { exit; } ?>
  </main>
  <footer class="footer">
    <div class="container" style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
      <div>
        <div class="brand" style="margin-bottom:8px;"><span class="brand-badge"></span>FinMarkets</div>
        <div class="muted">&copy; <?php echo date('Y'); ?> FinMarkets. All rights reserved.</div>
      </div>
      <nav aria-label="Footer">
        <?php wp_nav_menu([
          'theme_location' => 'footer',
          'container' => false,
          'items_wrap' => '%3$s',
          'link_before' => '',
          'link_after' => '',
          'fallback_cb' => false
        ]); ?>
        <a href="#">Privacy</a> · <a href="#">Terms</a> · <a href="#">Security</a>
      </nav>
    </div>
  </footer>
  <?php wp_footer(); ?>
</body>
</html>