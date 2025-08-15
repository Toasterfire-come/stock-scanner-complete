<?php
/**
 * Template Name: Contact
 * 
 * The template for displaying the contact page
 */

get_header(); 
?>

<div class="contact-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-envelope"></i>
                Contact Us
            </h1>
            <p class="page-subtitle">Get in touch with our team - we're here to help you succeed</p>
        </div>
    </div>

    <div class="contact-content">
        <div class="container">
            <!-- Contact Options -->
            <div class="contact-options">
                <div class="contact-card">
                    <div class="card-icon">
                        <i class="fas fa-headset"></i>
                    </div>
                    <h3>Customer Support</h3>
                    <p>Get help with your account, technical issues, or general questions.</p>
                    <div class="contact-info">
                        <div class="info-item">
                            <i class="fas fa-envelope"></i>
                            <span>support@stockscannerpro.com</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-clock"></i>
                            <span>24/7 Support Available</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-reply"></i>
                            <span>Average response: 2 hours</span>
                        </div>
                    </div>
                </div>

                <div class="contact-card">
                    <div class="card-icon">
                        <i class="fas fa-building"></i>
                    </div>
                    <h3>Business Inquiries</h3>
                    <p>Enterprise solutions, partnerships, and bulk licensing opportunities.</p>
                    <div class="contact-info">
                        <div class="info-item">
                            <i class="fas fa-envelope"></i>
                            <span>business@stockscannerpro.com</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-phone"></i>
                            <span>+1 (555) 123-4567</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-calendar"></i>
                            <span>Schedule a demo call</span>
                        </div>
                    </div>
                </div>

                <div class="contact-card">
                    <div class="card-icon">
                        <i class="fas fa-bug"></i>
                    </div>
                    <h3>Technical Issues</h3>
                    <p>Report bugs, request features, or get help with API integration.</p>
                    <div class="contact-info">
                        <div class="info-item">
                            <i class="fas fa-envelope"></i>
                            <span>tech@stockscannerpro.com</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-code"></i>
                            <span>Developer documentation</span>
                        </div>
                        <div class="info-item">
                            <i class="fas fa-tools"></i>
                            <span>API support included</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Contact Form Section -->
            <div class="contact-form-section">
                <div class="form-container">
                    <div class="form-header">
                        <h2>Send us a Message</h2>
                        <p>Fill out the form below and we'll get back to you as soon as possible.</p>
                    </div>

                    <form id="contactForm" class="contact-form">
                        <?php wp_nonce_field('contact_form', 'contact_nonce'); ?>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="firstName">First Name *</label>
                                <input type="text" id="firstName" name="first_name" required class="form-input">
                                <div class="field-error"></div>
                            </div>
                            
                            <div class="form-group">
                                <label for="lastName">Last Name *</label>
                                <input type="text" id="lastName" name="last_name" required class="form-input">
                                <div class="field-error"></div>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="email">Email Address *</label>
                                <input type="email" id="email" name="email" required class="form-input">
                                <div class="field-error"></div>
                            </div>
                            
                            <div class="form-group">
                                <label for="phone">Phone Number</label>
                                <input type="tel" id="phone" name="phone" class="form-input">
                                <div class="field-error"></div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="subject">Subject *</label>
                            <select id="subject" name="subject" required class="form-select">
                                <option value="">Select a subject...</option>
                                <option value="general">General Inquiry</option>
                                <option value="support">Technical Support</option>
                                <option value="billing">Billing Question</option>
                                <option value="feature">Feature Request</option>
                                <option value="partnership">Partnership Opportunity</option>
                                <option value="other">Other</option>
                            </select>
                            <div class="field-error"></div>
                        </div>

                        <div class="form-group">
                            <label for="company">Company (Optional)</label>
                            <input type="text" id="company" name="company" class="form-input">
                        </div>

                        <div class="form-group">
                            <label for="message">Message *</label>
                            <textarea id="message" name="message" rows="6" required class="form-textarea" placeholder="Please describe your inquiry in detail..."></textarea>
                            <div class="field-error"></div>
                            <div class="character-count">
                                <span id="charCount">0</span>/1000 characters
                            </div>
                        </div>

                        <div class="form-group checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="newsletter" name="newsletter">
                                <span class="checkmark"></span>
                                Subscribe to our newsletter for market insights and product updates
                            </label>
                        </div>

                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary" id="submitBtn">
                                <i class="fas fa-paper-plane"></i>
                                Send Message
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Contact Info Sidebar -->
                <div class="contact-sidebar">
                    <div class="sidebar-card">
                        <h3>Office Hours</h3>
                        <div class="hours-list">
                            <div class="hours-item">
                                <span class="day">Monday - Friday</span>
                                <span class="time">9:00 AM - 6:00 PM EST</span>
                            </div>
                            <div class="hours-item">
                                <span class="day">Saturday</span>
                                <span class="time">10:00 AM - 4:00 PM EST</span>
                            </div>
                            <div class="hours-item">
                                <span class="day">Sunday</span>
                                <span class="time">Closed</span>
                            </div>
                        </div>
                        <div class="note">
                            <i class="fas fa-info-circle"></i>
                            Emergency support available 24/7 for Enterprise customers
                        </div>
                    </div>

                    <div class="sidebar-card">
                        <h3>Quick Links</h3>
                        <div class="quick-links">
                            <a href="/faq/" class="quick-link">
                                <i class="fas fa-question-circle"></i>
                                FAQ & Help Center
                            </a>
                            <a href="/help-center/" class="quick-link">
                                <i class="fas fa-book"></i>
                                Documentation
                            </a>
                            <a href="/getting-started/" class="quick-link">
                                <i class="fas fa-rocket"></i>
                                Getting Started Guide
                            </a>
                            <a href="/premium-plans/" class="quick-link">
                                <i class="fas fa-star"></i>
                                View Plans & Pricing
                            </a>
                        </div>
                    </div>

                    <div class="sidebar-card">
                        <h3>Follow Us</h3>
                        <div class="social-links">
                            <a href="#" class="social-link twitter">
                                <i class="fab fa-twitter"></i>
                                Twitter
                            </a>
                            <a href="#" class="social-link linkedin">
                                <i class="fab fa-linkedin"></i>
                                LinkedIn
                            </a>
                            <a href="#" class="social-link youtube">
                                <i class="fab fa-youtube"></i>
                                YouTube
                            </a>
                            <a href="#" class="social-link discord">
                                <i class="fab fa-discord"></i>
                                Discord
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.contact-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 1rem 0 0 0;
}

.contact-content {
    padding: 3rem 0;
}

.contact-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.contact-card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.contact-card:hover {
    transform: translateY(-5px);
}

.card-icon {
    background: #3685fb;
    color: white;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 1.5rem;
}

.contact-card h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 1rem 0;
}

.contact-card p {
    color: #666;
    line-height: 1.6;
    margin: 0 0 1.5rem 0;
}

.contact-info {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.info-item {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: #555;
    font-size: 0.95rem;
}

.info-item i {
    color: #3685fb;
    width: 16px;
}

.contact-form-section {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 3rem;
    align-items: start;
}

.form-container {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-header {
    margin-bottom: 2rem;
}

.form-header h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.5rem 0;
}

.form-header p {
    color: #666;
    line-height: 1.6;
    margin: 0;
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-weight: 600;
    color: #333;
    font-size: 0.95rem;
}

.form-input,
.form-select,
.form-textarea {
    padding: 0.75rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
    transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.form-textarea {
    resize: vertical;
    min-height: 120px;
    font-family: inherit;
}

.character-count {
    font-size: 0.8rem;
    color: #888;
    text-align: right;
}

.checkbox-group {
    flex-direction: row;
    align-items: center;
    gap: 0.75rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: 0.95rem;
    color: #666;
    line-height: 1.4;
}

.checkbox-label input[type="checkbox"] {
    display: none;
}

.checkmark {
    width: 20px;
    height: 20px;
    border: 2px solid #e1e5e9;
    border-radius: 4px;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
    background: #3685fb;
    border-color: #3685fb;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.field-error {
    color: #ef4444;
    font-size: 0.8rem;
    display: none;
}

.field-error.show {
    display: block;
}

.form-actions {
    margin-top: 1rem;
}

.btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
}

.btn-primary {
    background: #3685fb;
    color: white;
    width: 100%;
    justify-content: center;
}

.btn-primary:hover {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(54, 133, 251, 0.3);
}

.btn-primary:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
}

.contact-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.sidebar-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.sidebar-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 1rem 0;
}

.hours-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.hours-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f0f0f0;
}

.hours-item:last-child {
    border-bottom: none;
}

.day {
    font-weight: 600;
    color: #333;
}

.time {
    color: #666;
}

.note {
    background: #f0f9ff;
    border: 1px solid #e0f2fe;
    border-radius: 6px;
    padding: 0.75rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #0369a1;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}

.quick-links {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.quick-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 6px;
    color: #666;
    text-decoration: none;
    transition: all 0.2s;
    border: 1px solid transparent;
}

.quick-link:hover {
    background: #f8f9fa;
    color: #3685fb;
    border-color: #e1e5e9;
}

.quick-link i {
    color: #3685fb;
}

.social-links {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.social-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 6px;
    color: #666;
    text-decoration: none;
    transition: all 0.2s;
    border: 1px solid transparent;
}

.social-link:hover {
    transform: translateX(5px);
}

.social-link.twitter:hover {
    background: #e6f3ff;
    color: #1da1f2;
    border-color: #1da1f2;
}

.social-link.linkedin:hover {
    background: #e6f0ff;
    color: #0077b5;
    border-color: #0077b5;
}

.social-link.youtube:hover {
    background: #ffe6e6;
    color: #ff0000;
    border-color: #ff0000;
}

.social-link.discord:hover {
    background: #f0e6ff;
    color: #7289da;
    border-color: #7289da;
}

@media (max-width: 1024px) {
    .contact-form-section {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .contact-options {
        grid-template-columns: 1fr;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .form-container,
    .sidebar-card {
        padding: 1.5rem;
    }
    
    .checkbox-label {
        font-size: 0.9rem;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeContactForm();
});

function initializeContactForm() {
    const form = document.getElementById('contactForm');
    const messageTextarea = document.getElementById('message');
    const charCount = document.getElementById('charCount');
    
    // Character counter
    messageTextarea.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count > 1000) {
            charCount.style.color = '#ef4444';
        } else {
            charCount.style.color = '#888';
        }
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            submitForm();
        }
    });
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

function validateForm() {
    const form = document.getElementById('contactForm');
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Check message length
    const message = document.getElementById('message');
    if (message.value.length > 1000) {
        showFieldError(message, 'Message must be less than 1000 characters');
        isValid = false;
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        isValid = false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Phone validation (if provided)
    if (field.name === 'phone' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
            showFieldError(field, 'Please enter a valid phone number');
            isValid = false;
        }
    }
    
    if (isValid) {
        clearFieldError(field);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    const errorElement = field.parentElement.querySelector('.field-error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
    field.style.borderColor = '#ef4444';
}

function clearFieldError(field) {
    const errorElement = field.parentElement.querySelector('.field-error');
    if (errorElement) {
        errorElement.classList.remove('show');
    }
    field.style.borderColor = '#e1e5e9';
}

function submitForm() {
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    submitBtn.disabled = true;
    
    // Simulate form submission
    setTimeout(() => {
        // Reset button
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Message Sent!';
        submitBtn.style.background = '#10b981';
        
        // Show success message
        showNotification('Your message has been sent successfully! We\'ll get back to you soon.', 'success');
        
        // Reset form after a delay
        setTimeout(() => {
            document.getElementById('contactForm').reset();
            document.getElementById('charCount').textContent = '0';
            submitBtn.innerHTML = originalText;
            submitBtn.style.background = '#3685fb';
            submitBtn.disabled = false;
        }, 3000);
        
    }, 2000);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3685fb',
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
        zIndex: '1001',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        maxWidth: '400px'
    });
    
    const closeBtn = notification.querySelector('button');
    Object.assign(closeBtn.style, {
        background: 'none',
        border: 'none',
        color: 'white',
        fontSize: '1.25rem',
        cursor: 'pointer',
        padding: '0'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}
</script>

<?php get_footer(); ?>