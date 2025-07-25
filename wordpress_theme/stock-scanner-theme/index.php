<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php wp_title('|', true, 'right'); bloginfo('name'); ?></title>
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
    <?php wp_body_open(); ?>
    
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <a href="<?php echo home_url(); ?>" class="site-title">
                    📈 <?php bloginfo('name'); ?>
                </a>
                
                <nav class="main-nav">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_class' => 'main-menu',
                        'fallback_cb' => 'stock_scanner_fallback_menu'
                    ));
                    ?>
                </nav>
                
                <div class="user-menu">
                    <?php if (is_user_logged_in()): ?>
                        <?php
                        $user_level = 0;
                        if (function_exists('pmpro_getMembershipLevelForUser')) {
                            $level = pmpro_getMembershipLevelForUser(get_current_user_id());
                            $user_level = $level ? $level->id : 0;
                        }
                        
                        $level_names = array(0 => 'Free', 1 => 'Basic', 2 => 'Pro', 3 => 'Enterprise');
$level_classes = array(0 => '', 1 => 'basic', 2 => 'pro', 3 => 'enterprise');
                        ?>
                        
                        <span class="membership-badge <?php echo $level_classes[$user_level]; ?>">
                            <?php echo $level_names[$user_level]; ?>
                        </span>
                        
                        <a href="<?php echo wp_logout_url(home_url()); ?>">Logout</a>
                    <?php else: ?>
                        <a href="<?php echo wp_login_url(); ?>">Login</a>
                        <a href="<?php echo wp_registration_url(); ?>">Sign Up</a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </header>

    <main class="site-main">
        <div class="container">
            <?php if (have_posts()): ?>
                <?php while (have_posts()): the_post(); ?>
                    <article <?php post_class(); ?>>
                        <div class="page-header">
                            <h1 class="page-title"><?php the_title(); ?></h1>
                            <?php if (get_the_excerpt()): ?>
                                <p class="page-description"><?php the_excerpt(); ?></p>
                            <?php endif; ?>
                        </div>
                        
                        <div class="page-content">
                            <?php the_content(); ?>
                        </div>
                    </article>
                <?php endwhile; ?>
            <?php else: ?>
                <div class="page-header">
                    <h1 class="page-title">Welcome to Stock Scanner</h1>
                    <p class="page-description">
                        Get real-time stock data, charts, and alerts. Track your favorite stocks with our powerful dashboard.
                    </p>
                </div>
                
                <div class="stock-grid">
                    <div class="stock-row">
                        <h3>🔥 Popular Stocks</h3>
                        <?php echo do_shortcode('[stock_scanner symbol="AAPL" show_chart="true" show_details="true"]'); ?>
                        <?php echo do_shortcode('[stock_scanner symbol="TSLA" show_chart="true" show_details="true"]'); ?>
                        <?php echo do_shortcode('[stock_scanner symbol="NVDA" show_chart="true" show_details="true"]'); ?>
                    </div>
                    
                    <div class="stock-row">
                        <h3>📊 Market Indices</h3>
                        <?php echo do_shortcode('[stock_scanner symbol="SPY" show_chart="true" show_details="true"]'); ?>
                        <?php echo do_shortcode('[stock_scanner symbol="QQQ" show_chart="true" show_details="true"]'); ?>
                        <?php echo do_shortcode('[stock_scanner symbol="DIA" show_chart="true" show_details="true"]'); ?>
                    </div>
                </div>
                
                <div class="upgrade-notice">
                    <h4>🚀 Ready to track more stocks?</h4>
                    <p>Upgrade to Pro for 5,000 API calls per day or Enterprise for 20,000 API calls per day!</p>
                    <a href="/membership-plans/" class="button-premium">View Plans</a>
                </div>
            <?php endif; ?>
        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>Stock Scanner</h4>
                    <ul>
                        <li><a href="/about/">About</a></li>
                        <li><a href="/contact/">Contact</a></li>
                        <li><a href="/stock-dashboard/">Dashboard</a></li>
                        <li><a href="/stock-watchlist/">Watchlist</a></li>
                        <li><a href="/stock-market-news/">Market News</a></li>
                        <li><a href="/stock-alerts/">Alerts</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h4>Membership</h4>
                    <ul>
                        <li><a href="/membership-plans/">Pricing Plans</a></li>
                        <li><a href="/membership-account/">My Account</a></li>
                        <li><a href="/membership-account/membership-checkout/">Upgrade</a></li>
                        <li><a href="/membership-account/membership-cancel/">Cancel</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h4>Support</h4>
                    <ul>
                        <li><a href="/contact/">Contact Us</a></li>
                        <li><a href="/help/">Help Center</a></li>
                        <li><a href="/api-docs/">API Documentation</a></li>
                        <li><a href="/privacy/">Privacy Policy</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h4>Connect</h4>
                    <ul>
                        <li><a href="#">Twitter</a></li>
                        <li><a href="#">LinkedIn</a></li>
                        <li><a href="#">GitHub</a></li>
                        <li><a href="#">Discord</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved. | Real-time stock data powered by yfinance</p>
            </div>
        </div>
    </footer>

    <?php wp_footer(); ?>
</body>
</html>