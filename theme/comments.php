<?php
/**
 * Comments template
 */
if (post_password_required()) { return; }
?>
<section id="comments" class="comments-area">
  <?php if (have_comments()) : ?>
    <h2 class="comments-title">
      <?php
      $count = get_comments_number();
      printf( /* translators: 1: number of comments, 2: post title */
        esc_html(_n('%1$s Comment on "%2$s"', '%1$s Comments on "%2$s"', $count, 'retail-trade-scanner')),
        number_format_i18n($count),
        esc_html(get_the_title())
      );
      ?>
    </h2>

    <ol class="comment-list">
      <?php
        wp_list_comments([
          'style'      => 'ol',
          'short_ping' => true,
          'avatar_size'=> 48,
          'reply_text' => esc_html__('Reply', 'retail-trade-scanner')
        ]);
      ?>
    </ol>

    <?php the_comments_pagination(['prev_text' => '&laquo;','next_text' => '&raquo;']); ?>
  <?php endif; ?>

  <?php if (!comments_open() && get_comments_number()) : ?>
    <p class="no-comments"><?php esc_html_e('Comments are closed.', 'retail-trade-scanner'); ?></p>
  <?php endif; ?>

  <?php
  comment_form([
    'title_reply'         => esc_html__('Leave a comment', 'retail-trade-scanner'),
    'title_reply_before'  => '<h3 id="reply-title" class="comment-reply-title">',
    'title_reply_after'   => '</h3>',
    'comment_notes_after' => '',
  ]);
  ?>
</section>