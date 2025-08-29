<?php
/**
 * Template Name: About Us
 * 
 * About page showcasing company information and team
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('About Retail Trade Scanner', 'retail-trade-scanner'),
    'page_description' => __('Learn about our mission to democratize financial markets through advanced trading technology and data-driven insights.', 'retail-trade-scanner'),
    'page_class' => 'about-page'
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- About Hero -->
<section class="about-hero">
    <div class="container">
        <div class="hero-content grid grid-cols-12 gap-2xl">
            <div class="hero-text col-span-6">
                <div class="hero-badge animate-fade-up">
                    <?php echo rts_get_icon('star', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Trusted by 50,000+ traders worldwide', 'retail-trade-scanner'); ?>
                </div>
                
                <h1 class="hero-title animate-fade-up">
                    <?php esc_html_e('Empowering Traders with', 'retail-trade-scanner'); ?>
                    <span class="title-highlight"><?php esc_html_e('Intelligent Market Insights', 'retail-trade-scanner'); ?></span>
                </h1>
                
                <p class="hero-description animate-fade-up">
                    <?php esc_html_e('Since 2019, we\'ve been building cutting-edge tools that help individual and institutional traders make smarter investment decisions. Our platform combines real-time market data, advanced analytics, and intuitive design to level the playing field in financial markets.', 'retail-trade-scanner'); ?>
                </p>
                
                <div class="hero-stats animate-fade-up">
                    <div class="stat-item">
                        <div class="stat-value">50K+</div>
                        <div class="stat-label"><?php esc_html_e('Active Users', 'retail-trade-scanner'); ?></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">$2.5B+</div>
                        <div class="stat-label"><?php esc_html_e('Assets Tracked', 'retail-trade-scanner'); ?></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">99.9%</div>
                        <div class="stat-label"><?php esc_html_e('Uptime', 'retail-trade-scanner'); ?></div>
                    </div>
                </div>
            </div>
            
            <div class="hero-visual col-span-6">
                <div class="about-image-container animate-scale-in">
                    <div class="about-image-main glass-card">
                        <?php echo rts_get_icon('trending-up', ['width' => '120', 'height' => '120', 'class' => 'about-main-icon']); ?>
                        <div class="floating-elements">
                            <div class="floating-element" data-animate="float-1">
                                <div class="element-content">
                                    <?php echo rts_get_icon('bar-chart', ['width' => '24', 'height' => '24']); ?>
                                    <span><?php esc_html_e('Analytics', 'retail-trade-scanner'); ?></span>
                                </div>
                            </div>
                            <div class="floating-element" data-animate="float-2">
                                <div class="element-content">
                                    <?php echo rts_get_icon('bell', ['width' => '24', 'height' => '24']); ?>
                                    <span><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></span>
                                </div>
                            </div>
                            <div class="floating-element" data-animate="float-3">
                                <div class="element-content">
                                    <?php echo rts_get_icon('shield-check', ['width' => '24', 'height' => '24']); ?>
                                    <span><?php esc_html_e('Security', 'retail-trade-scanner'); ?></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Mission & Vision -->
<section class="mission-vision">
    <div class="container">
        <div class="mission-vision-grid grid grid-cols-12 gap-2xl">
            <div class="mission-card col-span-6 glass-card">
                <div class="card-icon">
                    <?php echo rts_get_icon('target', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h2 class="card-title"><?php esc_html_e('Our Mission', 'retail-trade-scanner'); ?></h2>
                <p class="card-description">
                    <?php esc_html_e('To democratize access to professional-grade trading tools and market intelligence, empowering every trader to make informed investment decisions regardless of their experience level or portfolio size.', 'retail-trade-scanner'); ?>
                </p>
                <ul class="mission-points">
                    <li><?php esc_html_e('Provide real-time, accurate market data', 'retail-trade-scanner'); ?></li>
                    <li><?php esc_html_e('Simplify complex financial analysis', 'retail-trade-scanner'); ?></li>
                    <li><?php esc_html_e('Enable smarter trading decisions', 'retail-trade-scanner'); ?></li>
                    <li><?php esc_html_e('Foster financial literacy and education', 'retail-trade-scanner'); ?></li>
                </ul>
            </div>
            
            <div class="vision-card col-span-6 glass-card">
                <div class="card-icon">
                    <?php echo rts_get_icon('eye', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h2 class="card-title"><?php esc_html_e('Our Vision', 'retail-trade-scanner'); ?></h2>
                <p class="card-description">
                    <?php esc_html_e('To become the world\'s most trusted and innovative trading platform, where technology meets intuition to create extraordinary investment outcomes for traders across all markets and asset classes.', 'retail-trade-scanner'); ?>
                </p>
                <div class="vision-features">
                    <div class="feature-item">
                        <?php echo rts_get_icon('globe', ['width' => '24', 'height' => '24']); ?>
                        <span><?php esc_html_e('Global Market Coverage', 'retail-trade-scanner'); ?></span>
                    </div>
                    <div class="feature-item">
                        <?php echo rts_get_icon('zap', ['width' => '24', 'height' => '24']); ?>
                        <span><?php esc_html_e('AI-Powered Insights', 'retail-trade-scanner'); ?></span>
                    </div>
                    <div class="feature-item">
                        <?php echo rts_get_icon('users', ['width' => '24', 'height' => '24']); ?>
                        <span><?php esc_html_e('Community-Driven', 'retail-trade-scanner'); ?></span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Company Values -->
<section class="company-values">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title"><?php esc_html_e('Our Core Values', 'retail-trade-scanner'); ?></h2>
            <p class="section-description">
                <?php esc_html_e('The principles that guide every decision we make and every feature we build.', 'retail-trade-scanner'); ?>
            </p>
        </div>
        
        <div class="values-grid grid grid-4 gap-xl">
            <div class="value-card animate-scale-in">
                <div class="value-icon">
                    <?php echo rts_get_icon('shield', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="value-title"><?php esc_html_e('Trust & Transparency', 'retail-trade-scanner'); ?></h3>
                <p class="value-description">
                    <?php esc_html_e('We believe in complete transparency in our data sources, methodologies, and pricing. Your trust is our most valuable asset.', 'retail-trade-scanner'); ?>
                </p>
            </div>
            
            <div class="value-card animate-scale-in">
                <div class="value-icon">
                    <?php echo rts_get_icon('cpu', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="value-title"><?php esc_html_e('Innovation', 'retail-trade-scanner'); ?></h3>
                <p class="value-description">
                    <?php esc_html_e('We continuously push the boundaries of what\'s possible in financial technology, always staying ahead of market needs.', 'retail-trade-scanner'); ?>
                </p>
            </div>
            
            <div class="value-card animate-scale-in">
                <div class="value-icon">
                    <?php echo rts_get_icon('heart', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="value-title"><?php esc_html_e('User-Centric', 'retail-trade-scanner'); ?></h3>
                <p class="value-description">
                    <?php esc_html_e('Every feature we build starts with understanding our users\' needs and challenges in the trading world.', 'retail-trade-scanner'); ?>
                </p>
            </div>
            
            <div class="value-card animate-scale-in">
                <div class="value-icon">
                    <?php echo rts_get_icon('award', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="value-title"><?php esc_html_e('Excellence', 'retail-trade-scanner'); ?></h3>
                <p class="value-description">
                    <?php esc_html_e('We strive for excellence in everything we do, from our code quality to customer support and beyond.', 'retail-trade-scanner'); ?>
                </p>
            </div>
        </div>
    </div>
</section>

<!-- Team Section -->
<section class="team-section">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title"><?php esc_html_e('Meet Our Team', 'retail-trade-scanner'); ?></h2>
            <p class="section-description">
                <?php esc_html_e('The passionate professionals behind Retail Trade Scanner, bringing together decades of experience in finance, technology, and design.', 'retail-trade-scanner'); ?>
            </p>
        </div>
        
        <div class="team-grid grid grid-3 gap-xl">
            <div class="team-member-card glass-card animate-scale-in">
                <div class="member-photo">
                    <div class="photo-placeholder">
                        <?php echo rts_get_icon('user', ['width' => '60', 'height' => '60']); ?>
                    </div>
                </div>
                <div class="member-info">
                    <h3 class="member-name"><?php esc_html_e('Sarah Chen', 'retail-trade-scanner'); ?></h3>
                    <p class="member-role"><?php esc_html_e('CEO & Co-Founder', 'retail-trade-scanner'); ?></p>
                    <p class="member-bio">
                        <?php esc_html_e('Former Goldman Sachs quantitative analyst with 15+ years in algorithmic trading. Stanford MBA, passionate about democratizing financial markets.', 'retail-trade-scanner'); ?>
                    </p>
                    <div class="member-social">
                        <a href="#" class="social-link" aria-label="LinkedIn">
                            <?php echo rts_get_icon('linkedin', ['width' => '20', 'height' => '20']); ?>
                        </a>
                        <a href="#" class="social-link" aria-label="Twitter">
                            <?php echo rts_get_icon('twitter', ['width' => '20', 'height' => '20']); ?>
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="team-member-card glass-card animate-scale-in">
                <div class="member-photo">
                    <div class="photo-placeholder">
                        <?php echo rts_get_icon('user', ['width' => '60', 'height' => '60']); ?>
                    </div>
                </div>
                <div class="member-info">
                    <h3 class="member-name"><?php esc_html_e('Michael Rodriguez', 'retail-trade-scanner'); ?></h3>
                    <p class="member-role"><?php esc_html_e('CTO & Co-Founder', 'retail-trade-scanner'); ?></p>
                    <p class="member-bio">
                        <?php esc_html_e('Ex-Google senior engineer specialized in real-time data systems and machine learning. MIT Computer Science, 12 years in fintech.', 'retail-trade-scanner'); ?>
                    </p>
                    <div class="member-social">
                        <a href="#" class="social-link" aria-label="LinkedIn">
                            <?php echo rts_get_icon('linkedin', ['width' => '20', 'height' => '20']); ?>
                        </a>
                        <a href="#" class="social-link" aria-label="GitHub">
                            <?php echo rts_get_icon('github', ['width' => '20', 'height' => '20']); ?>
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="team-member-card glass-card animate-scale-in">
                <div class="member-photo">
                    <div class="photo-placeholder">
                        <?php echo rts_get_icon('user', ['width' => '60', 'height' => '60']); ?>
                    </div>
                </div>
                <div class="member-info">
                    <h3 class="member-name"><?php esc_html_e('Emma Thompson', 'retail-trade-scanner'); ?></h3>
                    <p class="member-role"><?php esc_html_e('Head of Product Design', 'retail-trade-scanner'); ?></p>
                    <p class="member-bio">
                        <?php esc_html_e('Award-winning UX designer from Apple, specializing in financial interfaces. 10 years creating intuitive experiences for complex data.', 'retail-trade-scanner'); ?>
                    </p>
                    <div class="member-social">
                        <a href="#" class="social-link" aria-label="LinkedIn">
                            <?php echo rts_get_icon('linkedin', ['width' => '20', 'height' => '20']); ?>
                        </a>
                        <a href="#" class="social-link" aria-label="Portfolio">
                            <?php echo rts_get_icon('external-link', ['width' => '20', 'height' => '20']); ?>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="team-cta">
            <div class="cta-content">
                <h3><?php esc_html_e('Join Our Team', 'retail-trade-scanner'); ?></h3>
                <p><?php esc_html_e('We\'re always looking for talented individuals who share our passion for innovation in financial technology.', 'retail-trade-scanner'); ?></p>
                <a href="<?php echo esc_url(home_url('/careers/')); ?>" class="btn btn-primary">
                    <?php esc_html_e('View Open Positions', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Company Timeline -->
<section class="company-timeline">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title"><?php esc_html_e('Our Journey', 'retail-trade-scanner'); ?></h2>
            <p class="section-description">
                <?php esc_html_e('From a small startup to a trusted platform serving thousands of traders worldwide.', 'retail-trade-scanner'); ?>
            </p>
        </div>
        
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-marker">
                    <div class="marker-content">2019</div>
                </div>
                <div class="timeline-content glass-card">
                    <h3 class="timeline-title"><?php esc_html_e('Company Founded', 'retail-trade-scanner'); ?></h3>
                    <p class="timeline-description">
                        <?php esc_html_e('Sarah and Michael started Retail Trade Scanner with a vision to democratize access to professional trading tools.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-marker">
                    <div class="marker-content">2020</div>
                </div>
                <div class="timeline-content glass-card">
                    <h3 class="timeline-title"><?php esc_html_e('First Product Launch', 'retail-trade-scanner'); ?></h3>
                    <p class="timeline-description">
                        <?php esc_html_e('Launched our MVP with basic stock screening and portfolio tracking features. Gained our first 1,000 users.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-marker">
                    <div class="marker-content">2021</div>
                </div>
                <div class="timeline-content glass-card">
                    <h3 class="timeline-title"><?php esc_html_e('Series A Funding', 'retail-trade-scanner'); ?></h3>
                    <p class="timeline-description">
                        <?php esc_html_e('Raised $5M in Series A funding to expand our team and enhance our data infrastructure. Reached 10,000 active users.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-marker">
                    <div class="marker-content">2022</div>
                </div>
                <div class="timeline-content glass-card">
                    <h3 class="timeline-title"><?php esc_html_e('Advanced Analytics Platform', 'retail-trade-scanner'); ?></h3>
                    <p class="timeline-description">
                        <?php esc_html_e('Introduced AI-powered market analysis and sentiment tracking. Launched mobile apps for iOS and Android.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-marker">
                    <div class="marker-content">2023</div>
                </div>
                <div class="timeline-content glass-card">
                    <h3 class="timeline-title"><?php esc_html_e('Enterprise Solutions', 'retail-trade-scanner'); ?></h3>
                    <p class="timeline-description">
                        <?php esc_html_e('Launched enterprise-grade solutions for institutional clients. Partnerships with major financial institutions established.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-marker current">
                    <div class="marker-content">2024</div>
                </div>
                <div class="timeline-content glass-card current">
                    <h3 class="timeline-title"><?php esc_html_e('Global Expansion', 'retail-trade-scanner'); ?></h3>
                    <p class="timeline-description">
                        <?php esc_html_e('Expanding to international markets with localized features. 50,000+ users and growing rapidly.', 'retail-trade-scanner'); ?>
                    </p>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Awards & Recognition -->
<section class="awards-section">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title"><?php esc_html_e('Awards & Recognition', 'retail-trade-scanner'); ?></h2>
        </div>
        
        <div class="awards-grid grid grid-4 gap-xl">
            <div class="award-card glass-card">
                <div class="award-icon">
                    <?php echo rts_get_icon('award', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="award-title"><?php esc_html_e('FinTech Innovation Award', 'retail-trade-scanner'); ?></h3>
                <p class="award-year">2023</p>
                <p class="award-description"><?php esc_html_e('Best Trading Platform Innovation', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="award-card glass-card">
                <div class="award-icon">
                    <?php echo rts_get_icon('star', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="award-title"><?php esc_html_e('TechCrunch Disruptor', 'retail-trade-scanner'); ?></h3>
                <p class="award-year">2022</p>
                <p class="award-description"><?php esc_html_e('Top 100 Startups to Watch', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="award-card glass-card">
                <div class="award-icon">
                    <?php echo rts_get_icon('shield', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="award-title"><?php esc_html_e('Security Excellence', 'retail-trade-scanner'); ?></h3>
                <p class="award-year">2023</p>
                <p class="award-description"><?php esc_html_e('SOC 2 Type II Certified', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="award-card glass-card">
                <div class="award-icon">
                    <?php echo rts_get_icon('users', ['width' => '40', 'height' => '40']); ?>
                </div>
                <h3 class="award-title"><?php esc_html_e('Customer Choice Award', 'retail-trade-scanner'); ?></h3>
                <p class="award-year">2024</p>
                <p class="award-description"><?php esc_html_e('Highest User Satisfaction Rating', 'retail-trade-scanner'); ?></p>
            </div>
        </div>
    </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initAboutPage();
});

function initAboutPage() {
    // Animated counters for stats
    animateCounters();
    
    // Floating elements animation
    initFloatingElements();
    
    // Timeline intersection observer
    initTimelineAnimation();
    
    // Scroll animations
    initScrollAnimations();
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = counter.textContent;
                
                // Extract numeric value
                let numericValue = 0;
                let suffix = '';
                
                if (target.includes('K+')) {
                    numericValue = parseFloat(target.replace('K+', '')) * 1000;
                    suffix = 'K+';
                } else if (target.includes('B+')) {
                    numericValue = parseFloat(target.replace('B+', '')) * 1000000000;
                    suffix = 'B+';
                } else if (target.includes('%')) {
                    numericValue = parseFloat(target.replace('%', ''));
                    suffix = '%';
                } else {
                    numericValue = parseFloat(target.replace(/[^0-9.]/g, ''));
                }
                
                animateCounter(counter, numericValue, suffix);
                observer.unobserve(counter);
            }
        });
    });
    
    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element, target, suffix) {
    let current = 0;
    const increment = target / 60; // 60 frames
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        let displayValue;
        if (suffix === 'K+') {
            displayValue = (current / 1000).toFixed(1) + 'K+';
        } else if (suffix === 'B+') {
            displayValue = '$' + (current / 1000000000).toFixed(1) + 'B+';
        } else if (suffix === '%') {
            displayValue = current.toFixed(1) + '%';
        } else {
            displayValue = Math.floor(current).toLocaleString();
        }
        
        element.textContent = displayValue;
    }, 16);
}

function initFloatingElements() {
    const elements = document.querySelectorAll('.floating-element');
    
    elements.forEach((element, index) => {
        const delay = index * 0.5;
        element.style.animationDelay = `${delay}s`;
        element.classList.add('floating');
    });
}

function initTimelineAnimation() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    });
    
    timelineItems.forEach(item => observer.observe(item));
}

function initScrollAnimations() {
    const animateElements = document.querySelectorAll('.animate-scale-in, .animate-fade-up');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    animateElements.forEach(el => observer.observe(el));
}
</script>

<style>
/* About Page Styles */
.about-page {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.about-hero {
    padding: var(--spacing-4xl) 0;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(217, 70, 239, 0.05) 100%);
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-lg);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: 600;
    margin-bottom: var(--spacing-xl);
}

.hero-title {
    font-size: clamp(2.5rem, 2.2rem + 1.5vw, 3.5rem);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xl);
    line-height: 1.2;
}

.title-highlight {
    color: var(--primary-600);
    background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    line-height: 1.6;
    margin-bottom: var(--spacing-2xl);
}

.hero-stats {
    display: flex;
    gap: var(--spacing-2xl);
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: var(--text-2xl);
    font-weight: 900;
    color: var(--primary-600);
    margin-bottom: var(--spacing-xs);
    font-family: var(--font-display);
}

.stat-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
    font-weight: 600;
}

.about-image-container {
    position: relative;
    display: flex;
    justify-content: center;
}

.about-image-main {
    width: 300px;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.about-main-icon {
    color: var(--primary-500);
    opacity: 0.8;
}

.floating-elements {
    position: absolute;
    inset: 0;
}

.floating-element {
    position: absolute;
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
}

.floating-element:nth-child(1) {
    top: 20%;
    right: -20px;
}

.floating-element:nth-child(2) {
    bottom: 30%;
    left: -30px;
}

.floating-element:nth-child(3) {
    top: 60%;
    right: -10px;
}

.floating-element.floating {
    animation: float 3s ease-in-out infinite;
}

.floating-element[data-animate="float-2"].floating {
    animation: float 3s ease-in-out infinite 1s;
}

.floating-element[data-animate="float-3"].floating {
    animation: float 3s ease-in-out infinite 2s;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.element-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
    white-space: nowrap;
}

/* Mission & Vision */
.mission-vision {
    padding: var(--spacing-4xl) 0;
}

.mission-card,
.vision-card {
    padding: var(--spacing-2xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
    height: 100%;
}

.card-icon {
    color: var(--primary-600);
}

.card-title {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0;
}

.card-description {
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0;
}

.mission-points {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.mission-points li {
    position: relative;
    padding-left: var(--spacing-lg);
    color: var(--gray-700);
}

.mission-points li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--success);
    font-weight: 700;
}

.vision-features {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.feature-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--gray-700);
    font-weight: 600;
}

/* Company Values */
.company-values {
    padding: var(--spacing-4xl) 0;
    background: var(--gray-50);
}

.section-header {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.section-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-lg);
}

.section-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    max-width: 600px;
    margin: 0 auto;
}

.values-grid {
    max-width: 1000px;
    margin: 0 auto;
}

.value-card {
    padding: var(--spacing-2xl);
    text-align: center;
    background: var(--surface);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-2xl);
    transition: all var(--transition-normal) var(--easing-standard);
    opacity: 0;
    transform: translateY(50px);
}

.value-card.in-view {
    opacity: 1;
    transform: translateY(0);
}

.value-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}

.value-icon {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-2xl);
    background: var(--primary-100);
    color: var(--primary-600);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--spacing-lg);
}

.value-title {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
}

.value-description {
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0;
}

/* Team Section */
.team-section {
    padding: var(--spacing-4xl) 0;
}

.team-grid {
    margin-bottom: var(--spacing-2xl);
}

.team-member-card {
    padding: var(--spacing-2xl);
    text-align: center;
    transition: all var(--transition-normal) var(--easing-standard);
    opacity: 0;
    transform: translateY(50px);
}

.team-member-card.in-view {
    opacity: 1;
    transform: translateY(0);
}

.team-member-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}

.member-photo {
    margin-bottom: var(--spacing-lg);
}

.photo-placeholder {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: var(--primary-100);
    color: var(--primary-600);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
}

.member-name {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xs);
}

.member-role {
    color: var(--primary-600);
    font-weight: 600;
    margin: 0 0 var(--spacing-md);
}

.member-bio {
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0 0 var(--spacing-lg);
}

.member-social {
    display: flex;
    gap: var(--spacing-sm);
    justify-content: center;
}

.social-link {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--gray-100);
    color: var(--gray-600);
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    transition: all var(--transition-fast) var(--easing-standard);
}

.social-link:hover {
    background: var(--primary-500);
    color: white;
    text-decoration: none;
}

.team-cta {
    background: var(--primary-50);
    border: 1px solid var(--primary-200);
    border-radius: var(--radius-2xl);
    padding: var(--spacing-2xl);
    text-align: center;
}

.team-cta h3 {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
}

.team-cta p {
    color: var(--gray-600);
    margin: 0 0 var(--spacing-lg);
}

/* Timeline */
.company-timeline {
    padding: var(--spacing-4xl) 0;
    background: var(--gray-50);
}

.timeline {
    position: relative;
    max-width: 800px;
    margin: 0 auto;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 30px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--primary-200);
}

.timeline-item {
    position: relative;
    padding-left: 80px;
    margin-bottom: var(--spacing-2xl);
    opacity: 0;
    transform: translateX(-50px);
    transition: all var(--transition-normal) var(--easing-standard);
}

.timeline-item.animate-in {
    opacity: 1;
    transform: translateX(0);
}

.timeline-item:last-child {
    margin-bottom: 0;
}

.timeline-marker {
    position: absolute;
    left: 0;
    top: 0;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--primary-500);
    border: 4px solid var(--surface);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-lg);
}

.timeline-marker.current {
    background: var(--secondary-500);
    box-shadow: 0 0 0 4px var(--secondary-200);
}

.marker-content {
    color: white;
    font-weight: 700;
    font-size: var(--text-sm);
}

.timeline-content {
    padding: var(--spacing-xl);
}

.timeline-content.current {
    border: 2px solid var(--secondary-500);
    box-shadow: 0 0 0 4px var(--secondary-100);
}

.timeline-title {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
}

.timeline-description {
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0;
}

/* Awards Section */
.awards-section {
    padding: var(--spacing-4xl) 0;
}

.award-card {
    padding: var(--spacing-2xl);
    text-align: center;
    transition: all var(--transition-normal) var(--easing-standard);
}

.award-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.award-icon {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-2xl);
    background: var(--warning-light);
    color: var(--warning);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--spacing-lg);
}

.award-title {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xs);
}

.award-year {
    color: var(--primary-600);
    font-weight: 600;
    margin: 0 0 var(--spacing-sm);
}

.award-description {
    color: var(--gray-600);
    margin: 0;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .hero-stats {
        justify-content: center;
    }
    
    .mission-vision-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-xl);
    }
    
    .values-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .team-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-xl);
    }
    
    .awards-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .hero-title {
        font-size: 2rem;
    }
    
    .hero-stats {
        flex-direction: column;
        gap: var(--spacing-lg);
    }
    
    .values-grid,
    .awards-grid {
        grid-template-columns: 1fr;
    }
    
    .floating-element {
        position: static;
        margin-bottom: var(--spacing-md);
    }
    
    .timeline::before {
        left: 15px;
    }
    
    .timeline-item {
        padding-left: 50px;
    }
    
    .timeline-marker {
        width: 30px;
        height: 30px;
        left: 0;
    }
    
    .marker-content {
        font-size: var(--text-xs);
    }
}

/* Animation Classes */
.animate-fade-up {
    opacity: 0;
    transform: translateY(30px);
    transition: all var(--transition-slow) var(--easing-standard);
}

.animate-fade-up.in-view {
    opacity: 1;
    transform: translateY(0);
}

.animate-scale-in {
    opacity: 0;
    transform: scale(0.9);
    transition: all var(--transition-normal) var(--easing-standard);
}

.animate-scale-in.in-view {
    opacity: 1;
    transform: scale(1);
}

/* Dark Mode */
[data-theme="dark"] .hero-title,
[data-theme="dark"] .section-title,
[data-theme="dark"] .card-title,
[data-theme="dark"] .value-title,
[data-theme="dark"] .member-name,
[data-theme="dark"] .timeline-title,
[data-theme="dark"] .award-title {
    color: var(--gray-100);
}

[data-theme="dark"] .hero-description,
[data-theme="dark"] .section-description,
[data-theme="dark"] .card-description,
[data-theme="dark"] .value-description,
[data-theme="dark"] .member-bio,
[data-theme="dark"] .timeline-description,
[data-theme="dark"] .award-description {
    color: var(--gray-300);
}

[data-theme="dark"] .company-values,
[data-theme="dark"] .company-timeline {
    background: var(--gray-850);
}

[data-theme="dark"] .value-card,
[data-theme="dark"] .team-member-card,
[data-theme="dark"] .timeline-content,
[data-theme="dark"] .award-card {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .value-icon,
[data-theme="dark"] .photo-placeholder {
    background: var(--gray-700);
    color: var(--primary-400);
}

[data-theme="dark"] .timeline::before {
    background: var(--gray-700);
}

[data-theme="dark"] .team-cta {
    background: var(--gray-800);
    border-color: var(--gray-700);
}
</style>

<?php get_footer(); ?>