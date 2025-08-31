<?php
/**
 * Template Name: Dashboard Page
 * Modern dashboard with enhanced design
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <div class="fade-in">
    <!-- Dashboard Header -->
    <section class="mb-8">
      <div class="flex-between mb-6">
        <div>
          <h1 class="mb-2"><?php esc_html_e('Trading Dashboard', 'retail-trade-scanner'); ?></h1>
          <p class="text-muted"><?php esc_html_e('Monitor your investments and market performance', 'retail-trade-scanner'); ?></p>
        </div>
        <div class="flex gap-4">
          <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="btn btn-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="21 21l-4.35-4.35"></path>
            </svg>
            <?php esc_html_e('Scan Stocks', 'retail-trade-scanner'); ?>
          </a>
        </div>
      </div>
    </section>

    <!-- Key Metrics Grid -->
    <section class="grid grid-4 mb-8">
      <div class="card p-6">
        <div class="flex-between mb-4">
          <h3 class="text-lg"><?php esc_html_e('Portfolio Value', 'retail-trade-scanner'); ?></h3>
          <div style="color: var(--accent);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
        </div>
        <div class="text-3xl font-bold mb-2" style="color: var(--foreground);">$127,845.32</div>
        <div class="text-sm flex items-center gap-2">
          <span style="color: #22c55e;">+2.4%</span>
          <span class="text-muted"><?php esc_html_e('Today', 'retail-trade-scanner'); ?></span>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex-between mb-4">
          <h3 class="text-lg"><?php esc_html_e('Total Return', 'retail-trade-scanner'); ?></h3>
          <div style="color: var(--primary);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
            </svg>
          </div>
        </div>
        <div class="text-3xl font-bold mb-2" style="color: var(--foreground);">+$27,845</div>
        <div class="text-sm flex items-center gap-2">
          <span style="color: #22c55e;">+27.8%</span>
          <span class="text-muted"><?php esc_html_e('All Time', 'retail-trade-scanner'); ?></span>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex-between mb-4">
          <h3 class="text-lg"><?php esc_html_e('Active Positions', 'retail-trade-scanner'); ?></h3>
          <div style="color: var(--accent);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </div>
        </div>
        <div class="text-3xl font-bold mb-2" style="color: var(--foreground);">24</div>
        <div class="text-sm text-muted"><?php esc_html_e('Across 8 sectors', 'retail-trade-scanner'); ?></div>
      </div>

      <div class="card p-6">
        <div class="flex-between mb-4">
          <h3 class="text-lg"><?php esc_html_e('Watchlist Items', 'retail-trade-scanner'); ?></h3>
          <div style="color: var(--primary);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon>
            </svg>
          </div>
        </div>
        <div class="text-3xl font-bold mb-2" style="color: var(--foreground);">156</div>
        <div class="text-sm text-muted"><?php esc_html_e('Stocks monitored', 'retail-trade-scanner'); ?></div>
      </div>
    </section>

    <!-- Charts and Analysis Section -->
    <section class="grid grid-2 mb-8">
      <div class="card p-6">
        <h3 class="mb-4"><?php esc_html_e('Portfolio Performance', 'retail-trade-scanner'); ?></h3>
        <div class="text-center p-8" style="background: var(--muted); border-radius: var(--radius); min-height: 200px; display: flex; align-items: center; justify-content: center;">
          <div class="text-muted">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 16px;">
              <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
            </svg>
            <p><?php esc_html_e('Portfolio chart will be displayed here', 'retail-trade-scanner'); ?></p>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <h3 class="mb-4"><?php esc_html_e('Market Overview', 'retail-trade-scanner'); ?></h3>
        <div class="space-y-4">
          <div class="flex-between p-3" style="background: var(--muted); border-radius: var(--radius);">
            <div>
              <div class="font-semibold">S&P 500</div>
              <div class="text-sm text-muted">SPX</div>
            </div>
            <div class="text-right">
              <div class="font-semibold">4,192.63</div>
              <div class="text-sm" style="color: #22c55e;">+1.2%</div>
            </div>
          </div>
          
          <div class="flex-between p-3" style="background: var(--muted); border-radius: var(--radius);">
            <div>
              <div class="font-semibold">NASDAQ</div>
              <div class="text-sm text-muted">IXIC</div>
            </div>
            <div class="text-right">
              <div class="font-semibold">12,932.73</div>
              <div class="text-sm" style="color: #ef4444;">-0.8%</div>
            </div>
          </div>
          
          <div class="flex-between p-3" style="background: var(--muted); border-radius: var(--radius);">
            <div>
              <div class="font-semibold">Dow Jones</div>
              <div class="text-sm text-muted">DJI</div>
            </div>
            <div class="text-right">
              <div class="font-semibold">33,745.40</div>
              <div class="text-sm" style="color: #22c55e;">+0.3%</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent Activity -->
    <section class="card p-6">
      <div class="flex-between mb-6">
        <h3><?php esc_html_e('Recent Activity', 'retail-trade-scanner'); ?></h3>
        <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="text-primary hover:text-primary-hover font-medium text-sm">
          <?php esc_html_e('View All', 'retail-trade-scanner'); ?>
        </a>
      </div>
      
      <div class="space-y-4">
        <div class="flex items-center gap-4 p-4" style="background: var(--muted); border-radius: var(--radius); border-left: 3px solid var(--accent);">
          <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: var(--accent);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </div>
          <div class="flex-1">
            <div class="font-semibold"><?php esc_html_e('Bought 50 shares of AAPL', 'retail-trade-scanner'); ?></div>
            <div class="text-sm text-muted"><?php esc_html_e('2 hours ago at $175.32', 'retail-trade-scanner'); ?></div>
          </div>
          <div class="text-right">
            <div class="font-semibold">$8,766.00</div>
          </div>
        </div>
        
        <div class="flex items-center gap-4 p-4" style="background: var(--muted); border-radius: var(--radius); border-left: 3px solid var(--primary);">
          <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: var(--primary);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
          </div>
          <div class="flex-1">
            <div class="font-semibold"><?php esc_html_e('Price alert triggered for TSLA', 'retail-trade-scanner'); ?></div>
            <div class="text-sm text-muted"><?php esc_html_e('4 hours ago - Target price $250.00 reached', 'retail-trade-scanner'); ?></div>
          </div>
        </div>
        
        <div class="flex items-center gap-4 p-4" style="background: var(--muted); border-radius: var(--radius); border-left: 3px solid #22c55e;">
          <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: #22c55e;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
          <div class="flex-1">
            <div class="font-semibold"><?php esc_html_e('Sold 100 shares of MSFT', 'retail-trade-scanner'); ?></div>
            <div class="text-sm text-muted"><?php esc_html_e('Yesterday at $378.85 (+12.4% gain)', 'retail-trade-scanner'); ?></div>
          </div>
          <div class="text-right">
            <div class="font-semibold" style="color: #22c55e;">+$4,692.50</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</main>

<style>
.space-y-4 > * + * {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .flex-between {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .grid-4 {
    grid-template-columns: 1fr;
  }
  
  .grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>

<?php get_footer(); ?>