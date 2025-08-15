<?php
/**
 * Title: Home Banner Section
 * Slug: zatra/banner-section
 * Categories: cover, text, button
 */
?>

<!-- wp:cover {"url":"<?php echo esc_url( get_template_directory_uri() ) . '/assets/images/wave-bg.jpg'; ?>","id":1162,"dimRatio":50,"overlayColor":"black","isUserOverlayColor":true,"focalPoint":{"x":0.5,"y":0},"metadata":{"name":"Home Banner"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|80","bottom":"var:preset|spacing|80"},"blockGap":"var:preset|spacing|70"}},"layout":{"type":"constrained"}} -->
<div class="wp-block-cover" style="padding-top:var(--wp--preset--spacing--80);padding-bottom:var(--wp--preset--spacing--80)"><span aria-hidden="true" class="wp-block-cover__background has-black-background-color has-background-dim"></span><img class="wp-block-cover__image-background wp-image-1162" alt="" src="<?php echo esc_url( get_template_directory_uri() ) . '/assets/images/wave-bg.jpg'; ?>" style="object-position:50% 0%" data-object-fit="cover" data-object-position="50% 0%"/><div class="wp-block-cover__inner-container"><!-- wp:heading {"level":1,"style":{"typography":{"fontSize":"100px"}}} -->
<h1 class="wp-block-heading" style="font-size:100px"><?php esc_html_e('','zatra'); ?><?php esc_html_e('Working','zatra'); ?><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-custom-color-1-color"><?php esc_html_e(',','zatra'); ?></mark> <br><?php esc_html_e('Together','zatra'); ?><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-custom-color-1-color"><?php esc_html_e('.','zatra'); ?></mark>
        </h1>
<!-- /wp:heading -->

<!-- wp:group {"layout":{"type":"flex","flexWrap":"wrap","justifyContent":"right"}} -->
<div class="wp-block-group"><!-- wp:group {"style":{"border":{"right":{"color":"var:preset|color|custom-color-1","width":"5px"},"top":[],"bottom":[],"left":[]}},"layout":{"type":"constrained"}} -->
<div class="wp-block-group" style="border-right-color:var(--wp--preset--color--custom-color-1);border-right-width:5px"><!-- wp:heading {"textAlign":"right","style":{"typography":{"fontStyle":"normal","fontWeight":"300","fontSize":"22px"},"spacing":{"padding":{"right":"var:preset|spacing|50"}}}} -->
<h2 class="wp-block-heading has-text-align-right" style="padding-right:var(--wp--preset--spacing--50);font-size:22px;font-style:normal;font-weight:300"><?php esc_html_e('Teamwork at the','zatra'); ?><br> <?php esc_html_e('heart of our process','zatra'); ?></h2>
<!-- /wp:heading --></div>
<!-- /wp:group -->

<!-- wp:buttons {"style":{"layout":{"selfStretch":"fit","flexSize":null}}} -->
<div class="wp-block-buttons"><!-- wp:button {"className":"is-style-outline","style":{"spacing":{"padding":{"left":"var:preset|spacing|70","right":"var:preset|spacing|70","top":"var:preset|spacing|50","bottom":"var:preset|spacing|50"}}},"fontFamily":"poppins"} -->
<div class="wp-block-button is-style-outline has-poppins-font-family"><a class="wp-block-button__link wp-element-button" href="#" style="padding-top:var(--wp--preset--spacing--50);padding-right:var(--wp--preset--spacing--70);padding-bottom:var(--wp--preset--spacing--50);padding-left:var(--wp--preset--spacing--70)"><?php esc_html_e('Contact Us','zatra'); ?></a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group --></div></div>
<!-- /wp:cover -->