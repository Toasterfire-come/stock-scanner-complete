<?php
/**
 * The header for our theme
 *
 * Displays the site header and primary navigation
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between py-4 gap-4">
      <div class="flex items-center gap-3">
        <a href="<?php echo esc_url( home_url('/') ); ?>" class="flex items-center gap-2 font-semibold text-lg hover:opacity-90">
          <?php if ( function_exists('the_custom_logo') && has_custom_logo() ) { the_custom_logo(); } ?>
          <span class="leading-none"><?php bloginfo('name'); ?></span>
        </a>
      </div>

      <nav class="hidden md:block" aria-label="Primary">
        <?php
          if ( has_nav_menu('primary') ) {
            wp_nav_menu([
              'theme_location' => 'primary',
              'container'      => false,
              'menu_class'     => 'flex items-center gap-6 text-sm',
              'fallback_cb'    => false,
              'depth'          => 2,
            ]);
          } else {
            echo '<ul class="flex items-center gap-6 text-sm">'
                . '<li><a class="hover:underline" href="' . esc_url( home_url('/') ) . '">' . esc_html__('Home','retail-trade-scanner') . '</a></li>'
                . '<li><a class="hover:underline" href="' . esc_url( home_url('/scanner') ) . '">' . esc_html__('Scanner','retail-trade-scanner') . '</a></li>'
                . '<li><a class="hover:underline" href="' . esc_url( home_url('/portfolio') ) . '">' . esc_html__('Portfolio','retail-trade-scanner') . '</a></li>'
                . '</ul>';
          }
        ?>
      </nav>

      <div class="flex items-center gap-3">
        <div class="hidden md:block">
          <?php get_search_form(); ?>
        </div>
        <button class="md:hidden inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm" aria-controls="mobile-menu" aria-expanded="false" id="mobile-menu-button">
          <?php esc_html_e('Menu', 'retail-trade-scanner'); ?>
        </button>
      </div>
    </div>
  </div>

  <div id="mobile-menu" class="md:hidden hidden border-t">
    <div class="px-4 py-3">
      <?php
        if ( has_nav_menu('primary') ) {
          wp_nav_menu([
            'theme_location' => 'primary',
            'container'      => false,
            'menu_class'     => 'grid gap-2',
            'fallback_cb'    => false,
            'depth'          => 1,
          ]);
        }
      ?>
      <div class="mt-3">
        <?php get_search_form(); ?>
      </div>
    </div>
  </div>
</header>

<script>
  (function(){
    var btn = document.getElementById('mobile-menu-button');
    var menu = document.getElementById('mobile-menu');
    if (btn && menu) {
      btn.addEventListener('click', function(){
        if (menu.classList.contains('hidden')) { menu.classList.remove('hidden'); }
        else { menu.classList.add('hidden'); }
      });
    }
  })();
</script>