<?php
/**
 * The template for displaying the footer
 *
 * Contains the closing of the #content div and all content after
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
?>

<footer class="mt-16 border-t bg-background">
  <div class="container mx-auto px-4 py-10 grid gap-8 md:grid-cols-4">
    <div>
      <a href="<?php echo esc_url( home_url('/') ); ?>" class="font-semibold text-lg hover:opacity-90"><?php bloginfo('name'); ?></a>
      <p class="mt-2 text-sm text-muted-foreground max-w-xs"><?php bloginfo('description'); ?></p>
    </div>
    <div>
      <h2 class="text-sm font-semibold mb-3"><?php esc_html_e('Navigate', 'retail-trade-scanner'); ?></h2>
      <?php
        if ( has_nav_menu('footer') ) {
          wp_nav_menu([
            'theme_location' => 'footer',
            'container'      => false,
            'menu_class'     => 'grid gap-2 text-sm',
            'fallback_cb'    => false,
            'depth'          => 1,
          ]);
        } else {
          echo '<ul class="grid gap-2 text-sm">'
            . '<li><a class="hover:underline" href="' . esc_url( home_url('/help') ) . '">' . esc_html__('Help','retail-trade-scanner') . '</a></li>'
            . '<li><a class="hover:underline" href="' . esc_url( home_url('/tutorials') ) . '">' . esc_html__('Tutorials','retail-trade-scanner') . '</a></li>'
            . '<li><a class="hover:underline" href="' . esc_url( home_url('/contact') ) . '">' . esc_html__('Contact','retail-trade-scanner') . '</a></li>'
            . '</ul>';
        }
      ?>
    </div>
    <div>
      <h2 class="text-sm font-semibold mb-3"><?php esc_html_e('Legal', 'retail-trade-scanner'); ?></h2>
      <ul class="grid gap-2 text-sm">
        <li><a class="hover:underline" href="<?php echo esc_url( home_url('/privacy-policy') ); ?>"><?php esc_html_e('Privacy Policy','retail-trade-scanner'); ?></a></li>
        <li><a class="hover:underline" href="<?php echo esc_url( home_url('/terms-of-service') ); ?>"><?php esc_html_e('Terms of Service','retail-trade-scanner'); ?></a></li>
        <li><a class="hover:underline" href="<?php echo esc_url( home_url('/disclaimer') ); ?>"><?php esc_html_e('Disclaimer','retail-trade-scanner'); ?></a></li>
      </ul>
    </div>
    <div>
      <h2 class="text-sm font-semibold mb-3"><?php esc_html_e('Subscribe', 'retail-trade-scanner'); ?></h2>
      <form class="flex gap-2">
        <input class="border rounded px-3 py-2 text-sm w-full" type="email" placeholder="<?php esc_attr_e('Your email','retail-trade-scanner'); ?>" />
        <button class="rounded-md bg-primary text-primary-foreground px-3 py-2 text-sm" type="button"><?php esc_html_e('Join','retail-trade-scanner'); ?></button>
      </form>
    </div>
  </div>
  <div class="border-t">
    <div class="container mx-auto px-4 py-4 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
      <span>&copy; <?php echo esc_html( date('Y') ); ?> <?php bloginfo('name'); ?>. <?php esc_html_e('All rights reserved.', 'retail-trade-scanner'); ?></span>
      <div class="flex items-center gap-4">
        <a class="hover:underline" href="#">Twitter</a>
        <a class="hover:underline" href="#">LinkedIn</a>
        <a class="hover:underline" href="#">GitHub</a>
      </div>
    </div>
  </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>