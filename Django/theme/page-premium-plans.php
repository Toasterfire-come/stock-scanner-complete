<?php
/**
 * Template Name: Premium Plans
 */

get_header(); ?>

<div class="plans-page">
    <section class="hero">
        <div class="container-narrow">
            <h1>Choose Your Plan</h1>
            <p>Start free. Upgrade anytime. Cancel anytime.</p>
        </div>
    </section>
    <section class="plans-section">
        <div class="container-narrow">
            <?php echo do_shortcode('[stock_scanner_pricing]'); ?>
        </div>
    </section>
    <section class="faq-section">
        <div class="container-narrow">
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