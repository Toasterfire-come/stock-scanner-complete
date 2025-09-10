<?php
/**
 * Comments Template
 * Template for displaying comments
 */

if (post_password_required()) {
    return;
}
?>

<div id="comments" class="comments-area">
    <?php if (have_comments()) : ?>
        <h3 class="comments-title">
            <?php
            $comment_count = get_comments_number();
            if ('1' === $comment_count) {
                printf(
                    esc_html__('One comment on "%s"', 'stock-scanner'),
                    '<span>' . wp_kses_post(get_the_title()) . '</span>'
                );
            } else {
                printf(
                    esc_html(_nx(
                        '%1$s comment on "%2$s"',
                        '%1$s comments on "%2$s"',
                        $comment_count,
                        'comments title',
                        'stock-scanner'
                    )),
                    number_format_i18n($comment_count),
                    '<span>' . wp_kses_post(get_the_title()) . '</span>'
                );
            }
            ?>
        </h3>

        <div class="comment-navigation">
            <?php the_comments_navigation(); ?>
        </div>

        <ol class="comment-list">
            <?php
            wp_list_comments(array(
                'style'       => 'ol',
                'short_ping'  => true,
                'avatar_size' => 64,
                'callback'    => 'stock_scanner_comment_callback',
            ));
            ?>
        </ol>

        <div class="comment-navigation">
            <?php the_comments_navigation(); ?>
        </div>

        <?php if (!comments_open()) : ?>
            <p class="no-comments"><?php esc_html_e('Comments are closed.', 'stock-scanner'); ?></p>
        <?php endif; ?>

    <?php endif; ?>

    <?php comment_form(array(
        'title_reply_before' => '<h3 id="reply-title" class="comment-reply-title">',
        'title_reply_after'  => '</h3>',
        'class_form'         => 'comment-form',
        'class_submit'       => 'submit btn btn-primary',
        'comment_field'      => '<div class="comment-form-comment"><label for="comment">' . esc_html__('Comment', 'stock-scanner') . ' <span class="required">*</span></label><textarea id="comment" name="comment" cols="45" rows="8" maxlength="65525" required="required" placeholder="Share your thoughts on this post..."></textarea></div>',
        'fields'             => array(
            'author' => '<div class="comment-form-author"><label for="author">' . esc_html__('Name', 'stock-scanner') . ' <span class="required">*</span></label> <input id="author" name="author" type="text" value="' . esc_attr($commenter['comment_author']) . '" size="30" maxlength="245" autocomplete="name" required="required" /></div>',
            'email'  => '<div class="comment-form-email"><label for="email">' . esc_html__('Email', 'stock-scanner') . ' <span class="required">*</span></label> <input id="email" name="email" type="email" value="' . esc_attr($commenter['comment_author_email']) . '" size="30" maxlength="100" aria-describedby="email-notes" autocomplete="email" required="required" /></div>',
            'url'    => '<div class="comment-form-url"><label for="url">' . esc_html__('Website', 'stock-scanner') . '</label> <input id="url" name="url" type="url" value="' . esc_attr($commenter['comment_author_url']) . '" size="30" maxlength="200" autocomplete="url" /></div>',
        ),
    )); ?>
</div>

<style>
.comments-area {
    margin-top: 3rem;
    padding: 2rem;
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.comments-title {
    color: var(--text-primary);
    font-size: 1.5rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.comment-navigation {
    margin: 1.5rem 0;
}

.comment-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.comment {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
}

.comment-author {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.comment-author img {
    border-radius: 50%;
    border: 2px solid var(--border-color);
}

.comment-author-name {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1.1rem;
}

.comment-meta {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.comment-meta a {
    color: var(--text-secondary);
    text-decoration: none;
}

.comment-meta a:hover {
    color: var(--primary-color);
}

.comment-content {
    margin: 1rem 0;
    line-height: 1.6;
    color: var(--text-primary);
}

.comment-content p {
    margin-bottom: 1rem;
}

.comment-content p:last-child {
    margin-bottom: 0;
}

.reply {
    margin-top: 1rem;
}

.comment-reply-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 500;
    transition: all var(--transition-normal);
}

.comment-reply-link:hover {
    background: var(--primary-hover);
    color: white;
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}

.children {
    list-style: none;
    padding: 0;
    margin: 1.5rem 0 0 2rem;
}

.children .comment {
    background: var(--bg-primary);
    border-left: 3px solid var(--primary-color);
}

.comment-reply-title {
    color: var(--text-primary);
    font-size: 1.25rem;
    margin: 2rem 0 1.5rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-color);
}

.comment-form {
    display: grid;
    gap: 1.5rem;
}

.comment-form-author,
.comment-form-email,
.comment-form-url {
    display: flex;
    flex-direction: column;
}

.comment-form label {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

.required {
    color: var(--danger-color);
}

.comment-form input[type="text"],
.comment-form input[type="email"],
.comment-form input[type="url"],
.comment-form textarea {
    padding: 1rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.95rem;
    font-family: inherit;
    transition: all var(--transition-normal);
}

.comment-form input:focus,
.comment-form textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
}

.comment-form textarea {
    resize: vertical;
    min-height: 120px;
    line-height: 1.5;
}

.comment-form textarea::placeholder {
    color: var(--text-secondary);
    font-style: italic;
}

.comment-form-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.comment-form-url {
    grid-column: 1 / -1;
}

.form-submit {
    margin-top: 1rem;
}

.submit {
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all var(--transition-normal);
}

.no-comments {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary);
    font-style: italic;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    margin: 2rem 0;
}

@media (max-width: 768px) {
    .comments-area {
        padding: 1.5rem;
    }
    
    .children {
        margin-left: 1rem;
    }
    
    .comment-form-fields {
        grid-template-columns: 1fr;
    }
    
    .comment-author {
        flex-direction: column;
        align-items: flex-start;
        text-align: center;
    }
    
    .comment {
        padding: 1rem;
    }
}
</style>

<?php
/**
 * Custom comment callback function
 */
function stock_scanner_comment_callback($comment, $args, $depth) {
    if ('div' === $args['style']) {
        $tag       = 'div';
        $add_below = 'comment';
    } else {
        $tag       = 'li';
        $add_below = 'div-comment';
    }
    ?>
    <<?php echo $tag; ?> <?php comment_class(empty($args['has_children']) ? '' : 'parent'); ?> id="comment-<?php comment_ID(); ?>">
    <?php if ('div' != $args['style']) : ?>
        <div id="div-comment-<?php comment_ID(); ?>" class="comment-body">
    <?php endif; ?>
    
    <div class="comment-author vcard">
        <?php
        if ($args['avatar_size'] != 0) {
            echo get_avatar($comment, $args['avatar_size']);
        }
        ?>
        <div class="comment-author-info">
            <div class="comment-author-name">
                <?php
                $author = get_comment_author_link();
                if (!empty($author)) {
                    echo $author;
                } else {
                    comment_author();
                }
                ?>
            </div>
            <div class="comment-meta commentmetadata">
                <a href="<?php echo htmlspecialchars(get_comment_link($comment->comment_ID)); ?>">
                    <?php
                    printf(
                        __('%1$s at %2$s', 'stock-scanner'),
                        get_comment_date(),
                        get_comment_time()
                    );
                    ?>
                </a>
                <?php edit_comment_link(__('(Edit)', 'stock-scanner'), '  ', ''); ?>
            </div>
        </div>
    </div>

    <?php if ($comment->comment_approved == '0') : ?>
        <em class="comment-awaiting-moderation"><?php _e('Your comment is awaiting moderation.', 'stock-scanner'); ?></em>
        <br />
    <?php endif; ?>

    <div class="comment-content">
        <?php comment_text(); ?>
    </div>

    <div class="reply">
        <?php
        comment_reply_link(array_merge($args, array(
            'add_below' => $add_below,
            'depth'     => $depth,
            'max_depth' => $args['max_depth']
        )));
        ?>
    </div>
    
    <?php if ('div' != $args['style']) : ?>
        </div>
    <?php endif; ?>
    <?php
}
?>