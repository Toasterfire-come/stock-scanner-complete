<?php
/**
 * Title: Footer 
 * Slug: zatra/footer
 * Categories: footer
 * Block Types: core/template-part/footer
 */
?>

<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|70","bottom":"var:preset|spacing|40","right":"var:preset|spacing|20","left":"var:preset|spacing|20"},"blockGap":"0.29rem"},"elements":{"link":{"color":{"text":"var:preset|color|custom-color-3"},":hover":{"color":{"text":"var:preset|color|custom-color-1"}}}}},"textColor":"custom-color-3","gradient":"custom-color-1","layout":{"type":"constrained"}} -->
<div class="wp-block-group has-custom-color-3-color has-custom-color-1-gradient-background has-text-color has-background has-link-color" style="padding-top:var(--wp--preset--spacing--70);padding-right:var(--wp--preset--spacing--20);padding-bottom:var(--wp--preset--spacing--40);padding-left:var(--wp--preset--spacing--20)"><!-- wp:columns -->
    <div class="wp-block-columns"><!-- wp:column {"style":{"spacing":{"blockGap":"var:preset|spacing|50"}}} -->
        <div class="wp-block-column"><!-- wp:site-title /-->

            <!-- wp:site-tagline /-->

            <!-- wp:social-links {"iconColor":"white","iconColorValue":"#ffffff","openInNewTab":true,"size":"has-normal-icon-size","className":"is-style-logos-only","style":{"spacing":{"blockGap":{"top":"12px","left":"12px"}}},"layout":{"type":"flex","flexWrap":"nowrap"}} -->
            <ul class="wp-block-social-links has-normal-icon-size has-icon-color is-style-logos-only">
                <!-- wp:social-link {"url":"https://www.facebook.com/","service":"facebook"} /-->

                <!-- wp:social-link {"url":"https://x.com/","service":"twitter"} /-->

                <!-- wp:social-link {"url":"https://wordpress.org/","service":"wordpress"} /-->
            </ul>
            <!-- /wp:social-links -->
        </div>
        <!-- /wp:column -->

        <!-- wp:column -->
        <div class="wp-block-column"><!-- wp:heading {"level":4} -->
            <h4 class="wp-block-heading"><?php esc_html_e('Pages','zatra'); ?></h4>
            <!-- /wp:heading -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('About Us','zatra'); ?></a></p>
            <!-- /wp:paragraph -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Contact Us','zatra'); ?></a></p>
            <!-- /wp:paragraph -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Services','zatra'); ?></a></p>
            <!-- /wp:paragraph -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Blog','zatra'); ?></a></p>
            <!-- /wp:paragraph -->
        </div>
        <!-- /wp:column -->

        <!-- wp:column -->
        <div class="wp-block-column"><!-- wp:heading {"level":4} -->
            <h4 class="wp-block-heading"><?php esc_html_e('Links','zatra'); ?></h4>
            <!-- /wp:heading -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Privacy Policy','zatra'); ?></a></p>
            <!-- /wp:paragraph -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Terms and Conditions','zatra'); ?></a></p>
            <!-- /wp:paragraph -->
        </div>
        <!-- /wp:column -->

        <!-- wp:column -->
        <div class="wp-block-column"><!-- wp:heading {"level":4} -->
            <h4 class="wp-block-heading"><?php esc_html_e('Career','zatra'); ?></h4>
            <!-- /wp:heading -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Opening Posts','zatra'); ?></a></p>
            <!-- /wp:paragraph -->

            <!-- wp:paragraph -->
            <p><a href="#"><?php esc_html_e('Partner','zatra'); ?></a></p>
            <!-- /wp:paragraph -->
        </div>
        <!-- /wp:column -->
    </div>
    <!-- /wp:columns -->

    <!-- wp:spacer {"height":"50px"} -->
    <div style="height:50px" aria-hidden="true" class="wp-block-spacer"></div>
    <!-- /wp:spacer -->

    <!-- wp:paragraph {"align":"center","style":{"elements":{"link":{"color":{"text":"var:preset|color|white"}}},"typography":{"fontSize":"16px"}}} -->
    <p class="has-text-align-center has-link-color" style="font-size:16px"><?php esc_html_e('Copyright © 2024 | WordPress Theme by: ','zatra'); ?><a href="https://dezigndigital.com.au/" target="_blank" rel="noreferrer noopener nofollow"><?php esc_html_e('Dezign Digital','zatra'); ?></a></p>
    <!-- /wp:paragraph -->
</div>
<!-- /wp:group -->