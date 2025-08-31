<?php if (!defined('ABSPATH')) { exit; } ?>
</main>
<footer class="site-footer">
  <div class="container" style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:40px;padding:48px 0;">
    <div>
      <h4><?php echo esc_html__( 'Retail Trade Scanner', 'rts' ); ?></h4>
      <p style="color:#6b7280;font-size:14px;"><?php echo esc_html__( 'Professional stock screening, alerts and portfolio tools for serious traders.', 'rts' ); ?></p>
      <form id="rts-subscribe" style="display:flex;gap:8px;margin-top:12px;">
        <input class="input" type="email" placeholder="<?php echo esc_attr__( 'Enter your email', 'rts' ); ?>" required />
        <button class="btn btn-secondary" type="submit"><?php echo esc_html__( 'Subscribe', 'rts' ); ?></button>
      </form>
    </div>
    <div>
      <h5><?php echo esc_html__( 'Product', 'rts' ); ?></h5>
      <ul style="list-style:none;padding:0;margin:8px 0;">
        <li><a href="<?php echo esc_url(site_url('/features')); ?>"><?php echo esc_html__( 'Features', 'rts' ); ?></a></li>
        <li><a href="<?php echo esc_url(site_url('/pricing')); ?>"><?php echo esc_html__( 'Pricing', 'rts' ); ?></a></li>
        <li><a href="<?php echo esc_url(site_url('/use-cases')); ?>"><?php echo esc_html__( 'Use cases', 'rts' ); ?></a></li>
      </ul>
    </div>
    <div>
      <h5><?php echo esc_html__( 'Resources', 'rts' ); ?></h5>
      <ul style="list-style:none;padding:0;margin:8px 0;">
        <li><a href="<?php echo esc_url(site_url('/docs')); ?>"><?php echo esc_html__( 'Docs', 'rts' ); ?></a></li>
        <li><a href="<?php echo esc_url(site_url('/guides')); ?>"><?php echo esc_html__( 'Guides', 'rts' ); ?></a></li>
        <li><a href="<?php echo esc_url(site_url('/tutorials')); ?>"><?php echo esc_html__( 'Tutorials', 'rts' ); ?></a></li>
      </ul>
    </div>
    <div>
      <h5><?php echo esc_html__( 'Legal', 'rts' ); ?></h5>
      <ul style="list-style:none;padding:0;margin:8px 0;">
        <li><a href="<?php echo esc_url(site_url('/legal/terms')); ?>"><?php echo esc_html__( 'Terms', 'rts' ); ?></a></li>
        <li><a href="<?php echo esc_url(site_url('/legal/privacy')); ?>"><?php echo esc_html__( 'Privacy', 'rts' ); ?></a></li>
        <li><a href="<?php echo esc_url(site_url('/legal/security')); ?>"><?php echo esc_html__( 'Security', 'rts' ); ?></a></li>
      </ul>
    </div>
  </div>
  <div style="border-top:1px solid var(--border);">
    <div class="container" style="display:flex;align-items:center;justify-content:space-between;padding:16px 0;color:#6b7280;font-size:12px;">
      <span><?php echo esc_html( sprintf( __( '© %1$s %2$s. All rights reserved.', 'rts' ), date_i18n('Y'), get_bloginfo('name') ) ); ?></span>
      <span><?php echo esc_html__( 'Trading involves risk. Past performance is not indicative of future results.', 'rts' ); ?></span>
    </div>
  </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>