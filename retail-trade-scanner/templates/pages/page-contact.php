<?php
/**
 * Template Name: Contact
 * 
 * Contact form and support information
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Contact Us', 'retail-trade-scanner'),
    'page_description' => __('Get in touch with our team for support, questions, or feedback', 'retail-trade-scanner'),
    'page_class' => 'contact-page',
    'breadcrumbs' => false
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="contact-content grid grid-cols-12 gap-lg">
    
    <!-- Contact Form -->
    <div class="contact-form-section col-span-8">
        <div class="card">
            <div class="card-header">
                <h2 class="card-title"><?php esc_html_e('Send us a message', 'retail-trade-scanner'); ?></h2>
                <p class="card-description"><?php esc_html_e('We\'ll get back to you within 24 hours', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="card-body">
                <form class="contact-form" id="contact-form">
                    <div class="form-grid grid-2">
                        <div class="form-field">
                            <label class="form-label" for="first-name">
                                <?php esc_html_e('First Name', 'retail-trade-scanner'); ?>
                            </label>
                            <input type="text" class="form-input" id="first-name" name="first_name" required>
                        </div>
                        
                        <div class="form-field">
                            <label class="form-label" for="last-name">
                                <?php esc_html_e('Last Name', 'retail-trade-scanner'); ?>
                            </label>
                            <input type="text" class="form-input" id="last-name" name="last_name" required>
                        </div>
                    </div>
                    
                    <div class="form-field">
                        <label class="form-label" for="email">
                            <?php esc_html_e('Email Address', 'retail-trade-scanner'); ?>
                        </label>
                        <input type="email" class="form-input" id="email" name="email" required>
                    </div>
                    
                    <div class="form-field">
                        <label class="form-label" for="subject">
                            <?php esc_html_e('Subject', 'retail-trade-scanner'); ?>
                        </label>
                        <select class="form-select" id="subject" name="subject" required>
                            <option value=""><?php esc_html_e('Select a topic', 'retail-trade-scanner'); ?></option>
                            <option value="general"><?php esc_html_e('General Inquiry', 'retail-trade-scanner'); ?></option>
                            <option value="support"><?php esc_html_e('Technical Support', 'retail-trade-scanner'); ?></option>
                            <option value="billing"><?php esc_html_e('Billing Question', 'retail-trade-scanner'); ?></option>
                            <option value="feature"><?php esc_html_e('Feature Request', 'retail-trade-scanner'); ?></option>
                            <option value="bug"><?php esc_html_e('Bug Report', 'retail-trade-scanner'); ?></option>
                            <option value="partnership"><?php esc_html_e('Partnership', 'retail-trade-scanner'); ?></option>
                        </select>
                    </div>
                    
                    <div class="form-field">
                        <label class="form-label" for="message">
                            <?php esc_html_e('Message', 'retail-trade-scanner'); ?>
                        </label>
                        <textarea class="form-input" id="message" name="message" rows="6" 
                                  placeholder="<?php esc_attr_e('Please describe your inquiry in detail...', 'retail-trade-scanner'); ?>" required></textarea>
                    </div>
                    
                    <div class="form-field">
                        <label class="checkbox-option">
                            <input type="checkbox" name="newsletter" value="1">
                            <span class="option-label"><?php esc_html_e('Subscribe to our newsletter for market updates', 'retail-trade-scanner'); ?></span>
                        </label>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">
                            <?php echo rts_get_icon('send', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Send Message', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Contact Information -->
    <div class="contact-info-section col-span-4">
        
        <!-- Contact Details -->
        <div class="contact-info-card card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Get in Touch', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="contact-methods">
                    
                    <div class="contact-method">
                        <div class="method-icon">
                            <?php echo rts_get_icon('email', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <div class="method-info">
                            <h4><?php esc_html_e('Email Us', 'retail-trade-scanner'); ?></h4>
                            <p>support@retailtradescanner.com</p>
                            <small><?php esc_html_e('We respond within 24 hours', 'retail-trade-scanner'); ?></small>
                        </div>
                    </div>
                    
                    <div class="contact-method">
                        <div class="method-icon">
                            <?php echo rts_get_icon('phone', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <div class="method-info">
                            <h4><?php esc_html_e('Call Us', 'retail-trade-scanner'); ?></h4>
                            <p>+1 (555) 123-4567</p>
                            <small><?php esc_html_e('Mon-Fri, 9AM-6PM EST', 'retail-trade-scanner'); ?></small>
                        </div>
                    </div>
                    
                    <div class="contact-method">
                        <div class="method-icon">
                            <?php echo rts_get_icon('chat', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <div class="method-info">
                            <h4><?php esc_html_e('Live Chat', 'retail-trade-scanner'); ?></h4>
                            <p><?php esc_html_e('Chat with our team', 'retail-trade-scanner'); ?></p>
                            <button class="btn btn-outline btn-sm start-chat">
                                <?php esc_html_e('Start Chat', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                    
                    <div class="contact-method">
                        <div class="method-icon">
                            <?php echo rts_get_icon('map', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <div class="method-info">
                            <h4><?php esc_html_e('Visit Us', 'retail-trade-scanner'); ?></h4>
                            <p>123 Financial District<br>New York, NY 10004</p>
                            <small><?php esc_html_e('By appointment only', 'retail-trade-scanner'); ?></small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Response Times -->
        <div class="response-times-card card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Response Times', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="response-list">
                    <div class="response-item">
                        <div class="response-type"><?php esc_html_e('General Inquiries', 'retail-trade-scanner'); ?></div>
                        <div class="response-time"><?php esc_html_e('24 hours', 'retail-trade-scanner'); ?></div>
                    </div>
                    
                    <div class="response-item">
                        <div class="response-type"><?php esc_html_e('Technical Support', 'retail-trade-scanner'); ?></div>
                        <div class="response-time"><?php esc_html_e('4 hours', 'retail-trade-scanner'); ?></div>
                    </div>
                    
                    <div class="response-item">
                        <div class="response-type"><?php esc_html_e('Billing Issues', 'retail-trade-scanner'); ?></div>
                        <div class="response-time"><?php esc_html_e('2 hours', 'retail-trade-scanner'); ?></div>
                    </div>
                    
                    <div class="response-item">
                        <div class="response-type"><?php esc_html_e('Critical Issues', 'retail-trade-scanner'); ?></div>
                        <div class="response-time"><?php esc_html_e('1 hour', 'retail-trade-scanner'); ?></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Social Links -->
        <div class="social-links-card card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Follow Us', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="social-links">
                    <a href="#" class="social-link twitter" title="Follow us on Twitter">
                        <?php echo rts_get_icon('twitter', ['width' => '20', 'height' => '20']); ?>
                        <span>Twitter</span>
                    </a>
                    
                    <a href="#" class="social-link linkedin" title="Connect on LinkedIn">
                        <?php echo rts_get_icon('linkedin', ['width' => '20', 'height' => '20']); ?>
                        <span>LinkedIn</span>
                    </a>
                    
                    <a href="#" class="social-link github" title="View our GitHub">
                        <?php echo rts_get_icon('github', ['width' => '20', 'height' => '20']); ?>
                        <span>GitHub</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initContactPage();
});

function initContactPage() {
    const contactForm = document.getElementById('contact-form');
    const startChatBtn = document.querySelector('.start-chat');
    
    // Contact form submission
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleContactFormSubmission();
        });
    }
    
    // Start chat
    if (startChatBtn) {
        startChatBtn.addEventListener('click', function() {
            startLiveChat();
        });
    }
    
    function handleContactFormSubmission() {
        const formData = new FormData(contactForm);
        const contactData = Object.fromEntries(formData.entries());
        
        console.log('Submitting contact form:', contactData);
        
        // Validate required fields
        const requiredFields = ['first_name', 'last_name', 'email', 'subject', 'message'];
        const missingFields = requiredFields.filter(field => !contactData[field]);
        
        if (missingFields.length > 0) {
            RTS.showError('Please fill in all required fields');
            return;
        }
        
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="loading-spinner"></div> Sending...';
        
        // Simulate form submission
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg> Send Message';
            
            RTS.showSuccess('Message sent successfully! We\'ll get back to you within 24 hours.');
            contactForm.reset();
        }, 2000);
    }
    
    function startLiveChat() {
        console.log('Starting live chat');
        RTS.showInfo('Live chat would open here');
        
        // In real implementation, this would integrate with a chat service
        // like Intercom, Zendesk Chat, or custom solution
    }
}
</script>

<style>
/* Contact Page Styles */
.contact-content {
    margin-bottom: var(--spacing-2xl);
}

.form-grid {
    display: grid;
    gap: var(--spacing-lg);
}

.form-grid.grid-2 {
    grid-template-columns: repeat(2, 1fr);
}

.checkbox-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
}

.contact-methods {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.contact-method {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
}

.method-icon {
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    background: rgba(var(--primary-500), 0.1);
    color: var(--primary-600);
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
}

.method-info h4 {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xs);
}

.method-info p {
    color: var(--gray-700);
    margin: 0 0 var(--spacing-xs);
    font-weight: 500;
}

.method-info small {
    color: var(--gray-500);
    font-size: var(--text-xs);
}

.response-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.response-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.response-item:last-child {
    border-bottom: none;
}

.response-type {
    font-size: var(--text-sm);
    color: var(--gray-700);
}

.response-time {
    font-weight: 600;
    color: var(--primary-600);
    font-size: var(--text-sm);
}

.social-links {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.social-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--gray-700);
    text-decoration: none;
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast) var(--easing-standard);
}

.social-link:hover {
    background: rgba(255, 255, 255, 0.1);
    text-decoration: none;
    transform: translateX(4px);
}

.social-link.twitter:hover {
    color: #1da1f2;
}

.social-link.linkedin:hover {
    color: #0077b5;
}

.social-link.github:hover {
    color: #333;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .contact-content {
        grid-template-columns: 1fr;
    }
    
    .contact-info-section {
        order: -1;
    }
}

@media (max-width: 640px) {
    .form-grid.grid-2 {
        grid-template-columns: 1fr;
    }
    
    .contact-method {
        flex-direction: column;
        text-align: center;
    }
    
    .method-icon {
        align-self: center;
    }
    
    .response-item {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-xs);
    }
}

/* Dark Mode */
[data-theme="dark"] .method-info h4 {
    color: var(--gray-100);
}

[data-theme="dark"] .method-info p,
[data-theme="dark"] .response-type {
    color: var(--gray-300);
}

[data-theme="dark"] .method-info small {
    color: var(--gray-500);
}

[data-theme="dark"] .social-link {
    color: var(--gray-300);
}

[data-theme="dark"] .social-link.github:hover {
    color: var(--gray-100);
}
</style>

<?php get_footer(); ?>