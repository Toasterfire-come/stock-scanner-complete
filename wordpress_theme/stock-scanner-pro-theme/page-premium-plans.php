<?php
/**
 * Template Name: Premium Plans
 */

get_header(); ?>

<div class="plans-page">
    <section class="hero" style="background:linear-gradient(135deg,#2271b1,#135e96);color:#fff;padding:60px 0;">
        <div class="container" style="max-width:1100px;margin:0 auto;padding:0 20px;">
            <h1 style="margin:0 0 12px;">Choose Your Plan</h1>
            <p style="margin:0;opacity:0.9;">Start free. Upgrade anytime. Cancel anytime.</p>
        </div>
    </section>
    <section class="plans" style="padding:40px 0;background:#f7f8fa;">
        <div class="container" style="max-width:1100px;margin:0 auto;padding:0 20px;">
            <?php echo do_shortcode('[stock_scanner_pricing]'); ?>
        </div>
    </section>
    <section class="faq" style="padding:40px 0;">
        <div class="container" style="max-width:1100px;margin:0 auto;padding:0 20px;">
            <div class="card">
                <h2>Frequently Asked Questions</h2>
                <details>
                    <summary>Can I cancel anytime?</summary>
                    <p>Yes. You can cancel your subscription at any time from your account page.</p>
                </details>
                <details>
                    <summary>Do you offer refunds?</summary>
                    <p>We offer a 7-day refund policy if you’re not satisfied. Contact support.</p>
                </details>
                <details>
                    <summary>Do you provide invoices?</summary>
                    <p>Yes. Invoices are emailed and available in your account.</p>
                </details>
            </div>
        </div>
    </section>
</div>

<?php get_footer(); ?>