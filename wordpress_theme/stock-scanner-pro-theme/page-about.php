<?php
/**
 * Template Name: About Stock Scanner
 */
get_header(); ?>

<div class="about-page">
    <div class="container">
        <div class="page-header">
            <h1>About Stock Scanner</h1>
            <p class="page-description">Learn about our mission, values, and commitment to providing professional stock analysis tools</p>
        </div>

        <div class="card p-6 mb-6">
            <div style="display: grid; gap: var(--space-6);">
                <div class="mission-section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">
                        Our Mission
                    </h2>
                    <p style="font-size: 1.125rem; line-height: 1.7; color: var(--color-text-muted);">
                        Stock Scanner is a professional platform for stock analysis, designed to help investors make informed decisions with efficient tools and clean design. We believe that powerful market analysis should be accessible to everyone, not just institutional investors.
                    </p>
                </div>

                <div class="vision-section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">
                        Our Vision
                    </h2>
                    <p style="font-size: 1.125rem; line-height: 1.7; color: var(--color-text-muted);">
                        To democratize professional-grade stock analysis tools and make powerful market research accessible to retail traders and investors worldwide.
                    </p>
                </div>

                <div class="values-section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4); display: flex; align-items: center; gap: var(--space-2);">
                        💎 What We Value
                    </h2>
                    <div class="values-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-5); margin-top: var(--space-4);">
                        <div class="value-item" style="text-align: center; padding: var(--space-4);">
                            <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Clarity over Complexity</h3>
                            <p style="color: var(--color-text-muted);">Simple, intuitive interfaces that don't compromise on power or functionality.</p>
                        </div>
                        <div class="value-item" style="text-align: center; padding: var(--space-4);">
                            <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Performance & Reliability</h3>
                            <p style="color: var(--color-text-muted);">Fast, accurate data and tools you can depend on for critical investment decisions.</p>
                        </div>
                        <div class="value-item" style="text-align: center; padding: var(--space-4);">
                            <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Privacy & Security</h3>
                            <p style="color: var(--color-text-muted);">Your data and investment strategies remain private and secure.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card p-6">
            <h2 style="color: var(--color-text); margin-bottom: var(--space-4); text-align: center;">
                Join Our Community
            </h2>
            <div style="text-align: center;">
                <p style="color: var(--color-text-muted); margin-bottom: var(--space-5);">
                    Ready to take your trading to the next level? Start with our free plan and upgrade as you grow.
                </p>
                <div style="display: flex; gap: var(--space-3); justify-content: center; flex-wrap: wrap;">
                    <a href="/signup/" class="btn btn-primary">Get Started Free</a>
                    <a href="/premium-plans/" class="btn btn-outline">View Premium Plans</a>
                </div>
            </div>
        </div>
    </div>
</div>

<?php get_footer(); ?>