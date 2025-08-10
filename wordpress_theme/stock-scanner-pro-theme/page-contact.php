<?php
/**
 * Template Name: Contact Us
 */
get_header(); ?>

<div class="contact-page">
    <div class="container">
        <div class="page-header">
            <h1>📞 Contact Us</h1>
            <p class="page-description">Get in touch with our support team or send us your feedback</p>
        </div>

        <div class="contact-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: var(--space-6);">
            <!-- Contact Form -->
            <div class="card p-6">
                <h2 style="color: var(--color-text); margin-bottom: var(--space-5);">Send us a Message</h2>
                <form class="contact-form" style="display: grid; gap: var(--space-4);">
                    <div class="form-group">
                        <label for="contact-name">Your Name *</label>
                        <input type="text" id="contact-name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="contact-email">Email Address *</label>
                        <input type="email" id="contact-email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="contact-subject">Subject *</label>
                        <select id="contact-subject" name="subject" required>
                            <option value="">Select a topic</option>
                            <option value="support">Technical Support</option>
                            <option value="billing">Billing & Account</option>
                            <option value="feature">Feature Request</option>
                            <option value="bug">Bug Report</option>
                            <option value="general">General Inquiry</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="contact-message">Message *</label>
                        <textarea id="contact-message" name="message" rows="5" required placeholder="Please describe your question or issue in detail..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Send Message</button>
                </form>
            </div>

            <!-- Contact Information -->
            <div class="contact-info" style="display: grid; gap: var(--space-4);">
                <div class="card p-6">
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-4); display: flex; align-items: center; gap: var(--space-2);">
                        ⚡ Quick Support
                    </h3>
                    <div style="display: grid; gap: var(--space-3);">
                        <div class="contact-item" style="display: flex; align-items: center; gap: var(--space-3);">
                            <span style="font-size: 1.5rem;">📧</span>
                            <div>
                                <strong style="color: var(--color-text);">Email Support</strong>
                                <p style="margin: 0; color: var(--color-text-muted);">support@stockscanner.com</p>
                            </div>
                        </div>
                        <div class="contact-item" style="display: flex; align-items: center; gap: var(--space-3);">
                            <span style="font-size: 1.5rem;">⏰</span>
                            <div>
                                <strong style="color: var(--color-text);">Response Time</strong>
                                <p style="margin: 0; color: var(--color-text-muted);">Within 24 hours</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card p-6">
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-4); display: flex; align-items: center; gap: var(--space-2);">
                        📚 Self-Help Resources
                    </h3>
                    <div style="display: grid; gap: var(--space-2);">
                        <a href="/help-center/" class="resource-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius-md); transition: background-color 0.2s; text-decoration: none;">
                            <span>📖</span>
                            <span style="color: var(--color-primary);">Help Center</span>
                        </a>
                        <a href="/faq/" class="resource-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius-md); transition: background-color 0.2s; text-decoration: none;">
                            <span>❓</span>
                            <span style="color: var(--color-primary);">FAQ</span>
                        </a>
                        <a href="/getting-started/" class="resource-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius-md); transition: background-color 0.2s; text-decoration: none;">
                            <span>🚀</span>
                            <span style="color: var(--color-primary);">Getting Started</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.contact-page {
    padding: var(--space-10) 0;
    background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
    min-height: 100vh;
}

.resource-link:hover {
    background: var(--color-border);
}

.contact-form .form-group label {
    display: block;
    margin-bottom: var(--space-2);
    color: var(--color-text);
    font-weight: 600;
}

@media (max-width: 768px) {
    .contact-grid {
        grid-template-columns: 1fr !important;
    }
}
</style>

<?php get_footer(); ?>