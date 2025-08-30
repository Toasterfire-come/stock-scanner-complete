<?php
/** Header (extended health indicator) */
if (!defined('ABSPATH')) { exit; }
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#primary"><?php esc_html_e('Skip to content','retail-trade-scanner'); ?></a>

<header class="site-header border-b bg-background/80 backdrop-blur" role="banner">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between py-4 gap-4">
      <div class="flex items-center gap-3">
        <a href="<?php echo esc_url( home_url('/') ); ?>" class="flex items-center gap-2 font-semibold text-lg hover:opacity-90">
          <?php if ( function_exists('the_custom_logo') && has_custom_logo() ) { the_custom_logo(); } ?>
          <span class="leading-none"><?php bloginfo('name'); ?></span>
        </a>
        <span id="rts-health-dot" aria-label="API health" style="width:10px;height:10px;border-radius:999px;display:inline-block;border:1px solid var(--border);"></span>
      </div>

      <nav class="hidden md:block" aria-label="Primary" role="navigation">
        <?php
          if ( has_nav_menu('primary') ) {
            wp_nav_menu([
              'theme_location' => 'primary',
              'container'      => false,
              'menu_class'     => 'flex items-center gap-6 text-sm',
              'fallback_cb'    => false,
              'depth'          => 3,
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

  <div id="mobile-menu" class="md:hidden hidden border-t" role="dialog" aria-modal="true" aria-label="Primary Menu">
    <div class="px-4 py-3">
      <?php
        if ( has_nav_menu('primary') ) {
          wp_nav_menu([
            'theme_location' => 'primary',
            'container'      => false,
            'menu_class'     => 'grid gap-2',
            'fallback_cb'    => false,
            'depth'          => 2,
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
    var header = document.querySelector('.site-header');
    var main = document.getElementById('primary');
    var lastFocus = null;
    function getFocusable(container){ return container ? container.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])') : []; }
    function trapFocus(e){ if (!menu || menu.classList.contains('hidden')) return; var f=getFocusable(menu); if(!f.length) return; var first=f[0], last=f[f.length-1]; if(e.key==='Tab'){ if(e.shiftKey && document.activeElement===first){ last.focus(); e.preventDefault(); } else if(!e.shiftKey && document.activeElement===last){ first.focus(); e.preventDefault(); } } if(e.key==='Escape'){ closeMenu(); btn.focus(); } }
    function openMenu(){ menu.classList.remove('hidden'); btn.setAttribute('aria-expanded','true'); header && header.classList.add('is-open'); if (main) { main.setAttribute('aria-hidden','true'); } lastFocus = document.activeElement; var f=getFocusable(menu); if(f.length) f[0].focus(); document.addEventListener('keydown', trapFocus); }
    function closeMenu(){ menu.classList.add('hidden'); btn.setAttribute('aria-expanded','false'); header && header.classList.remove('is-open'); if (main) { main.removeAttribute('aria-hidden'); } document.removeEventListener('keydown', trapFocus); }
    if (btn && menu){ btn.addEventListener('click', function(){ var expanded = btn.getAttribute('aria-expanded')==='true'; if(expanded){ closeMenu(); if(lastFocus) lastFocus.focus(); } else { openMenu(); } }); }
  })();
</script>