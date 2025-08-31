<?php if (!defined('ABSPATH')) { exit; } ?>
</main>
<footer class="site-footer">
  <div class="container" style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:40px;padding:48px 0;">
    <div>
      <h4>Retail Trade Scanner</h4>
      <p style="color:#6b7280;font-size:14px;">Professional stock screening, alerts and portfolio tools for serious traders.</p>
      <form id="rts-subscribe" style="display:flex;gap:8px;margin-top:12px;">
        <input class="input" type="email" placeholder="Enter your email" required />
        <button class="btn btn-secondary" type="submit">Subscribe</button>
      </form>
    </div>
    <div>
      <h5>Product</h5>
      <ul style="list-style:none;padding:0;margin:8px 0;">
        <li><a href="<?php echo esc_url(site_url('/features')); ?>">Features</a></li>
        <li><a href="<?php echo esc_url(site_url('/pricing')); ?>">Pricing</a></li>
        <li><a href="<?php echo esc_url(site_url('/use-cases')); ?>">Use cases</a></li>
      </ul>
    </div>
    <div>
      <h5>Resources</h5>
      <ul style="list-style:none;padding:0;margin:8px 0;">
        <li><a href="<?php echo esc_url(site_url('/docs')); ?>">Docs</a></li>
        <li><a href="<?php echo esc_url(site_url('/guides')); ?>">Guides</a></li>
        <li><a href="<?php echo esc_url(site_url('/tutorials')); ?>">Tutorials</a></li>
      </ul>
    </div>
    <div>
      <h5>Legal</h5>
      <ul style="list-style:none;padding:0;margin:8px 0;">
        <li><a href="<?php echo esc_url(site_url('/legal/terms')); ?>">Terms</a></li>
        <li><a href="<?php echo esc_url(site_url('/legal/privacy')); ?>">Privacy</a></li>
        <li><a href="<?php echo esc_url(site_url('/legal/security')); ?>">Security</a></li>
      </ul>
    </div>
  </div>
  <div style="border-top:1px solid var(--border);">
    <div class="container" style="display:flex;align-items:center;justify-content:space-between;padding:16px 0;color:#6b7280;font-size:12px;">
      <span>© <?php echo esc_html(date('Y')); ?> Retail Trade Scanner. All rights reserved.</span>
      <span>Trading involves risk. Past performance is not indicative of future results.</span>
    </div>
  </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>