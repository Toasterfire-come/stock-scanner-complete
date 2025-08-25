<?php if (!defined('ABSPATH')) { exit; } if (post_password_required()) { return; } ?>
<section id="comments" class="section">
  <div class="container content">
    <?php if (have_comments()) : ?>
      <h3 style="color:var(--navy); margin:0 0 8px;">
        <?php printf(_n('One comment', '%1$s comments', get_comments_number(), 'finmarkets'), number_format_i18n(get_comments_number())); ?>
      </h3>
      <ol style="list-style:none; padding:0;">
        <?php wp_list_comments(['style' => 'ol', 'short_ping' => true]); ?>
      </ol>
      <div><?php paginate_comments_links(); ?></div>
    <?php endif; ?>

    <?php if (comments_open()) : ?>
      <div class="card" style="padding:16px; margin-top:12px;">
        <?php comment_form(['class_submit' => 'btn btn-primary']); ?>
      </div>
    <?php endif; ?>
  </div>
</section>