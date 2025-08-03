    <footer id="colophon" class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Stock Scanner</h3>
                    <p>Real-time stock data and market news powered by Django API.</p>
                </div>
                
                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="<?php echo home_url('/'); ?>">Home</a></li>
                        <li><a href="<?php echo home_url('/stocks/'); ?>">Stocks</a></li>
                        <li><a href="<?php echo home_url('/news/'); ?>">News</a></li>
                        <li><a href="<?php echo home_url('/alerts/'); ?>">Alerts</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h3>Market Data</h3>
                    <div class="market-summary">
                        <div class="market-item">
                            <span class="label">S&P 500:</span>
                            <span class="value" id="sp500-value">Loading...</span>
                        </div>
                        <div class="market-item">
                            <span class="label">NASDAQ:</span>
                            <span class="value" id="nasdaq-value">Loading...</span>
                        </div>
                        <div class="market-item">
                            <span class="label">DOW:</span>
                            <span class="value" id="dow-value">Loading...</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="site-info">
                <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.</p>
            </div>
        </div>
    </footer>
</div><!-- #page -->

<?php wp_footer(); ?>

</body>
</html>