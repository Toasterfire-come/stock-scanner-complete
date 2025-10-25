<?php
/**
 * Template Name: Privacy Policy
 */
get_header(); ?>

<div class="privacy-page">
    <div class="container">
        <div class="page-header">
            <h1>🔒 Privacy Policy</h1>
            <p class="page-description">How we collect, use, and protect your personal information</p>
        </div>

        <div class="card p-6">
            <div class="privacy-content" style="display: grid; gap: var(--space-6); max-width: 800px; margin: 0 auto;">
                <div class="section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">📋 Information We Collect</h2>
                    <p style="color: var(--color-text-muted); line-height: 1.7;">
                        We collect information you provide directly to us, such as when you create an account, use our services, or contact us for support. This may include your name, email address, and usage preferences.
                    </p>
                </div>

                <div class="section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">🛡️ How We Use Your Information</h2>
                    <ul style="color: var(--color-text-muted); line-height: 1.7; padding-left: var(--space-5);">
                        <li>Provide and maintain our stock analysis services</li>
                        <li>Personalize your experience and recommendations</li>
                        <li>Communicate with you about your account and our services</li>
                        <li>Improve and enhance our platform</li>
                        <li>Ensure security and prevent fraud</li>
                    </ul>
                </div>

                <div class="section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">🔐 Data Security</h2>
                    <p style="color: var(--color-text-muted); line-height: 1.7;">
                        We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. All data transmission is encrypted using industry-standard protocols.
                    </p>
                </div>

                <div class="section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">🍪 Cookies and Tracking</h2>
                    <p style="color: var(--color-text-muted); line-height: 1.7;">
                        We use cookies and similar technologies to enhance your browsing experience, analyze usage patterns, and provide personalized content. You can control cookie settings through your browser preferences.
                    </p>
                </div>

                <div class="section">
                    <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">📞 Contact Us</h2>
                    <p style="color: var(--color-text-muted); line-height: 1.7;">
                        If you have any questions about this Privacy Policy, please contact us at <a href="mailto:privacy@stockscanner.com" style="color: var(--color-primary);">privacy@stockscanner.com</a>.
                    </p>
                </div>

                <div class="section" style="background: var(--color-border); padding: var(--space-4); border-radius: var(--radius-md); border-left: 4px solid var(--color-primary);">
                    <p style="margin: 0; font-size: 0.875rem; color: var(--color-text-muted);">
                        <strong style="color: var(--color-text);">Last updated:</strong> January 2025<br>
                        This policy may be updated from time to time. We will notify you of any significant changes.
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<?php get_footer(); ?>