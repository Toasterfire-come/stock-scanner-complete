<?php
/**
 * Template Name: Contact
 * 
 * Contact page with support form and company information
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Contact Us', 'retail-trade-scanner'),
    'page_description' => __('Get in touch with our team for support, partnerships, or general inquiries', 'retail-trade-scanner'),
    'page_class' => 'contact-page',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Contact Hero Section -->
<section class="contact-hero">
    <div class="container">
        <div class="contact-hero-content grid grid-cols-12 gap-lg">
            <div class="hero-text col-span-6">
                <h1 class="hero-title animate-fade-up">
                    <?php esc_html_e('We\'re Here to Help', 'retail-trade-scanner'); ?>
                </h1>
                <p class="hero-description animate-fade-up">
                    <?php esc_html_e('Have questions about our platform? Need technical support? Want to discuss partnership opportunities? Our team is ready to assist you.', 'retail-trade-scanner'); ?>
                </p>
                
                <div class="contact-stats animate-fade-up">
                    <div class="stat-item">
                        <div class="stat-value">&lt; 2h</div>
                        <div class="stat-label"><?php esc_html_e('Response Time', 'retail-trade-scanner'); ?></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">24/7</div>
                        <div class="stat-label"><?php esc_html_e('Support Available', 'retail-trade-scanner'); ?></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">99.9%</div>
                        <div class="stat-label"><?php esc_html_e('Customer Satisfaction', 'retail-trade-scanner'); ?></div>
                    </div>
                </div>
            </div>
            
            <div class="hero-visual col-span-6">
                <div class="contact-cards animate-scale-in">
                    <div class="contact-card glass-card">
                        <div class="card-icon">
                            <?php echo rts_get_icon('email', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <h3><?php esc_html_e('Email Support', 'retail-trade-scanner'); ?></h3>
                        <p><?php esc_html_e('Get detailed help via email', 'retail-trade-scanner'); ?></p>
                        <a href="mailto:support@retailtradescanner.com" class="contact-link">
                            support@retailtradescanner.com
                        </a>
                    </div>
                    
                    <div class="contact-card glass-card">
                        <div class="card-icon">
                            <?php echo rts_get_icon('phone', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <h3><?php esc_html_e('Phone Support', 'retail-trade-scanner'); ?></h3>
                        <p><?php esc_html_e('Speak directly with our team', 'retail-trade-scanner'); ?></p>
                        <a href="tel:+1-800-SCANNER" class="contact-link">
                            +1 (800) SCANNER
                        </a>
                    </div>
                    
                    <div class="contact-card glass-card">
                        <div class="card-icon">
                            <?php echo rts_get_icon('chat', ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <h3><?php esc_html_e('Live Chat', 'retail-trade-scanner'); ?></h3>
                        <p><?php esc_html_e('Instant help when you need it', 'retail-trade-scanner'); ?></p>
                        <button class="contact-link chat-trigger">
                            <?php esc_html_e('Start Chat', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Contact Form Section -->
<section class="contact-form-section">
    <div class="container">
        <div class="contact-layout grid grid-cols-12 gap-2xl">
            
            <!-- Contact Form -->
            <div class="contact-form-container col-span-8">
                <div class="card glass-card">
                    <div class="card-header">
                        <h2 class="card-title"><?php esc_html_e('Send us a Message', 'retail-trade-scanner'); ?></h2>
                        <p class="card-description">
                            <?php esc_html_e('Fill out the form below and we\'ll get back to you within 2 hours during business hours.', 'retail-trade-scanner'); ?>
                        </p>
                    </div>
                    
                    <div class="card-body">
                        <form id="contact-form" class="contact-form" method="post">
                            <?php wp_nonce_field('contact_form_nonce', 'contact_nonce'); ?>
                            
                            <!-- Form Type Selector -->
                            <div class="form-group">
                                <label class="form-label"><?php esc_html_e('How can we help?', 'retail-trade-scanner'); ?></label>
                                <div class="inquiry-types">
                                    <label class="inquiry-option">
                                        <input type="radio" name="inquiry_type" value="support" checked>
                                        <div class="option-card">
                                            <?php echo rts_get_icon('help-circle', ['width' => '20', 'height' => '20']); ?>
                                            <span><?php esc_html_e('Technical Support', 'retail-trade-scanner'); ?></span>
                                        </div>
                                    </label>
                                    
                                    <label class="inquiry-option">
                                        <input type="radio" name="inquiry_type" value="sales">
                                        <div class="option-card">
                                            <?php echo rts_get_icon('dollar-sign', ['width' => '20', 'height' => '20']); ?>
                                            <span><?php esc_html_e('Sales Inquiry', 'retail-trade-scanner'); ?></span>
                                        </div>
                                    </label>
                                    
                                    <label class="inquiry-option">
                                        <input type="radio" name="inquiry_type" value="partnership">
                                        <div class="option-card">
                                            <?php echo rts_get_icon('handshake', ['width' => '20', 'height' => '20']); ?>
                                            <span><?php esc_html_e('Partnership', 'retail-trade-scanner'); ?></span>
                                        </div>
                                    </label>
                                    
                                    <label class="inquiry-option">
                                        <input type="radio" name="inquiry_type" value="general">
                                        <div class="option-card">
                                            <?php echo rts_get_icon('message-circle', ['width' => '20', 'height' => '20']); ?>
                                            <span><?php esc_html_e('General Inquiry', 'retail-trade-scanner'); ?></span>
                                        </div>
                                    </label>
                                </div>
                            </div>
                            
                            <!-- Personal Information -->
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label" for="first-name">
                                        <?php esc_html_e('First Name', 'retail-trade-scanner'); ?>
                                        <span class="required">*</span>
                                    </label>
                                    <input type="text" 
                                           id="first-name" 
                                           name="first_name" 
                                           class="form-input" 
                                           required
                                           placeholder="<?php esc_attr_e('John', 'retail-trade-scanner'); ?>">
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label" for="last-name">
                                        <?php esc_html_e('Last Name', 'retail-trade-scanner'); ?>
                                        <span class="required">*</span>
                                    </label>
                                    <input type="text" 
                                           id="last-name" 
                                           name="last_name" 
                                           class="form-input" 
                                           required
                                           placeholder="<?php esc_attr_e('Doe', 'retail-trade-scanner'); ?>">
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label" for="email">
                                        <?php esc_html_e('Email Address', 'retail-trade-scanner'); ?>
                                        <span class="required">*</span>
                                    </label>
                                    <input type="email" 
                                           id="email" 
                                           name="email" 
                                           class="form-input" 
                                           required
                                           placeholder="<?php esc_attr_e('john@example.com', 'retail-trade-scanner'); ?>">
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label" for="phone">
                                        <?php esc_html_e('Phone Number', 'retail-trade-scanner'); ?>
                                    </label>
                                    <input type="tel" 
                                           id="phone" 
                                           name="phone" 
                                           class="form-input"
                                           placeholder="<?php esc_attr_e('+1 (555) 123-4567', 'retail-trade-scanner'); ?>">
                                </div>
                            </div>
                            
                            <!-- Company Information -->
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label" for="company">
                                        <?php esc_html_e('Company', 'retail-trade-scanner'); ?>
                                    </label>
                                    <input type="text" 
                                           id="company" 
                                           name="company" 
                                           class="form-input"
                                           placeholder="<?php esc_attr_e('Your Company Name', 'retail-trade-scanner'); ?>">
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label" for="role">
                                        <?php esc_html_e('Your Role', 'retail-trade-scanner'); ?>
                                    </label>
                                    <select id="role" name="role" class="form-select">
                                        <option value=""><?php esc_html_e('Select your role', 'retail-trade-scanner'); ?></option>
                                        <option value="individual_trader"><?php esc_html_e('Individual Trader', 'retail-trade-scanner'); ?></option>
                                        <option value="portfolio_manager"><?php esc_html_e('Portfolio Manager', 'retail-trade-scanner'); ?></option>
                                        <option value="analyst"><?php esc_html_e('Financial Analyst', 'retail-trade-scanner'); ?></option>
                                        <option value="advisor"><?php esc_html_e('Financial Advisor', 'retail-trade-scanner'); ?></option>
                                        <option value="executive"><?php esc_html_e('Executive', 'retail-trade-scanner'); ?></option>
                                        <option value="developer"><?php esc_html_e('Developer', 'retail-trade-scanner'); ?></option>
                                        <option value="other"><?php esc_html_e('Other', 'retail-trade-scanner'); ?></option>
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Subject and Priority -->
                            <div class="form-group">
                                <label class="form-label" for="subject">
                                    <?php esc_html_e('Subject', 'retail-trade-scanner'); ?>
                                    <span class="required">*</span>
                                </label>
                                <input type="text" 
                                       id="subject" 
                                       name="subject" 
                                       class="form-input" 
                                       required
                                       placeholder="<?php esc_attr_e('Brief description of your inquiry', 'retail-trade-scanner'); ?>">
                            </div>
                            
                            <!-- Priority Level -->
                            <div class="form-group">
                                <label class="form-label"><?php esc_html_e('Priority Level', 'retail-trade-scanner'); ?></label>
                                <div class="priority-options">
                                    <label class="priority-option">
                                        <input type="radio" name="priority" value="low" checked>
                                        <span class="priority-indicator low"></span>
                                        <span><?php esc_html_e('Low', 'retail-trade-scanner'); ?></span>
                                    </label>
                                    
                                    <label class="priority-option">
                                        <input type="radio" name="priority" value="medium">
                                        <span class="priority-indicator medium"></span>
                                        <span><?php esc_html_e('Medium', 'retail-trade-scanner'); ?></span>
                                    </label>
                                    
                                    <label class="priority-option">
                                        <input type="radio" name="priority" value="high">
                                        <span class="priority-indicator high"></span>
                                        <span><?php esc_html_e('High', 'retail-trade-scanner'); ?></span>
                                    </label>
                                    
                                    <label class="priority-option">
                                        <input type="radio" name="priority" value="urgent">
                                        <span class="priority-indicator urgent"></span>
                                        <span><?php esc_html_e('Urgent', 'retail-trade-scanner'); ?></span>
                                    </label>
                                </div>
                            </div>
                            
                            <!-- Message -->
                            <div class="form-group">
                                <label class="form-label" for="message">
                                    <?php esc_html_e('Message', 'retail-trade-scanner'); ?>
                                    <span class="required">*</span>
                                </label>
                                <textarea id="message" 
                                          name="message" 
                                          class="form-textarea" 
                                          rows="6" 
                                          required
                                          placeholder="<?php esc_attr_e('Please provide as much detail as possible about your inquiry...', 'retail-trade-scanner'); ?>"></textarea>
                                <div class="character-count">
                                    <span class="current-count">0</span> / <span class="max-count">1000</span> <?php esc_html_e('characters', 'retail-trade-scanner'); ?>
                                </div>
                            </div>
                            
                            <!-- File Attachment -->
                            <div class="form-group">
                                <label class="form-label" for="attachment">
                                    <?php esc_html_e('Attachment (Optional)', 'retail-trade-scanner'); ?>
                                </label>
                                <div class="file-upload-area">
                                    <input type="file" 
                                           id="attachment" 
                                           name="attachment" 
                                           class="file-input"
                                           accept=".pdf,.doc,.docx,.png,.jpg,.jpeg">
                                    <div class="file-upload-content">
                                        <?php echo rts_get_icon('upload', ['width' => '24', 'height' => '24']); ?>
                                        <p><?php esc_html_e('Click to upload or drag and drop', 'retail-trade-scanner'); ?></p>
                                        <small><?php esc_html_e('PDF, DOC, PNG, JPG up to 5MB', 'retail-trade-scanner'); ?></small>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Newsletter Subscription -->
                            <div class="form-group">
                                <label class="checkbox-option">
                                    <input type="checkbox" name="newsletter" value="1">
                                    <span class="checkmark"></span>
                                    <span><?php esc_html_e('Subscribe to our newsletter for market insights and platform updates', 'retail-trade-scanner'); ?></span>
                                </label>
                            </div>
                            
                            <!-- Terms Agreement -->
                            <div class="form-group">
                                <label class="checkbox-option">
                                    <input type="checkbox" name="terms" value="1" required>
                                    <span class="checkmark"></span>
                                    <span>
                                        <?php esc_html_e('I agree to the', 'retail-trade-scanner'); ?>
                                        <a href="<?php echo esc_url(home_url('/privacy-policy/')); ?>"><?php esc_html_e('Privacy Policy', 'retail-trade-scanner'); ?></a>
                                        <?php esc_html_e('and', 'retail-trade-scanner'); ?>
                                        <a href="<?php echo esc_url(home_url('/terms-of-service/')); ?>"><?php esc_html_e('Terms of Service', 'retail-trade-scanner'); ?></a>
                                    </span>
                                </label>
                            </div>
                            
                            <!-- Form Actions -->
                            <div class="form-actions">
                                <button type="button" class="btn btn-outline clear-form">
                                    <?php echo rts_get_icon('refresh-cw', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Clear Form', 'retail-trade-scanner'); ?>
                                </button>
                                
                                <button type="submit" class="btn btn-primary">
                                    <?php echo rts_get_icon('send', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Send Message', 'retail-trade-scanner'); ?>
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Contact Information Sidebar -->
            <div class="contact-info-sidebar col-span-4">
                <!-- Office Information -->
                <div class="card glass-card">
                    <div class="card-header">
                        <h3 class="card-title"><?php esc_html_e('Office Locations', 'retail-trade-scanner'); ?></h3>
                    </div>
                    
                    <div class="card-body">
                        <div class="office-list">
                            <div class="office-item">
                                <div class="office-header">
                                    <h4><?php esc_html_e('New York (HQ)', 'retail-trade-scanner'); ?></h4>
                                    <span class="office-type"><?php esc_html_e('Headquarters', 'retail-trade-scanner'); ?></span>
                                </div>
                                <div class="office-details">
                                    <div class="detail-item">
                                        <?php echo rts_get_icon('map-pin', ['width' => '16', 'height' => '16']); ?>
                                        <span>123 Wall Street<br>New York, NY 10005</span>
                                    </div>
                                    <div class="detail-item">
                                        <?php echo rts_get_icon('phone', ['width' => '16', 'height' => '16']); ?>
                                        <span>+1 (212) 555-0123</span>
                                    </div>
                                    <div class="detail-item">
                                        <?php echo rts_get_icon('clock', ['width' => '16', 'height' => '16']); ?>
                                        <span><?php esc_html_e('9:00 AM - 6:00 PM EST', 'retail-trade-scanner'); ?></span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="office-item">
                                <div class="office-header">
                                    <h4><?php esc_html_e('London', 'retail-trade-scanner'); ?></h4>
                                    <span class="office-type"><?php esc_html_e('European Office', 'retail-trade-scanner'); ?></span>
                                </div>
                                <div class="office-details">
                                    <div class="detail-item">
                                        <?php echo rts_get_icon('map-pin', ['width' => '16', 'height' => '16']); ?>
                                        <span>1 Canary Wharf<br>London E14 5AB, UK</span>
                                    </div>
                                    <div class="detail-item">
                                        <?php echo rts_get_icon('phone', ['width' => '16', 'height' => '16']); ?>
                                        <span>+44 20 7946 0958</span>
                                    </div>
                                    <div class="detail-item">
                                        <?php echo rts_get_icon('clock', ['width' => '16', 'height' => '16']); ?>
                                        <span><?php esc_html_e('9:00 AM - 5:00 PM GMT', 'retail-trade-scanner'); ?></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- FAQ Section -->
                <div class="card glass-card">
                    <div class="card-header">
                        <h3 class="card-title"><?php esc_html_e('Frequently Asked Questions', 'retail-trade-scanner'); ?></h3>
                    </div>
                    
                    <div class="card-body">
                        <div class="faq-list">
                            <div class="faq-item">
                                <button class="faq-question">
                                    <span><?php esc_html_e('How quickly will I receive a response?', 'retail-trade-scanner'); ?></span>
                                    <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                                </button>
                                <div class="faq-answer hidden">
                                    <p><?php esc_html_e('We typically respond to all inquiries within 2 hours during business hours (9 AM - 6 PM EST). For urgent issues, please use our live chat or phone support.', 'retail-trade-scanner'); ?></p>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <button class="faq-question">
                                    <span><?php esc_html_e('What information should I include in my message?', 'retail-trade-scanner'); ?></span>
                                    <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                                </button>
                                <div class="faq-answer hidden">
                                    <p><?php esc_html_e('Please include your account details, steps to reproduce any issues, error messages, and screenshots if applicable. The more detail you provide, the faster we can help resolve your inquiry.', 'retail-trade-scanner'); ?></p>
                                </div>
                            </div>
                            
                            <div class="faq-item">
                                <button class="faq-question">
                                    <span><?php esc_html_e('Do you offer phone support?', 'retail-trade-scanner'); ?></span>
                                    <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                                </button>
                                <div class="faq-answer hidden">
                                    <p><?php esc_html_e('Yes! Our phone support is available 24/7 for all premium and enterprise customers. Contact us at +1 (800) SCANNER for immediate assistance.', 'retail-trade-scanner'); ?></p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="faq-footer">
                            <a href="<?php echo esc_url(home_url('/faq/')); ?>" class="btn btn-outline btn-sm">
                                <?php esc_html_e('View All FAQs', 'retail-trade-scanner'); ?>
                                <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Support Hours -->
                <div class="card glass-card">
                    <div class="card-header">
                        <h3 class="card-title"><?php esc_html_e('Support Hours', 'retail-trade-scanner'); ?></h3>
                    </div>
                    
                    <div class="card-body">
                        <div class="support-hours">
                            <div class="hours-item">
                                <div class="day"><?php esc_html_e('Monday - Friday', 'retail-trade-scanner'); ?></div>
                                <div class="time"><?php esc_html_e('9:00 AM - 6:00 PM EST', 'retail-trade-scanner'); ?></div>
                            </div>
                            <div class="hours-item">
                                <div class="day"><?php esc_html_e('Saturday', 'retail-trade-scanner'); ?></div>
                                <div class="time"><?php esc_html_e('10:00 AM - 4:00 PM EST', 'retail-trade-scanner'); ?></div>
                            </div>
                            <div class="hours-item">
                                <div class="day"><?php esc_html_e('Sunday', 'retail-trade-scanner'); ?></div>
                                <div class="time"><?php esc_html_e('Email Support Only', 'retail-trade-scanner'); ?></div>
                            </div>
                        </div>
                        
                        <div class="emergency-note">
                            <div class="note-icon">
                                <?php echo rts_get_icon('alert-circle', ['width' => '16', 'height' => '16']); ?>
                            </div>
                            <p><?php esc_html_e('For urgent technical issues outside business hours, please use our 24/7 emergency hotline for premium customers.', 'retail-trade-scanner'); ?></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initContactPage();
});

function initContactPage() {
    const contactForm = document.getElementById('contact-form');
    const messageTextarea = document.getElementById('message');
    const clearFormBtn = document.querySelector('.clear-form');
    const fileInput = document.getElementById('attachment');
    const fileUploadArea = document.querySelector('.file-upload-area');
    
    // Form submission
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitContactForm();
        });
    }
    
    // Character counter for message
    if (messageTextarea) {
        messageTextarea.addEventListener('input', function() {
            updateCharacterCount();
        });
        updateCharacterCount(); // Initialize
    }
    
    // Clear form
    if (clearFormBtn) {
        clearFormBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear the form? All entered data will be lost.')) {
                contactForm.reset();
                updateCharacterCount();
                RTS.showInfo('Form cleared');
            }
        });
    }
    
    // File upload handling
    if (fileUploadArea && fileInput) {
        // Click to upload
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Drag and drop
        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileSelection(this.files[0]);
            }
        });
    }
    
    // FAQ accordion
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', function() {
            const faqItem = this.parentElement;
            const answer = faqItem.querySelector('.faq-answer');
            const icon = this.querySelector('svg');
            
            // Close other FAQ items
            document.querySelectorAll('.faq-item').forEach(item => {
                if (item !== faqItem) {
                    item.querySelector('.faq-answer').classList.add('hidden');
                    item.querySelector('svg').style.transform = 'rotate(0deg)';
                }
            });
            
            // Toggle current item
            answer.classList.toggle('hidden');
            icon.style.transform = answer.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    });
    
    // Chat trigger
    const chatTrigger = document.querySelector('.chat-trigger');
    if (chatTrigger) {
        chatTrigger.addEventListener('click', function() {
            // In a real implementation, this would open a chat widget
            RTS.showInfo('Live chat would open here');
        });
    }
    
    function submitContactForm() {
        const submitBtn = contactForm.querySelector('[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <div class="loading-spinner"></div>
            ${RTS.translations?.submitting || 'Sending...'}
        `;
        
        // Get form data
        const formData = new FormData(contactForm);
        
        // Validate required fields
        const requiredFields = ['first_name', 'last_name', 'email', 'subject', 'message'];
        let isValid = true;
        
        requiredFields.forEach(field => {
            const input = contactForm.querySelector(`[name="${field}"]`);
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });
        
        if (!isValid) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            RTS.showError('Please fill in all required fields');
            return;
        }
        
        // Simulate form submission
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            
            // Show success message
            RTS.showSuccess('Message sent successfully! We\'ll get back to you within 2 hours.');
            
            // Reset form
            contactForm.reset();
            updateCharacterCount();
            
            // Remove any file selection display
            resetFileUpload();
        }, 3000);
    }
    
    function updateCharacterCount() {
        const currentLength = messageTextarea.value.length;
        const maxLength = 1000;
        
        const currentCountElement = document.querySelector('.current-count');
        const charCountElement = document.querySelector('.character-count');
        
        if (currentCountElement) {
            currentCountElement.textContent = currentLength;
            
            // Change color based on character count
            if (currentLength > maxLength * 0.9) {
                charCountElement.classList.add('warning');
            } else {
                charCountElement.classList.remove('warning');
            }
            
            if (currentLength > maxLength) {
                charCountElement.classList.add('error');
                messageTextarea.setCustomValidity('Message is too long');
            } else {
                charCountElement.classList.remove('error');
                messageTextarea.setCustomValidity('');
            }
        }
    }
    
    function handleFileSelection(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png', 'image/jpeg'];
        
        // Validate file size
        if (file.size > maxSize) {
            RTS.showError('File size must be less than 5MB');
            return;
        }
        
        // Validate file type
        if (!allowedTypes.includes(file.type)) {
            RTS.showError('Please select a PDF, DOC, PNG, or JPG file');
            return;
        }
        
        // Update UI to show selected file
        const uploadContent = fileUploadArea.querySelector('.file-upload-content');
        uploadContent.innerHTML = `
            <div class="file-selected">
                ${RTS.components.getIcon('file', 24)}
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
                <button type="button" class="remove-file" onclick="resetFileUpload()">
                    ${RTS.components.getIcon('x', 16)}
                </button>
            </div>
        `;
        
        RTS.showSuccess('File selected successfully');
    }
    
    function resetFileUpload() {
        fileInput.value = '';
        const uploadContent = fileUploadArea.querySelector('.file-upload-content');
        uploadContent.innerHTML = `
            ${RTS.components.getIcon('upload', 24)}
            <p>Click to upload or drag and drop</p>
            <small>PDF, DOC, PNG, JPG up to 5MB</small>
        `;
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Make resetFileUpload globally accessible
    window.resetFileUpload = resetFileUpload;
}
</script>

<style>
/* Contact Page Styles */
.contact-page {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    min-height: 100vh;
}

.contact-hero {
    padding: var(--spacing-4xl) 0;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(217, 70, 239, 0.05) 100%);
}

.hero-title {
    font-size: clamp(2.5rem, 2.2rem + 1.5vw, 3.5rem);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xl);
}

.hero-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    line-height: 1.6;
    margin-bottom: var(--spacing-2xl);
}

.contact-stats {
    display: flex;
    gap: var(--spacing-xl);
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--primary-600);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.contact-cards {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.contact-card {
    padding: var(--spacing-xl);
    text-align: center;
    transition: all var(--transition-normal) var(--easing-standard);
}

.contact-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.card-icon {
    width: 60px;
    height: 60px;
    border-radius: var(--radius-xl);
    background: var(--primary-100);
    color: var(--primary-600);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--spacing-lg);
}

.contact-card h3 {
    font-size: var(--text-lg);
    font-weight: 700;
    margin: 0 0 var(--spacing-sm);
}

.contact-card p {
    color: var(--gray-600);
    margin: 0 0 var(--spacing-md);
}

.contact-link {
    color: var(--primary-600);
    font-weight: 600;
    text-decoration: none;
    border: none;
    background: none;
    cursor: pointer;
    transition: color var(--transition-fast) var(--easing-standard);
}

.contact-link:hover {
    color: var(--primary-700);
    text-decoration: underline;
}

.contact-form-section {
    padding: var(--spacing-4xl) 0;
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
}

.inquiry-types {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
}

.inquiry-option {
    cursor: pointer;
}

.inquiry-option input {
    display: none;
}

.option-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-lg);
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast) var(--easing-standard);
    text-align: center;
}

.inquiry-option input:checked + .option-card {
    border-color: var(--primary-500);
    background: var(--primary-50);
    color: var(--primary-700);
}

.option-card:hover {
    border-color: var(--primary-300);
    background: var(--primary-25);
}

.priority-options {
    display: flex;
    gap: var(--spacing-lg);
}

.priority-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
}

.priority-option input {
    display: none;
}

.priority-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 2px solid transparent;
    transition: all var(--transition-fast) var(--easing-standard);
}

.priority-indicator.low { background: var(--success); }
.priority-indicator.medium { background: var(--warning); }
.priority-indicator.high { background: var(--danger); }
.priority-indicator.urgent { background: var(--error); }

.priority-option input:checked + .priority-indicator {
    border-color: var(--gray-900);
    box-shadow: 0 0 0 2px var(--surface);
}

.character-count {
    text-align: right;
    font-size: var(--text-xs);
    color: var(--gray-500);
    margin-top: var(--spacing-xs);
}

.character-count.warning {
    color: var(--warning);
}

.character-count.error {
    color: var(--danger);
}

.file-upload-area {
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    text-align: center;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.file-upload-area:hover,
.file-upload-area.drag-over {
    border-color: var(--primary-500);
    background: var(--primary-50);
}

.file-upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--gray-600);
}

.file-selected {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--success-light);
    border-radius: var(--radius-lg);
    color: var(--success-dark);
}

.file-info {
    flex: 1;
    text-align: left;
}

.file-name {
    font-weight: 600;
}

.file-size {
    font-size: var(--text-xs);
    opacity: 0.8;
}

.remove-file {
    padding: var(--spacing-xs);
    background: transparent;
    border: none;
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: background-color var(--transition-fast) var(--easing-standard);
}

.remove-file:hover {
    background: rgba(0, 0, 0, 0.1);
}

.checkbox-option {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
    cursor: pointer;
    line-height: 1.5;
}

.checkbox-option input {
    display: none;
}

.checkmark {
    width: 20px;
    height: 20px;
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-sm);
    position: relative;
    transition: all var(--transition-fast) var(--easing-standard);
    flex-shrink: 0;
    margin-top: 2px;
}

.checkbox-option input:checked + .checkmark {
    background: var(--primary-500);
    border-color: var(--primary-500);
}

.checkbox-option input:checked + .checkmark::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 6px;
    width: 4px;
    height: 8px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
}

.form-actions {
    display: flex;
    gap: var(--spacing-lg);
    justify-content: flex-end;
}

.required {
    color: var(--danger);
}

.form-input.error,
.form-textarea.error {
    border-color: var(--danger);
    background: var(--danger-light);
}

/* Sidebar Styles */
.contact-info-sidebar {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.office-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.office-item {
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
}

.office-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.office-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-md);
}

.office-header h4 {
    margin: 0;
    font-weight: 700;
}

.office-type {
    font-size: var(--text-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    font-weight: 600;
}

.office-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.detail-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.faq-list {
    display: flex;
    flex-direction: column;
}

.faq-item {
    border-bottom: 1px solid var(--gray-200);
}

.faq-item:last-child {
    border-bottom: none;
}

.faq-question {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) 0;
    background: none;
    border: none;
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-900);
    cursor: pointer;
    text-align: left;
}

.faq-question svg {
    transition: transform var(--transition-fast) var(--easing-standard);
    color: var(--gray-500);
}

.faq-answer {
    padding-bottom: var(--spacing-md);
}

.faq-answer p {
    margin: 0;
    color: var(--gray-600);
    line-height: 1.6;
}

.faq-footer {
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--gray-200);
    margin-top: var(--spacing-lg);
}

.support-hours {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.hours-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) 0;
}

.day {
    font-weight: 600;
    color: var(--gray-900);
}

.time {
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.emergency-note {
    margin-top: var(--spacing-lg);
    padding: var(--spacing-md);
    background: var(--warning-light);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
}

.note-icon {
    color: var(--warning);
    flex-shrink: 0;
    margin-top: 2px;
}

.emergency-note p {
    margin: 0;
    font-size: var(--text-sm);
    color: var(--warning-dark);
}

/* Loading spinner */
.loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-right: var(--spacing-xs);
}

/* Responsive Design */
@media (max-width: 1024px) {
    .contact-layout {
        grid-template-columns: 1fr;
    }
    
    .contact-info-sidebar {
        order: -1;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .contact-stats {
        justify-content: center;
        flex-wrap: wrap;
    }
}

@media (max-width: 640px) {
    .hero-title {
        font-size: 2rem;
    }
    
    .contact-hero {
        padding: var(--spacing-2xl) 0;
    }
    
    .contact-form-section {
        padding: var(--spacing-2xl) 0;
    }
    
    .inquiry-types {
        grid-template-columns: 1fr;
    }
    
    .priority-options {
        flex-wrap: wrap;
        gap: var(--spacing-md);
    }
    
    .form-actions {
        flex-direction: column;
    }
    
    .contact-stats {
        gap: var(--spacing-lg);
    }
}

/* Dark Mode */
[data-theme="dark"] .contact-page {
    background: var(--gray-900);
}

[data-theme="dark"] .hero-title {
    color: var(--gray-100);
}

[data-theme="dark"] .hero-description {
    color: var(--gray-300);
}

[data-theme="dark"] .card-icon {
    background: var(--gray-800);
    color: var(--primary-400);
}

[data-theme="dark"] .option-card {
    border-color: var(--gray-700);
    background: var(--gray-800);
    color: var(--gray-200);
}

[data-theme="dark"] .inquiry-option input:checked + .option-card {
    border-color: var(--primary-400);
    background: var(--gray-700);
    color: var(--primary-300);
}

[data-theme="dark"] .office-item {
    border-color: var(--gray-700);
}

[data-theme="dark"] .faq-item {
    border-color: var(--gray-700);
}

[data-theme="dark"] .faq-question {
    color: var(--gray-200);
}

[data-theme="dark"] .emergency-note {
    background: var(--gray-800);
    border: 1px solid var(--warning);
}
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>