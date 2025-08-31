<?php
/** Generic layout partial. Expects $rts_title and optional $rts_subtitle, $rts_html */
get_header(); ?>
<section class="section">
  <div class="container">
    <h1><?php echo esc_html($rts_title ?? get_the_title()); ?></h1>
    <?php if (!empty($rts_subtitle)): ?><p style="color:#6b7280;max-width:720px;"><?php echo esc_html($rts_subtitle); ?></p><?php endif; ?>
    <div class="card" style="padding:16px;margin-top:16px;">
      <?php if (!empty($rts_html)) { echo $rts_html; } else { the_content(); } ?>
    </div>
  </div>
</section>
<?php get_footer();